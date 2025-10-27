from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from lms.models import Course, Lesson
from users.models import Payment


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class CourseDetailSerializer(ModelSerializer):
    count_lessons_in_course = SerializerMethodField()
    lessons = LessonSerializer(read_only=True, many=True)

    @staticmethod
    def get_count_lessons_in_course(obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = ("name", "count_lessons_in_course", "lessons")
