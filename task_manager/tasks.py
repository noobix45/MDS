import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from task_manager.models import Notificare, UtilizatorTask
from task_manager.views import send_email_mailjet

logger = logging.getLogger(__name__)

@shared_task
def trimite_notificari_periodic():
    acum = timezone.now()
    in_3_minute = acum + timedelta(minutes=3)

    notificari = Notificare.objects.filter(
        notif_dt__lte=in_3_minute,
        trimis=False
    )

    total_emailuri_trimise = 0

    logger.info(f"Found {notificari.count()} notifications to process.")

    for notif in notificari:
        task = notif.id_task
        utilizatori_task = UtilizatorTask.objects.filter(id_task=notif.id_task)

        for ut in utilizatori_task:
            if ut.id_utilizator.email:

                logger.info(f"Sending email to {ut.id_utilizator.email}")
                print("Sending email to {}".format(ut.id_utilizator.email))
                send_email_mailjet(
                    destinatar=ut.id_utilizator.email,
                    subiect=task.titlu,
                    continut_html=f"""
                    <html>
                      <body>
                        <h2>{task.titlu}</h2>
                        <p>{notif.mesaj if notif.mesaj else "Mesaj de test"}</p>
                      </body>
                    </html>
                    """,
                    continut_text = f"Notificare Task: {notif.mesaj if notif.mesaj else 'Mesaj de test'}"
                )
                total_emailuri_trimise += 1

        if task.repetitiv:
            notif.notif_dt += timedelta(days=7)
            notif.trimis = False
        else:
            notif.trimis = True
        notif.save()

    return f'Trimise {total_emailuri_trimise} emailuri pentru {notificari.count()} notificări.'

