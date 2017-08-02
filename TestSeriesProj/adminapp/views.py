from django.shortcuts import render

# Create your views here.

from urlparse import urlparse

from django.shortcuts import render


def index(request):
    data={}
    return render(request, 'base.html', data)

def teacher(request):
    data={}
    return render(request, 'teacher/teacherTable.html', data)

def open_teacher(request):
    data={}
    return render(request, 'teacher/createTeacher.html', data)

