from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from lms.models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    """
    Отправка уведомлений всем пользователям,
    которые подписаны на обновления данного курса.
    """
    course = Course.objects.get(id=course_id)
    subscriptions = Subscription.objects.filter(course=course).select_related("user")

    for sub in subscriptions:
        user = sub.user

        send_mail(
            subject=f"Обновление курса: {course.name}",
            message=(
                f"Здравствуйте, {user.email}!\n\n"
                f"Курс «{course.name}» был обновлён.\n"
                f"Зайдите в личный кабинет, чтобы посмотреть новые материалы."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[sub.user.email],
            fail_silently=True,
        )

    return f"Писем отправлено: {subscriptions.count()}"
