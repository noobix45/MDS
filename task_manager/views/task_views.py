# task_manager/task_views.py
from django.shortcuts import render, redirect, get_object_or_404
from task_manager.forms import TaskForm
from django.contrib import messages
from django.db import IntegrityError, InternalError, transaction,DatabaseError
from task_manager.models import UtilizatorTask,Utilizator,Notificare
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from task_manager.models import Task
from django.http import JsonResponse
from django.utils import timezone
import json
from datetime import datetime,date, timedelta,time

@login_required
def delete_tasks(request):
    if request.method == 'POST':
        task_ids = request.POST.getlist('task_ids')
        Task.objects.filter(id_task__in=task_ids).delete()
    return redirect('home')

def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        print("Form primit:", request.POST)

        if form.is_valid():
            print("Formular valid.")
            titlu = form.cleaned_data.get('titlu')
            importanta = form.cleaned_data.get('importanta')
            deadline = form.cleaned_data.get('deadline')
            repetitiv = form.cleaned_data.get('repetitiv')
            days_to_do = form.cleaned_data.get('days_to_do')
            def_time = form.cleaned_data.get('def_time')  # presupun că ai și acest câmp în form

            if not titlu:
                messages.error(request, 'Titlul este obligatoriu.')
                return render(request, 'create_task.html', {'form': form})

            if not importanta:
                messages.error(request, 'Importanța este obligatorie.')
                return render(request, 'create_task.html', {'form': form})

            # if deadline is not None and deadline < timezone.now().date():
            #     messages.error(request, 'Deadline-ul nu poate fi înainte de data curentă.')
            #     return render(request, 'create_task.html', {'form': form})

            try:
                with transaction.atomic():
                    task = form.save(commit=False)

                    if repetitiv:
                        if days_to_do:
                            task.days_to_do = days_to_do
                        else:
                            messages.error(request, 'Pentru un task repetitiv, trebuie să specifici zilele.')
                            return render(request, 'create_task.html', {'form': form})
                    else:
                        task.days_to_do = None

                    task.save()

                    utilizator = Utilizator.objects.get(user=request.user)
                    UtilizatorTask.objects.create(id_utilizator=utilizator, id_task=task)

                    # Construim deadline ca datetime, folosind ora maximă a zilei
                    if deadline:
                        deadline_datetime = datetime.combine(deadline, time.max)
                        deadline_datetime = timezone.make_aware(deadline_datetime)
                    else:
                        deadline_datetime = None

                    # Salvăm notificările normale (cele introduse manual)
                    for i in range(1, 4):
                        data_n = request.POST.get(f'notificare_data_{i}')
                        ora_n = request.POST.get(f'notificare_ora_{i}')
                        text_n = request.POST.get(f'notificare_text_{i}')
                        print(f"Notificare {i} - Data: {data_n}, Ora: {ora_n}, Text: {text_n}")

                        if data_n and ora_n:
                            try:
                                notif_naive = datetime.strptime(f"{data_n} {ora_n}", "%Y-%m-%d %H:%M")
                                notif_datetime = timezone.make_aware(notif_naive)

                                if deadline_datetime and notif_datetime > deadline_datetime:
                                    messages.error(request, f'Notificarea {i} are data/ora după deadline și nu a fost adăugată.')
                                    continue

                                mesaj_final = genereaza_mesaj_notificare(task, text_n or '')

                                Notificare.objects.create(
                                    id_task=task,
                                    notif_dt=notif_datetime,
                                    mesaj=mesaj_final
                                )
                                print(f"Notificare {i} salvată.")
                            except ValueError as e:
                                print(f"Notificare {i} eroare ValueError:", str(e))
                                messages.error(request, f'Notificarea {i} are date invalide și nu a fost adăugată.')
                                continue

                    # Salvăm notificările repetitive dacă taskul este repetitiv și are zile + ora definită
                    if task.repetitiv and task.days_to_do and def_time:
                        azi = timezone.now().date()
                        zi_azi = azi.isoweekday()  # ziua curentă ca număr (1=luni..7=duminică)

                        for zi in task.days_to_do:
                            delta_zile = (zi - zi_azi) % 7
                            data_notif = azi + timedelta(days=delta_zile)
                            ora_notif = datetime.combine(data_notif, def_time)
                            ora_notif = timezone.make_aware(ora_notif)

                            # Poți decide dacă vrei să verifici deadline-ul aici
                            if deadline_datetime is None or notif_datetime <= deadline_datetime:
                                Notificare.objects.create(
                                    id_task=task,
                                    notif_dt=ora_notif,
                                    mesaj=genereaza_mesaj_notificare(task, f"Reminder {task.titlu}"),
                                    repetitiva=True
                                )
                        print("Notificările repetitive au fost salvate.")

                messages.success(request, 'Task-ul a fost creat cu succes.')
                return redirect('create_task')

            except IntegrityError as e:
                messages.error(request, 'Eroare neașteptată la salvarea în baza de date. Verifică datele și încearcă din nou.')
                return render(request, 'create_task.html', {'form': form})
            except DatabaseError as e:
                # verifică dacă eroarea e exact cea cu notificarea înainte de data creare
                if 'Notification date' in str(e):
                    messages.error(request, "Data notificării nu poate fi înainte de data creării taskului.")
                else:
                    messages.error(request, "A apărut o eroare la salvarea taskului.")

                # Rămâi pe pagina de create task cu mesajul de eroare
                return render(request, 'create_task.html', {'form': form})

        else:
            messages.error(request, 'Formularul conține erori. Te rog verifică câmpurile.')
            return render(request, 'create_task.html', {'form': form})

    else:
        form = TaskForm()
    return render(request, 'create_task.html', {'form': form})

