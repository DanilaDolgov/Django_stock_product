import os
from django.core.mail import EmailMessage
from celery import shared_task

from netology_pd_diplom.settings import EMAIL_HOST_USER


@shared_task()
def send_mail(subject, message, email):
    os.environ["DJANGO_SETTINGS_MODULE"] = "netology_pd_diplom.settings"
    msg = EmailMessage(subject, message, from_email=EMAIL_HOST_USER, to=[email])
    msg.send()
