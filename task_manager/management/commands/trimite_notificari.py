from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from task_manager.models import Notificare, UtilizatorTask
from task_manager.views import send_email_mailjet
from django.utils.timezone import localtime


class Command(BaseCommand):
    help = 'Trimite notificări programate prin email'

    def handle(self, *args, **kwargs):
        acum = timezone.now()

        # Verificăm ora curentă
        print("ACUM:", localtime(acum))  # Ora curentă locală

        # Afișăm notificările existente și orele lor
        print("Notif dt existente:")
        for n in Notificare.objects.all():
            print("-", localtime(n.notif_dt), "| trimis:", n.trimis)
        in_5_minute = acum + timedelta(minutes=5)

        notificari = Notificare.objects.filter(
            notif_dt__gte=acum,
            notif_dt__lte=in_5_minute,
            trimis=False
        )

        total_emailuri_trimise = 0

        for notif in notificari:
            utilizatori_task = UtilizatorTask.objects.filter(id_task=notif.id_task)

            for ut in utilizatori_task:
                if ut.id_utilizator.email:
                    send_email_mailjet(
                        destinatar=ut.id_utilizator.email,
                        subiect="Notificare task",
                        continut_html=notif.mesaj
                    )
                    total_emailuri_trimise += 1

            # Marchează notificarea ca trimisă o singură dată (nu per utilizator)
            notif.trimis = True
            notif.save()

        self.stdout.write(self.style.SUCCESS(
            f'Trimise {total_emailuri_trimise} emailuri pentru {notificari.count()} notificări.'
        ))
