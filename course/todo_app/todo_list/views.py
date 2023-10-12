from django.shortcuts import render, redirect
from .models import todo_list
from django.http import HttpResponse

# Create your views here.
def home(request):
    tasks = todo_list.objects.filter(status=False)
    completed = todo_list.objects.filter(status=True)
    context = {'Tasks':tasks,'Completed':completed,}
    return render(request,'home.html',context)

def addTask(request):
    task = request.POST['task']
    todo_list.objects.create(task=task)
    return redirect('home')