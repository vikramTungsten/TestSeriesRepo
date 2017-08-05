import json
from django.core.validators import validate_email
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
    renderer_classes,
    parser_classes,
)
from datetime import datetime
from datetime import timedelta
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import parser_classes
from push_notifications.models import GCMDevice
from mrbdapp.serializers import (LoginSerializer, ConsumerDetailsSerializer, MeterImageSerializer,
                                 MeterReadingSerializer, UserProfileSerializer)
from mrbdapp.helper import UserProfileToJSON, JobCardToJSON, paginate
from adminapp.models import UserProfile
from dispatch.models import JobCard, RouteAssignment
from consumerapp.models import ConsumerDetails
from .models import MeterImage, SuspiciousActivityImage, UserProfileImage, QrTemperedImage
from meterreaderapp.models import DeviceDetail
from django.db.models import Q
from .tasks import aysnc_update_jc_status, aysnc_update_rd_jc_status, aysnc_create_image_for_upload, \
    aysnc_create_image_for_unbilled, get_image_file

'''
    # Static error status variables
'''
username_password_missmatch = {
    "error_code": "101",
    "message": "Login failed. Username Password combination doesn't match."
}

account_not_activated = {
    "error_code": "102",
    "message": "Login failed. Account not ACTIVE."
}

invalid_imei_number = {
    "error_code": "103",
    "message": "Login failed. Invalid IMEI Number."
}

MAX_SIZE = 1 * 1024 * 1024  # 1MB

JC_TO_UPDATE_ON_GET = []
RD_JC_TO_UPDATE_ON_GET = []

# Create your views here.

'''
    # A test function to test API calls.
'''


@csrf_exempt
@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def index(request):
    return Response({"message": "MRBD_App"})


'''
    # REST API to LogIn to the App.
    # Input : email and password of the valid user.
    # Output : Auth token on successful login or error or failure.
'''


