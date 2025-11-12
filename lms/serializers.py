from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from lms.models import Course, Lesson
from lms.validators import VideoLinkValidator


class LessonSerializer(ModelSerializer):
    """Суриализатор уроков"""

    class Meta:
        model = Lesson
        fields = ("id", "name", "course", "preview", "video_link")
        validators = [VideoLinkValidator(field="video_link")]


class CourseSerializer(ModelSerializer):
    """Суриализатор курсов"""

    class Meta:
        model = Course
        fields = "__all__"


class CourseDetailSerializer(ModelSerializer):
    """Сериализатор курса с добавлением полей: количества уроков в курсе, и самих уроков"""

    count_lessons_in_course = SerializerMethodField()
    lessons = LessonSerializer(read_only=True, many=True)

    @staticmethod
    def get_count_lessons_in_course(obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = ("name", "count_lessons_in_course", "lessons")
