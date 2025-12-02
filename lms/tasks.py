from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_course_update_emails(course_id, lesson_id):
    from lms.models import Course, Lesson, Subscription
    from django.conf import settings

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return f"Course {course_id} not found"

    try:
        lesson = Lesson.objects.get(pk=lesson_id)
    except Lesson.DoesNotExist:
        lesson = None

    subscriptions = Subscription.objects.filter(course=course).select_related("user")

    subject = f"Обновление курса: {course.name}"
    if lesson:
        message_body = f"Урок «{lesson.name}» в курсе «{course.name}» был обновлён. Зайдите, чтобы увидеть изменения."
    else:
        message_body = f"Курс «{course.name}» был обновлён. Зайдите, чтобы увидеть изменения."

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "skayproapp@yandex.ru")

    for sub in subscriptions:
        user = sub.user
        if not user.email:
            continue
        send_mail(
            subject=subject,
            message=f"Здравствуйте, {user.email}!\n\n{message_body}",
            from_email=from_email,
            recipient_list=[user.email],
            fail_silently=True,
        )
