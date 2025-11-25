from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from lms.models import Course, Subscription, Lesson


@shared_task
def send_notification_email(user_email, course, lesson):
    send_mail(
        subject=f"Обновление курса: {course.name}",
        message=f"Урок '{lesson.name}' курса '{course.name}' был обновлён. Проверьте новые материалы.",
        from_email="no-reply@example.com",
        recipient_list=[user_email],
    )


@shared_task
def send_course_update_emails(course_id, lesson_id):
    from lms.models import Course, Lesson, Subscription

    course = Course.objects.get(pk=course_id)
    lesson = Lesson.objects.get(pk=lesson_id)

    subscriptions = Subscription.objects.filter(course=course)
    for sub in subscriptions:
        send_notification_email(sub.user.email, course, lesson)

    course.last_notification_sent = timezone.now()
    course.save()
