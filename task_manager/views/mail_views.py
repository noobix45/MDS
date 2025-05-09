from mailjet_rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email_mailjet(destinatar, subiect, continut_html, continut_text):
    logger.info(f"Apel de functie send email.")
    continut_html = continut_html or "<p>Fără conținut HTML.</p>"
    continut_text = continut_text or "Fără conținut text."
    mailjet = Client(auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": settings.MAILJET_SENDER_EMAIL,
                    "Name": "Task Manager"
                },
                "To": [
                    {
                        "Email": destinatar,
                        "Name": "User"
                    }
                ],
                "Subject": subiect,
                "HTMLPart":continut_html.strip(),
                "TextPart":continut_text.strip()
            }
        ]
    }
    result = mailjet.send.create(data=data)
    logger.info(f"Mailjet response status: {result.status_code}")
    logger.info(f"Mailjet response: {result.text}")
    return result.status_code