def delete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id_task=task_id)
        task.delete()
    return redirect('home')

def edit_task(request,task_id):

    task = get_object_or_404(Task, id_task=task_id)
    notificari = Notificare.objects.filter(id_task=task,repetitiva=False)

    if request.method == 'POST':

        print("=== POST Request Received ===")
        print("POST data:", request.POST)

        form = TaskForm(request.POST, instance=task)
        if form.is_valid():

            print("Form is valid.")
            print("repetitiv:", form.cleaned_data.get('repetitiv'))
            print("days_to_do:", form.cleaned_data.get('days_to_do'))
            # task_save_needed = False
            if not form.cleaned_data['repetitiv']:
                # Setați days_to_do gol explicit
                form.instance.days_to_do = None  # sau [] în funcție de tip
            task = form.save()

            deadline = task.deadline
            data_creare = task.data_creare

            for i in range(1, 4):
                date_str = request.POST.get(f'notif_date_{i}')
                time_str = request.POST.get(f'notif_time_{i}')
                mesaj_input = request.POST.get(f'notif_msg_{i}')

                mesaj = genereaza_mesaj_notificare(task, mesaj_input)

                print(f"\n--- Notificare {i} ---")
                print("Date:", date_str)
                print("Time:", time_str)
                print("Mesaj:", mesaj)

                if date_str and time_str: # daca am input de modificare
                    try:
                        notif_dt = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
                        notif_dt = timezone.make_aware(notif_dt, timezone.get_current_timezone())

                        if notif_dt < data_creare:
                            print(f"Notificarea {i} este înainte de data creării taskului.")
                            messages.error(request,f'Notificarea {i} este înainte de data creării taskului și a fost ignorată.')
                            continue

                        if deadline:
                            deadline_dt = datetime.combine(deadline, time.max)
                            deadline_dt = timezone.make_aware(deadline_dt)
                            if notif_dt > deadline_dt:
                                print(f"Notificarea {i} este după deadline.")
                                messages.error(request, f'Notificarea {i} este după deadline și a fost ignorată.')
                                continue

                        if i <= len(notificari):
                            notificare = notificari[i-1]
                            print(f"Actualizez notificarea existentă {i}")
                            notificare.notif_dt = notif_dt
                            notificare.mesaj = mesaj
                            if notificare.trimis:
                                notificare.trimis = False

                            if notif_dt > timezone.now():
                                notificare.save()
                                # notificari_actualizate = True
                            else:
                                messages.warning(request, f'Notificare {i}: Vii din trecut? 🤔')
                        else:
                            print(f"Creare notificare nouă {i}")
                            Notificare.objects.create(
                                id_task=task,
                                notif_dt=notif_dt,
                                mesaj=mesaj
                            )
                            # notificari_actualizate = True
                    except ValueError:
                        messages.warning(request, f'Notificarea {i} are un format invalid.')

            messages.success(request, 'Task-ul a fost actualizat.')
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