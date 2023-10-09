# Create your views here.
from django.shortcuts import render
from django.http import Http404, HttpResponse
from .models import Employee

def home(request):
    employees = Employee.objects.all()
    context = {
        'employees': employees,
    }
    return render(request,'home.html', context)


def employee_detail(request,id):
    try:
        employee = Employee.objects.get(id=id)
        # print(employee)
    except employee.DoesNotExist:
        raise Http404('Employee not found')
    #HttpResponse(employee)
    return render(request,'employee_detail.html',{'employee':employee,})