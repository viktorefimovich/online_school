from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson
from lms.serializers import CourseDetailSerializer, CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def get_permissions(self):
        if self.action in ["list"]:
            permission_classes = [IsAuthenticated, IsModerator]
        elif self.action in ["list", "retrieve", "update", "partial_update"]:
            permission_classes = [IsAuthenticated & IsOwner, IsModerator]
        elif self.action in ["create"]:
            permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ["destroy"]:
            permission_classes = [IsAuthenticated & IsOwner, ~IsModerator]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Moderators").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonCreateAPIView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]


class LessonListAPIView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator]


class LessonRetrieveAPIView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & IsOwner, IsModerator]


class LessonUpdateAPIView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & IsOwner, IsModerator]


class LessonDestroyAPIView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated & IsOwner, ~IsModerator]
