from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from lms.models import Course, Lesson, Subscription
from lms.validators import VideoLinkValidator


class LessonSerializer(ModelSerializer):
    """
    Сериализатор уроков
    """

    class Meta:
        model = Lesson
        fields = ("id", "name", "course", "preview", "video_link")
        validators = [VideoLinkValidator(field="video_link")]


class CourseSerializer(ModelSerializer):
    """
    Сериализатор курсов
    """
    is_subscribed = SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, course=obj).exists()
        return False

    class Meta:
        model = Course
        fields = ["id", "name", "description", "preview", "is_subscribed"]


class CourseDetailSerializer(ModelSerializer):
    """
    Сериализатор курса с добавлением полей: количества уроков в курсе, и самих уроков
    """

    count_lessons_in_course = SerializerMethodField()
    lessons = LessonSerializer(read_only=True, many=True)

    @staticmethod
    def get_count_lessons_in_course(obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = ("name", "count_lessons_in_course", "lessons")


class SubscriptionSerializer(ModelSerializer):
    """
    Сериализатор подписки пользователя на курс
    """

    class Meta:
        model = Subscription
        fields = ["id", "user", "course", "created_at"]
        read_only_fields = ["id", "created_at"]
