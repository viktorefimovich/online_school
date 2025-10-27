from django.contrib import admin

from lms.models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "preview", "description")
    search_fields = ("name",)
    list_filter = ("name",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "video_link")
    search_fields = ("name", "course__name")
    list_filter = ("course",)
