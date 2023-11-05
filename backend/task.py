from django.core.mail import EmailMessage, EmailMultiAlternatives
from celery import shared_task

from netology_pd_diplom.settings import EMAIL_HOST_USER
from backend.models import ConfirmEmailToken, User


@shared_task()
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param kwargs:
    :return:
    """
    # send an e-mail to the user

    msg = EmailMultiAlternatives(
        # title:

        f"Password Reset Token for {reset_password_token.user}",
        # message:
        reset_password_token.key,
        # from:
        EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
    msg.send()


@shared_task()
def send_mail(subject, message, email):
    msg = EmailMessage(subject, message, from_email=EMAIL_HOST_USER, to=[email])
    msg.send()


@shared_task()
def new_order(user_id, **kwargs):
    """
        отправяем письмо при изменении статуса заказа
        """
    # send an e-mail to the user
    user = User.objects.get(id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Обновление статуса заказа",
        # message:
        'Заказ сформирован',
        # from:
        EMAIL_HOST_USER,
        # to:
        [user.email]
    )
    msg.send()
