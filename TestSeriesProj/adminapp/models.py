from django.contrib.auth.models import User
from django.db import models
import pdb
from datetime import datetime

# Create your models here.

ROW_STATUS = (
    (True, 'ACTIVE'),
    (False, 'INACTIVE')
)

SUB_STATUS = (
    ('ACTIVE', 'ACTIVE'),
    ('INACTIVE', 'INACTIVE')
)

UPLOAD_NOTICE_IMAGE = 'media/'


class State(models.Model):
    state = models.CharField(max_length=255)
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(blank=True,null=True)
    created_by = models.CharField(max_length=255, null=True,blank=True)
    updated_by = models.CharField(max_length=255, null=True,blank=True)

    def __unicode__(self):
        return self.state


class City(models.Model):
    city = models.CharField(max_length=255)
    state = models.ForeignKey(State, related_name='Category')
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(blank=True,null=True)
    created_by = models.CharField(max_length=255, null=True,blank=True)
    updated_by = models.CharField(max_length=255, null=True,blank=True)

    def __unicode__(self):
        return self.city


class Category(models.Model):
    category = models.CharField(max_length=255)
    banner_img = models.ImageField(upload_to='banner_img',blank=True,null=True)
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(blank=True,null=True)
    created_by = models.CharField(max_length=255, null=True,blank=True)
    updated_by = models.CharField(max_length=255, null=True,blank=True)

    def __unicode__(self):
        return self.category


class SubCategory(models.Model):
    subCategory = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='Category')
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(blank=True,null=True)
    created_by = models.CharField(max_length=255, null=True,blank=True)
    updated_by = models.CharField(max_length=255, null=True,blank=True)

    def __unicode__(self):
        return self.subCategory


class Section(models.Model):
    section = models.CharField(max_length=255)
    subCategory = models.ForeignKey(SubCategory, related_name='SubCategory')
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(blank=True,null=True)
    created_by = models.CharField(max_length=255, null=True,blank=True)
    updated_by = models.CharField(max_length=255, null=True,blank=True)

    def __unicode__(self):
        return self.section


class UserRole(models.Model):
    role = models.CharField(max_length=50)
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(blank=True,null=True)
    created_by = models.CharField(max_length=255, null=True,blank=True)
    updated_by = models.CharField(max_length=255, null=True,blank=True)

    def __unicode__(self):
        return self.role


class UserProfile(User):
    state = models.ForeignKey(State, related_name='user_state')
    city = models.ForeignKey(City, related_name='user_city')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255,null=True,blank=True)
    pin_code = models.CharField(max_length=255,null=True,blank=True)
    user_type = models.ForeignKey(UserRole, related_name='user_role')
    user_status = models.CharField(max_length=255, choices=SUB_STATUS, default='Active')
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(blank=True,null=True)
    created_by = models.CharField(max_length=255, null=True,blank=True)
    updated_by = models.CharField(max_length=255, null=True,blank=True)

    def __unicode__(self):
        return self.username


class Teacher():
    teacher = models.ForeignKey(UserProfile, related_name='teacher')
    bank= models.CharField(max_length=255)
    bank_acct_no= models.CharField(max_length=255,null=True,blank=True)
    ifsc_no= models.CharField(max_length=255,null=True,blank=True)
    branch_name= models.CharField(max_length=255,null=True,blank=True)
    pan_no= models.CharField(max_length=255,null=True,blank=True)
    tin_no= models.CharField(max_length=255,null=True,blank=True)
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(blank=True,null=True)
    created_by = models.CharField(max_length=255, null=True,blank=True)
    updated_by = models.CharField(max_length=255, null=True,blank=True)

    def __unicode__(self):
        return self.teacher


class Student():
    student = models.ForeignKey(UserProfile, related_name='student')
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(blank=True,null=True)
    created_by = models.CharField(max_length=255, null=True,blank=True)
    updated_by = models.CharField(max_length=255, null=True,blank=True)

    def __unicode__(self):
        return self.student