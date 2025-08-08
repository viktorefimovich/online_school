from django.db import models


class Course(models.Model):
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

    def __str__(self):
        return f"{self.pk} | {self.name}"

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    name = models.CharField(max_length=150, verbose_name="Урок", help_text="Укажите урок")
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        verbose_name="Курс",
        help_text="Укажите курс",
        blank=True,
        null=True,
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

    def __str__(self):
        return f"{self.pk} | {self.name}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
