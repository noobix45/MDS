from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from task_manager.models import Task,Utilizator,UtilizatorTask
from task_manager.ai_sorter import sort_tasks_with_ai
from django.contrib import messages
from django.utils.timezone import make_aware, is_naive
@login_required
def ai_prioritize_user_tasks(request):
    try:
        utilizator = Utilizator.objects.get(user=request.user)
        messages.info(request, "AI sorting in progress, please wait...")

        utilizator_task = UtilizatorTask.objects.filter(id_utilizator = utilizator)
        taskuri = Task.objects.filter(
            id_task__in=[rel.id_task.id_task for rel in utilizator_task],
            grup_task=False,
            data_completare__isnull=True
        )
        print("Taskuri preluate:", taskuri)

        rezultate = sort_tasks_with_ai(taskuri)

        for task_id, score in rezultate.items():
            try:
                task = Task.objects.get(id_task=task_id)
                if task.data_creare and is_naive(task.data_creare):
                    task.data_creare = make_aware(task.data_creare)
                task.prioritate = score
                task.save()

                # Verifică dacă taskul a fost salvat corect
                print(f"Task {task.id_task} a fost actualizat cu prioritatea {task.prioritate}")
            except (ValueError, Task.DoesNotExist):
                continue
        messages.success(request, "Taskurile au fost prioritizate cu succes.")
    except Utilizator.DoesNotExist:
        messages.error(request, "Utilizatorul nu a fost gasit.")
    return redirect("home")