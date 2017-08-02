from django.shortcuts import render

# Create your views here.

def teacher(request):
    data={}
    return render(request, 'teacher/teacherTable.html', data)