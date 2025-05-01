# task_manager/task_views.py
from django.shortcuts import render, redirect
from task_manager.forms import TaskForm
from django.contrib import messages
from django.db import IntegrityError
from task_manager.models import UtilizatorTask,Utilizator
from django.core.exceptions import ObjectDoesNotExist

def create_task(request):

    if request.method == 'POST': # trimit datele catre baza de date
        form = TaskForm(request.POST)
        if form.is_valid():
            try:
                task = form.save(commit=False)
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

    return render(request, 'create_task.html', {'form': form})
