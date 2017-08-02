from django.shortcuts import render

# Create your views here.

def index(request):
    data={}
    return render(request, 'exam/examTable.html', data)

def open(request):
    data={}
    return render(request, 'exam/createExam.html', data)
