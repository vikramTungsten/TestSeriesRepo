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
from adminapp.models import Category,SubCategory


#@csrf_exempt
@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def get_categories(request):
    try:
        dict['categories']=get_categories()
        return Response({
            "result": "success",
            "message": "get categories successfully.",
            "data": dict
        }, status=status.HTTP_200_OK)
    except Exception,ex:
        print 'Exception|studentapi|get_categories|',ex
        return Response({
            "result": "failure",
            "message": "error in getting categories.",
        }, status=status.HTTP_200_OK)
