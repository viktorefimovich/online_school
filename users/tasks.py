from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import User  # ваша модель пользователя


@shared_task
def deactivate_inactive_users():
    """
    Деактивировать пользователей, которые не заходили более месяца.
    """
    one_month_ago = timezone.now() - timedelta(days=30)

    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_active=True)
    count = inactive_users.update(is_active=False)

    return f"{count} пользователей деактивировано"
