from django.db import models


class Course(models.Model):
    """
    Модель курсов.
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название курса",
        help_text="Укажите название курса",
    )
    preview = models.ImageField(
        upload_to="lms/previews",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите превью",
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание", help_text="Введите описание")
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="courses",
        null=True,
        blank=True,
        help_text="Укажите владелца",
    )
    last_notification_sent = models.DateTimeField(verbose_name="Время последнего уведомления", null=True, blank=True)

    def __str__(self):
        return f"{self.pk} | {self.name}"

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    """
    Модель уроков.
    """

    name = models.CharField(max_length=150, verbose_name="Урок", help_text="Укажите урок")
    course = models.ForeignKey(
        "lms.Course",
        on_delete=models.SET_NULL,
        verbose_name="Курс",
        help_text="Укажите курс",
        blank=True,
        null=True,
        related_name="lessons",
    )
    description = models.TextField(verbose_name="Описание", help_text="Введите описание")
    preview = models.ImageField(
        upload_to="lms/previews",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите превью",
    )
    video_link = models.URLField(
        max_length=200, null=True, blank=True, verbose_name="Ссылка на видео", help_text="Укажите ссылку на видео"
    )
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="lessons",
        null=True,
        blank=True,
        help_text="Укажите владелца",
    )

    def __str__(self):
        return f"{self.pk} | {self.name}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Subscription(models.Model):
    """
    Модель подписки пользователя на курс.
    """

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="subscriptions", verbose_name="Пользователь"
    )
    course = models.ForeignKey(
        "lms.Course", on_delete=models.CASCADE, related_name="subscriptions", verbose_name="Курс"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    def __str__(self):
        return f"{self.user.email} подписан на {self.course.name}"

    class Meta:
        unique_together = ("user", "course")
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
