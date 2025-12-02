from datetime import timedelta

from django.utils import timezone
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson, Subscription
from lms.paginators import CustomPagination
from lms.permissions import IsOwnerOrModerator
from lms.serializers import CourseDetailSerializer, CourseSerializer, LessonSerializer
from .tasks import send_course_update_emails
from users.permissions import IsModerator, IsOwner


class CourseViewSet(ModelViewSet):
    """
    Контролер Курсов
    """

    queryset = Course.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action in ["list"]:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["retrieve", "update", "partial_update"]:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action in ["create"]:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["destroy"]:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        return Course.objects.all().order_by("id")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        course = serializer.save()
        now = timezone.now()

        if not course.last_notification_sent or (now - course.last_notification_sent) >= timedelta(hours=4):
            course.last_notification_sent = now
            course.save(update_fields=["last_notification_sent"])
            send_course_update_emails.delay(course.id, None)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class LessonCreateAPIView(CreateAPIView):
    """
    Контролер создания урока
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & ~IsModerator]


class LessonListAPIView(ListAPIView):
    """
    Контролер списка уроков
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated | IsModerator]
    pagination_class = CustomPagination


class LessonRetrieveAPIView(RetrieveAPIView):
    """
    Контролер урока детально
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModerator]


class LessonUpdateAPIView(UpdateAPIView):
    """
    Контролер обновления урока
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]

    def perform_update(self, serializer):
        lesson = serializer.save()
        course = lesson.course
        if not course:
            return

        now = timezone.now()
        if not course.last_notification_sent or (now - course.last_notification_sent) >= timedelta(hours=4):

            course.last_notification_sent = now
            course.save(update_fields=["last_notification_sent"])
            send_course_update_emails.delay(course.id, lesson.id)


class LessonDestroyAPIView(DestroyAPIView):
    """
    Контролер удаления урока
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner, ~IsModerator]


class SubscriptionToggleAPIView(APIView):
    """
    Контролер подписки или отписки пользователя от курса.
    Если подписка существует — удаляем.
    Если нет — создаём.
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response({"error": "Не передан id курса"}, status=400)

        course = get_object_or_404(Course, id=course_id)
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            message = "Подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course)
            message = "Подписка добавлена"

        return Response({"message": message})
