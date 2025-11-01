from typing import Any, Dict

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import UntypedToken

from .models import Payment, User


class PaymentSerializer(ModelSerializer):
    """Суриализатор платежей"""

    class Meta:
        model = Payment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя с добавлением поля платежи"""

    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "phone", "city", "avatar"]


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Кастомный JWT-сериализатор, который возвращает access, refresh и данные пользователя.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data: Dict[str, Any] = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "username": self.user.username,
        }

        return data


class UserTokenRefreshSerializer(TokenRefreshSerializer):
    """
    Кастомный сериализатор для обновления токенов.
    Безопасно декодирует refresh-токен и возвращает данные пользователя.
    """

    def validate(self, attrs):
        data: Dict[str, Any] = super().validate(attrs)
        refresh_token_str = attrs.get("refresh")

        try:
            token = UntypedToken(refresh_token_str)
            user_id = token.get("user_id")

            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    data["user"] = {"id": user.id, "email": user.email}
                except User.DoesNotExist:  # type: ignore[attr-defined]
                    pass
        except (InvalidToken, TokenError):
            pass

        return data
