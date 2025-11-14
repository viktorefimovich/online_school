from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription
from users.models import User


class LessonTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(email="user@example.com", password="123456")
        self.moderator = User.objects.create_user(email="mod@example.com", password="123456")
        self.moderator.groups.create(name="Moderators")

        self.course = Course.objects.create(name="Тестовый курс", owner=self.user)

        self.lesson = Lesson.objects.create(
            name="Тестовый урок", course=self.course, description="Описание урока", owner=self.user
        )

        self.list_url = reverse("lms:lesson-list")
        self.detail_url = reverse("lms:lesson-retrieve", kwargs={"pk": self.lesson.pk})
        self.detail_update_url = reverse("lms:lesson-update", kwargs={"pk": self.lesson.pk})

    def test_lesson_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_lesson_detail(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.lesson.name)

    def test_lesson_update_owner(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.detail_update_url, {"name": "Новое название"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Новое название")

    def test_subscribe_and_unsubscribe(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("lms:subscription-toggle")

        # Подписка
        response = self.client.post(url, {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # Отписка
        response = self.client.post(url, {"course_id": self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())
