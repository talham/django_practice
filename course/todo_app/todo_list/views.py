from django.shortcuts import render, redirect, get_object_or_404
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

def mark_as_Done(request,id):
    task = get_object_or_404(todo_list,id=id)
    task.status = True
    task.save()
    return redirect('home')

def UndoCompleteTask(request,id):
    task = get_object_or_404(todo_list,id=id)
    task.status = False
    task.save()
    return redirect('home')

def editTask(request,id):
    """Edit task descriptions and due dates"""
    edittask = get_object_or_404(todo_list,id=id)
    if request.method == 'POST':
        new_task = request.POST['edittask']
        edittask.task = new_task
        edittask.save()
        return redirect('home')
    else:
        context = {'edit_task':edittask,}   
        return render(request,'edit_task.html',context)

def deleteTask(request,id):
    """Delete an existing task"""
    task = get_object_or_404(todo_list,id=id)
    task.delete()
    return redirect('home')

