from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from lms.models import Course, Lesson


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер пользователей, где email является уникальным идентификатором"""

    def create_user(self, email, password=None, **extra_fields):
        """Создает и возвращает пользователя с email и паролем"""
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и возвращает суперпользователя с email и паролем"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Почта", help_text="Укажите почту")
    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Укажите телефон",
    )
    city = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Укажите город",
    )
    avatar = models.ImageField(
        upload_to="users/avatars",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь",
                             help_text="Укажите пользователя")
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Сумма оплаты",
                                 help_text="Укажите сумму оплаты")
    payment_method = models.CharField(max_length=20, choices=[("cash", "Наличные"), ("transfer", "Перевод на счёт")],
                                      verbose_name="Способ оплаты", help_text="Укажите способ оплаты")
    payment_date = models.DateField(verbose_name="Дата оплаты", help_text="Укажите дату оплаты")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Платеж {self.user} за {self.course if self.course else self.lesson} сумма {self.amount}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