@csrf_exempt
@api_view(['POST'])
@renderer_classes((JSONRenderer,))
def login(request):
    print '============================', request.data
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        try:
            validate_email(serializer.validated_data['username'])
            user = authenticate(username=serializer.validated_data['username'],
                                password=serializer.validated_data['password'])
        except Exception:
            try:
                userprofile = UserProfile.objects.get(employee_id=serializer.validated_data['username'])
                user = authenticate(username=userprofile.email, password=serializer.validated_data['password'])
            except Exception:
                user = None

        if user is not None:

            user_profile = user.userprofile
            print user_profile, user_profile.status

            if (user_profile.status == 'ACTIVE'):

                devicedetail_obj = DeviceDetail.objects.filter(user_id=user.userprofile.id,
                                                               imei_no=serializer.validated_data['imei_no'])
                print 'device object', devicedetail_obj

                if len(devicedetail_obj) > 0:

                    user_info = UserProfileToJSON(user_profile, devicedetail_obj[0])
                    print '=============>', user_info
                    #                    try:


                    Token.objects.filter(user=user).delete()
                    token = Token.objects.create(user=user)
                    print 'token no==>', token

                    return Response({
                        "result": "success",
                        "message": "LogIn Successful.",
                        "responsedata": user_info,
                        "authorization": "Token " + str(token)
                    }, status=status.HTTP_200_OK)

                else:
                    return Response({
                        "result": "failure",
                        "responsedata": invalid_imei_number
                    }, status=status.HTTP_403_FORBIDDEN)

            else:
                return Response({
                    "result": "failure",
                    "responsedata": account_not_activated
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({
                "result": "failure",
                "responsedata": username_password_missmatch
            }, status=status.HTTP_403_FORBIDDEN)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'''
    # REST API to LogOut from the App.
    # Input : Auth token.
    # Output : Success message on successful logout or error or failure.
'''


@csrf_exempt
@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def logout(request):
    print "In logout"
    user = request.user
    print user.id
    Token.objects.filter(user=user).delete()
    return Response({
        "result": "success",
        "message": "LogOut Successful."
    }, status=status.HTTP_200_OK)


'''
    # REST API to get all allocated job cards.
    # Input : Auth Token.
    # Output : Pagewise Job Cards details. 1000 records per page.
'''


@csrf_exempt
@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_job_cards(request):
    try:
        started_datetime = datetime.utcnow()
        print "Job Card Pull started"

        user = request.user.userprofile

        print "Job Card Pull started by===>", user
        routeAssignment = RouteAssignment.objects.filter(meterreader=user, record_status='Active',
                                                         dispatch_status='Inprogress')
        if routeAssignment.exists():
            print "Allocation is in progress"
            return Response({
                "result": "success",
                "error_code": "201",
                "message": "Allocation is in progress",
            }, status=status.HTTP_200_OK)

        print "Job Card Pull started by===>", user

        # page_number = int(request.GET.get('page'))
        page_number = 1
        dict = {}
        dict["is_next"] = False

        if page_number == 1:
            del JC_TO_UPDATE_ON_GET[:]

        jobcards = JobCard.objects.filter(meterreader=user, record_status='ALLOCATED', is_active=True, is_deleted=False,
                                          is_deleted_for_mr=False)

        if (len(jobcards) > 0):
            jobcards_list = []

            dict["total_job_cards_count"] = len(jobcards)

            print "Total Job cards" + str(len(jobcards))

            page, jobcards = paginate(jobcards, page_number)

            for jobcard in jobcards:
                JC_TO_UPDATE_ON_GET.append(jobcard.id)
                jobcards_list.append(JobCardToJSON(jobcard))
                jobcard.save()

            dict["jobcards"] = jobcards_list
            dict["page_job_cards_count"] = len(jobcards_list)

            if (int(page.paginator.count) >= (int(page_number) * 1000)):
                dict["is_next"] = True

            # if (dict['is_next'] == False):
            aysnc_update_jc_status.delay(JC_TO_UPDATE_ON_GET)

            end_datetime = datetime.utcnow()
            e = end_datetime - started_datetime

            print 'total_time_taken', str(e.total_seconds())
            print "Processed : " + str(len(JC_TO_UPDATE_ON_GET))

            return Response({
                "result": "success",
                "message": "GetJobCards Successful.",
                "responsedata": dict,
            }, status=status.HTTP_200_OK)
        else:
            print "No allocated jobcards found."
            return Response({
                "result": "success",
                "message": "No allocated jobcards found.",
                "responsedata": dict
            }, status=status.HTTP_200_OK)
    except Exception, e:
        print 'Exception|get_job_cards|', e


# old function-- 10/02/17





@csrf_exempt
@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_job_cards__01(request):
    started_datetime = datetime.utcnow()

    print "Job Card Pull started"

    user = request.user.userprofile

    page_number = int(request.GET.get('page'))

    dict = {}
    dict["is_next"] = False

    if page_number == 1:
        del JC_TO_UPDATE_ON_GET[:]

    jobcards = JobCard.objects.filter(meterreader=user, record_status='ALLOCATED', is_active=True, is_deleted=False,
                                      is_deleted_for_mr=False)

    if (len(jobcards) > 0):
        jobcards_list = []

        dict["total_job_cards_count"] = len(jobcards)

        print "Total Job cards" + str(len(jobcards))

        page, jobcards = paginate(jobcards, page_number)

        for jobcard in jobcards:
            JC_TO_UPDATE_ON_GET.append(jobcard.id)
            jobcards_list.append(JobCardToJSON(jobcard))
            jobcard.save()

        dict["jobcards"] = jobcards_list
        dict["page_job_cards_count"] = len(jobcards_list)

        # if (int(page.paginator.count) >= (int(page_number)*100)):
        #     dict["is_next"] = True

        # if (dict['is_next'] == False):
        aysnc_update_jc_status.delay(JC_TO_UPDATE_ON_GET)

        end_datetime = datetime.utcnow()
        e = end_datetime - started_datetime

        print 'total_time_taken', str(e.total_seconds())
        print "Processed : " + str(len(JC_TO_UPDATE_ON_GET))

        return Response({
            "result": "success",
            "message": "GetJobCards Successful.",
            "responsedata": dict,
        }, status=status.HTTP_200_OK)
    else:
        print "No allocated jobcards found."
        return Response({
            "result": "success",
            "message": "No allocated jobcards found.",
            "responsedata": dict
        }, status=status.HTTP_200_OK)


'''
    # REST API to get all reassigned and deassigned job cards.
    # Input : Auth Token.
    # Output : Pagewise Job Cards details. 100 records per page.
'''


@csrf_exempt
@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def get_deassigned_reassigned_job_cards(request):
    started_datetime = datetime.utcnow()

    print "Deassigned Reassigned Job Card Pull started"

    user = request.user.userprofile

    # routeAssignment=RouteAssignment.objects.filter(meterreader=user,record_status='Active',dispatch_status='Inprogress')
    #
    # if routeAssignment.exists():
    #     print "Allocation is in progress"
    #     return Response({
    #         "result":"success",
    #         "error_code":"201",
    #         "message": "Allocation is in progress",
    #         },status=status.HTTP_200_OK)


    # page_number = int(request.GET.get('page'))
    page_number = 1

    dict = {}
    dict["is_next"] = False

    if page_number == 1:
        del RD_JC_TO_UPDATE_ON_GET[:]

    jobcards = JobCard.objects.filter((Q(record_status='REASSIGNED') | Q(record_status='DEASSIGNED')), meterreader=user,
                                      is_deleted_for_mr=False)

    jobcards_list = []

    dict["total_job_cards_count"] = len(jobcards)

    print "Total Deassigned Reassigned Job cards : " + str(len(jobcards))

    if (len(jobcards) > 0):
        page, jobcards = paginate(jobcards, page_number)

        for jobcard in jobcards:
            jobcards_list.append(jobcard.id)
            RD_JC_TO_UPDATE_ON_GET.append(jobcard.id)

        dict["re_de_assigned_jobcards"] = jobcards_list
        dict["page_job_cards_count"] = len(jobcards_list)

        if (int(page.paginator.count) >= (int(page_number) * 1000)):
            dict["is_next"] = True

        # if (dict["is_next"] == False):
        aysnc_update_rd_jc_status.delay(RD_JC_TO_UPDATE_ON_GET)

        end_datetime = datetime.utcnow()
        e = end_datetime - started_datetime

        print 'total_time_taken for deassigned reassigned : ', str(e.total_seconds())
        print "Deassigned Reassigned Processed : " + str(len(RD_JC_TO_UPDATE_ON_GET))

        return Response({
            "result": "success",
            "message": "Get ReassignedDeassigned JobCards Successful.",
            "responsedata": dict,
        }, status=status.HTTP_200_OK)
    else:
        print "No deassigned or reassigned records found."
        return Response({
            "result": "success",
            "message": "No deassigned or reassigned records found.",
            "responsedata": dict
        }, status=status.HTTP_200_OK)


'''
    # REST API to add new consumer.
    # Input : Auth Token. Unbilled consumer details JSON array.
    # Output : Auth token if Consumer created successfully or error on failure.
'''


@csrf_exempt
@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def add_new_consumer(request):
    user = request.user.userprofile

    started_datetime = datetime.utcnow()

    print "Uploading unbilled consumers started"

    data = request.data["unbilled_consumers"]

    dict = {}

    if (len(data) > 0):

        dict['new_unbilled_consumers'] = []
        dict['serializer_error_cids'] = []
        dict['image_missing_cids'] = []
        dict['create_error_cids'] = []

        imageDataDict = {}

        for d in data:

            meter_image = d.get("meter_image")

            if (meter_image is not None and meter_image["image"] != ""):

                suspicious_activity_image = d.get("suspicious_activity_image")

                qr_tempered_image = d.get("qr_tempered_image")

                serializer = ConsumerDetailsSerializer(data=d)

                if serializer.is_valid():

                    consumerdetails_obj = serializer.create_unbilled_customer(d, user)

                    if consumerdetails_obj is not None:

                        print "Consumer Added"
                        dict['new_unbilled_consumers'].append(consumerdetails_obj.id)

                        imageDataDict[consumerdetails_obj.id] = {}

                        imageDataDict[consumerdetails_obj.id]['meter_image'] = json.dumps(meter_image)

                        if (suspicious_activity_image is not None and suspicious_activity_image["image"] != ""):
                            imageDataDict[consumerdetails_obj.id]['suspicious_activity_image'] = json.dumps(
                                suspicious_activity_image)

                        if (qr_tempered_image is not None and qr_tempered_image["image"] != ""):
                            imageDataDict[consumerdetails_obj.id]['qr_tempered_image'] = json.dumps(qr_tempered_image)

                    else:
                        print "Create record error"
                        dict['create_error_cids'].append("Create Error : " + str(d.get('consumer_no')))
                else:
                    print "Serializer error"
                    dict['serializer_error_cids'].append(
                        "Serializer error : " + str(d.get('consumer_no')) + " for " + str(serializer.errors))

            else:
                print "Image missing error"
                dict['image_missing_cids'].append("Image data missing error : " + str(d.get('consumer_no')))

        # Token.objects.filter(user=user).delete()
        # token = Token.objects.create(user=user)
        token = Token.objects.get(user=user)

        end_datetime = datetime.utcnow()
        e = end_datetime - started_datetime

        aysnc_create_image_for_unbilled.delay(imageDataDict)

        print "Total time taken for Unbilled Consumers: ", str(e.total_seconds())
        print "Processed : " + str(len(dict['new_unbilled_consumers']))

        return Response({
            "result": "success",
            "message": "Unbilled Customers created successfully.",
            "responsedata": dict,
            "authorization": "Token " + str(token)
        }, status=status.HTTP_200_OK)

    return Response({
        "result": "failure",
        "message": "Unbilled Consumers' data not provided.",
    }, status=status.HTTP_200_OK)


'''
    # REST API to add new consumer.
    # Input : Auth Token. Meter readings details JSON array.
    # Output : Auth token if Consumer created successfully or error on failure.
'''


@csrf_exempt
@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def upload_meter_reading(request):
    started_datetime = datetime.utcnow()
    user = request.user.userprofile

    print "Meter Reading upload started by =>", user

    data = request.data["readings"]
    dict = {}

    if (len(data) > 0):
        dict['new_meter_readings'] = []
        dict['serializer_error_jcs'] = []
        dict['image_missing_jcs'] = []
        dict['create_error_jcs'] = []

        imageDataDict = {}

        for d in data:
            meter_image = d.get("meter_image")

            if (meter_image is not None and meter_image["image"] != ""):

                suspicious_activity_image = d.get("suspicious_activity_image")
                qr_tempered_image = d.get("qr_tempered_image")

                serializer = MeterReadingSerializer(data=d)

                if serializer.is_valid():
                    meterrading_obj = serializer.create(d, user)
                    if meterrading_obj is not None:
                        print "Meter readings taken"
                        dict['new_meter_readings'].append(meterrading_obj.id)

                        imageDataDict[meterrading_obj.id] = {}
                        imageDataDict[meterrading_obj.id]['meter_image'] = json.dumps(meter_image)

                        if (suspicious_activity_image is not None and suspicious_activity_image["image"] != ""):
                            imageDataDict[meterrading_obj.id]['suspicious_activity_image'] = json.dumps(
                                suspicious_activity_image)

                        if (qr_tempered_image is not None and qr_tempered_image["image"] != ""):
                            imageDataDict[meterrading_obj.id]['qr_tempered_image'] = json.dumps(qr_tempered_image)

                            # aysnc_create_image_for_upload.delay(imageDataDict)
                    else:
                        print "Create receord error:CHECK SERIALIZERS"
                        dict['create_error_jcs'].append(d.get('job_card_id'))

                else:
                    print "Serializer error"
                    dict['serializer_error_jcs'].append(d.get('job_card_id'))

            else:
                print "Image data missing error"
                dict['image_missing_jcs'].append(d.get('job_card_id'))

        end_datetime = datetime.utcnow()
        e = end_datetime - started_datetime

        aysnc_create_image_for_upload.delay(imageDataDict)

        print "Total time taken for reading upload : ", str(e.total_seconds())
        print "Processed : " + str(len(dict['new_meter_readings']))

        # Token.objects.filter(user=user).delete()
        # token = Token.objects.create(user=user)
        token = Token.objects.get(user=user)

        return Response({
            "result": "success",
            "message": "Readings uploaded successfully.",
            "responsedata": dict,
            "authorization": "Token " + str(token)
        }, status=status.HTTP_200_OK)

    return Response({
        "result": "failure",
        "message": "Readings data not provided.",
    }, status=status.HTTP_200_OK)


'''
    # REST API to update the user profile.
    # Input : Auth Token. User details to update.
    # Output : Auth token if details updated successfully or error on failure.
'''


@csrf_exempt
@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def update_user_profile(request):
    user = request.user.userprofile

    profile_image = request.data.get("profile_image")
    profile_image_obj = None

    if (profile_image is not None and profile_image["image"] != ""):
        file = get_image_file(str(profile_image["image"]))

        profile_image_obj = UserProfileImage(profile_image=SimpleUploadedFile(
            profile_image["name"],
            file,
            getattr(profile_image, "content_type", "application/octet-stream")))

        profile_image_obj.save()

    serializer = UserProfileSerializer(data=request.data)

    if serializer.is_valid():
        userprofile_obj = serializer.update_profile(serializer.validated_data, user, profile_image_obj)
        if userprofile_obj is not None:

            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)

            return Response({
                "result": "success",
                "message": "User profile updated successfully.",
                "responsedata": UserProfileToJSON(userprofile_obj),
                "authorization": "Token " + str(token)
            }, status=status.HTTP_200_OK)
        else:
            print "Deleting images"
            if profile_image_obj is not None:
                profile_image_obj.delete()
    else:
        print "Deleting images"

        dict = {}

        for error in serializer.errors:
            dict[error] = serializer.errors[error][0]

        if profile_image_obj is not None:
            profile_image_obj.delete()
        return Response({'result': 'failure', 'message': 'Serializer Error', 'responsedata': dict},
                        status=status.HTTP_400_BAD_REQUEST)


'''
    # REST API to Register or Update device push token.
    # Input : Auth token. Push token of the validated device.
    # Output : Auth token on successful registration/update or error or failure.
'''


@csrf_exempt
@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def update_push_token(request):
    user = request.user

    request_json = request.data
    push_token = request_json['push_token']

    if user.gcmdevice_set.filter(user=user).exists():
        ds = GCMDevice.objects.get(user=user)
        print 'push notification', push_token
        ds.registration_id = push_token
        ds.save()
    else:
        if user.gcmdevice_set.filter(registration_id=push_token).exists():
            GCMDevice.objects.filter(user=user).delete()
        GCMDevice.objects.create(active=True, registration_id=push_token, user=user)

    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)

    return Response({
        "result": "success",
        "message": "Push token created/updated successfully.",
        "authorization": "Token " + str(token),
    }, status=status.HTTP_200_OK)


'''
    # REST API to Delete device push token.
    # Input : Auth token.
    # Output : Auth token on successful deletion or error or failure.
'''


@csrf_exempt
@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
def delete_push_token(request):
    user = request.user
    GCMDevice.objects.filter(user=user).delete()
    return Response({
        "result": "success",
        "message": "Push token deleted successfully."
    }, status=status.HTTP_200_OK)