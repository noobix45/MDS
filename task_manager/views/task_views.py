# task_manager/task_views.py
from django.shortcuts import render, redirect, get_object_or_404
from task_manager.forms import TaskForm
from django.contrib import messages
from django.db import IntegrityError
from task_manager.models import UtilizatorTask,Utilizator,Notificare
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from task_manager.models import Task
from django.http import JsonResponse
from django.utils import timezone
import json
from datetime import datetime,date

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

                for i in range(1, 4):
                    date_str = request.POST.get(f'notif_date_{i}')
                    time_str = request.POST.get(f'notif_time_{i}')
                    mesaj_input = request.POST.get(f'notif_msg_{i}')

                    mesaj = genereaza_mesaj_notificare(task, mesaj_input)

                    if date_str and time_str:
                        try:
                            notif_dt = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
                            notificare = Notificare(
                                id_task=task,
                                notif_dt=notif_dt,
                                mesaj=mesaj
                            )
                            notificare.save()
                        except ValueError:
                            messages.warning(request, f'Notificarea {i} are un format invalid.')
                messages.success(request, 'Task și notificările au fost create.')

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

def delete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id_task=task_id)
        task.delete()
    return redirect('home')

def edit_task(request,task_id):

    task = get_object_or_404(Task, id_task=task_id)
    notificari = Notificare.objects.filter(id_task=task)
    notificari_actualizate = False
    mesaj_eroare = None

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task_save_needed = False
            task_saved = form.save(commit=False)
            if task_saved != task:
                task_save_needed = True

            for i in range(1, 4):
                date_str = request.POST.get(f'notif_date_{i}')
                time_str = request.POST.get(f'notif_time_{i}')
                mesaj_input = request.POST.get(f'notif_msg_{i}')

                mesaj = genereaza_mesaj_notificare(task, mesaj_input)

                if date_str and time_str: # daca am input de modificare
                    try:
                        notif_dt = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
                        notif_dt = timezone.make_aware(notif_dt, timezone.get_current_timezone())
                        if i <= len(notificari):
                            notificare = notificari[i-1]
                            notificare.notif_dt = notif_dt
                            notificare.mesaj = mesaj
                            if notificare.trimis:
                                notificare.trimis = False

                            if notif_dt > timezone.now():
                                notificare.save()
                                notificari_actualizate = True
                            else:
                                mesaj_eroare = f'Notificare {i} Vii din trecut?🤔'
                        else:
                            Notificare.objects.create(
                                id_task=task,
                                notif_dt=notif_dt,
                                mesaj=mesaj
                            )
                            notificari_actualizate = True
                    except ValueError:
                        messages.warning(request, f'Notificarea {i} are un format invalid.')

            if task_save_needed:
                task_saved.save()

            if not notificari_actualizate and not task_save_needed:
                messages.info(request, 'Nu s-au făcut modificări.')
            elif notificari_actualizate or task_save_needed:
                messages.success(request, 'Task-ul și notificările au fost actualizate cu succes.')
            elif mesaj_eroare:
                messages.warning(request, mesaj_eroare)

            return redirect('edit-task', task_id=task.id_task)
    else:
            form = TaskForm(instance=task)

    notificari = list(notificari)
    notificari += [None] * (3 - len(notificari))
    return render(request,'edit_task.html',{'form':form,'task':task, 'notificari': notificari})

def genereaza_mesaj_notificare(task, mesaj_input):
    if mesaj_input:
        return mesaj_input
    if task.deadline:
        zile_ramase = (task.deadline - date.today()).days
        if zile_ramase == 1:
            return "Mai ai o zi pana la deadline"
        else:
            return f"Mai ai {zile_ramase} zile pana la deadline"
    return "Reminder"

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