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
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.state


class City(models.Model):
    city = models.CharField(max_length=255)
    state = models.ForeignKey(State, related_name='Category')
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.city


class Category(models.Model):
    category = models.CharField(max_length=255)
    banner_img = models.CharField(max_length=255)
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.category


class SubCategory(models.Model):
    subCategory = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='Category')
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.subCategory


class Section(models.Model):
    section = models.CharField(max_length=255)
    subCategory = models.ForeignKey(SubCategory, related_name='SubCategory')
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.section


class UserRole(models.Model):
    role = models.CharField(max_length=50)
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.role


class UserProfile(User):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contanct_no = models.CharField(max_length=15)
    email = models.CharField(max_length=255)
    user_type = models.ForeignKey(UserRole, related_name='user_role')
    user_status = models.CharField(max_length=255, choices=SUB_STATUS, default='Active')
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.emailId


class Teacher(User):
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.emailId


class Student(User):
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField(default=datetime.now)
    updated_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.emailId