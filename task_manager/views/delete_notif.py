from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from task_manager.models import Notificare
from django.contrib import messages

@csrf_exempt  # doar temporar dacă nu vrei să trimiți CSRF token
def delete_notificare_api(request, id_notif):
    if request.method == 'POST':
        notif = get_object_or_404(Notificare, id_notificare=id_notif)
        notif.delete()
        messages.success(request, 'Notificarea a fost ștearsă cu succes.')
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)