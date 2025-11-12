from rest_framework import serializers


class VideoLinkValidator:
    """
    Валидатор, который проверяет, что ссылка принадлежит домену youtube.com.
    """
    def __init__(self, field):
        self.field = field

    def __call__(self, attrs):
        value = attrs.get(self.field)
        if value and "youtube.com" not in value and "youtu.be" not in value:
            raise serializers.ValidationError({self.field: "Можно добавлять только ссылки на YouTube!"})
        return attrs
