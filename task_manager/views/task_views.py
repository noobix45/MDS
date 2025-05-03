# task_manager/task_views.py
from django.shortcuts import render, redirect, get_object_or_404
from task_manager.forms import TaskForm
from django.contrib import messages
from django.db import IntegrityError
from task_manager.models import UtilizatorTask,Utilizator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from task_manager.models import Task
from django.http import JsonResponse
from django.utils import timezone
import json

def create_task(request):

    referrer = request.META.get('HTTP_REFERER','')

    is_from_group = 'group' in referrer

    if request.method == 'POST': # trimit datele catre baza de date
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                task = form.save(commit=False)

                task.grup_task = is_from_group

                task.save() #salvez task
                utilizator = Utilizator.objects.get(user=request.user)
                UtilizatorTask.objects.create(id_utilizator=utilizator, id_task=task)
                messages.success(request, 'Taskul a fost creat cu succes!')
                return redirect('create_task')
            except IntegrityError as e:
                form.add_error(None, f"Eroare din baza de date: {str(e)}")
            except ObjectDoesNotExist:
                form.add_error(None,f"Utilizatorul logat nu exista in tabela Utilizator")
    else:
        form = TaskForm() # cer formularul ca sa il pot completa

    return render(request, 'create_task.html', {'form': form,'is_from_group': is_from_group})

@login_required
def delete_tasks(request):
    if request.method == 'POST':
        task_ids = request.POST.getlist('task_ids')
        Task.objects.filter(id_task__in=task_ids).delete()
    return redirect('home')

def edit_task(request,task_id):
    task = get_object_or_404(Task, id_task=task_id)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
            form = TaskForm(instance=task)

    return render(request,'edit_task.html',{'form':form,'task':task})

def update_task_completion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        completed = data.get('completed')

        try:
            task = Task.objects.get(id_task=task_id)

            if completed:
                task.data_completare = timezone.now()
            else:
                task.data_completare = None

            task.save()
            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False,'error':'Task not found'},status=404)
    return JsonResponse({'success': False,'error':'Invalid request method'},status=400)