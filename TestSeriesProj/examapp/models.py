from django.db import models
from adminapp.models import Section,Teacher


# Create your models here.

class Exam(models.Model):
    name = models.CharField(max_length=255,blank=False,null=False)
    section = models.ForeignKey(Section, related_name='section',blank=False,null=False)
    teacher = models.ForeignKey(Teacher, related_name='teacher',blank=False,null=False)
    total_time = models.CharField(max_length=255)
    total_quest = models.CharField(max_length=255)
    total_marks = models.CharField(max_length=255)
    passing_marks = models.CharField(max_length=255)
    sale_start_date = models.CharField(max_length=255)
    sale_end_date = models.CharField(max_length=255)
    exam_start_date = models.CharField(max_length=255)
    exam_end_date = models.CharField(max_length=255)
    result_date = models.CharField(max_length=255)
    sale_price = models.CharField(max_length=255)
    offer_price = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    short_desc = models.CharField(max_length=255)
    note = models.CharField(max_length=255)
    instruction_set = models.CharField(max_length=255)
    offer_available = models.BooleanField()
    record_status = models.BooleanField(choices=ROW_STATUS, default=True)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.name

class Question(models.Model):
    questions = models.TextField()
    ref_image = models.CharField(max_length=255)
    exam = models.ForeignKey(Exam, related_name='section',blank=False,null=False)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)

    def __unicode__(self):
        return self.questions