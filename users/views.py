from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Payment, User
from .serializers import (
    PaymentSerializer,
    UserSerializer,
    UserTokenObtainPairSerializer,
    UserTokenRefreshSerializer,
    PaymentStatusSerializer,
)
from .services import create_product, create_stripe_price, create_session, retrieve_session


class UserRegisterAPIView(CreateAPIView):
    """
    Регистрация(создание) пользователя
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)

        user.set_password(serializer.validated_data["password"])
        user.save()


class UserRetrieveAPIView(RetrieveAPIView):
    """
    Подробное описание пользователя
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class UserListAPIView(ListAPIView):
    """
    Список пользователей
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserUpdateAPIView(UpdateAPIView):
    """
    Обновление информации о пользователе
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user != obj:
            self.permission_denied(self.request, message="Можно редактировать только свой профиль.")
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class UserDestroyAPIView(DestroyAPIView):
    """
    Удаление пользователя
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user != obj:
            self.permission_denied(self.request, message="Можно удалять только свой профиль.")
        return obj


class PaymentCreateAPIView(CreateAPIView):
    """
    Создание платежа пользователя
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        item = payment.course if payment.course else payment.lesson

        product_id = create_product(item)

        stripe_price = create_stripe_price(amount=payment.amount, product_id=product_id)
        price_id = stripe_price.get("id")

        session_id, payment_url = create_session(price_id)

        payment.session_id = session_id
        payment.payment_link = payment_url
        payment.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        payment = Payment.objects.get(id=response.data["id"])

        return Response(
            {
                "payment_id": payment.id,
                "amount": payment.amount,
                "session_id": payment.session_id,
                "payment_link": payment.payment_link,
            }
        )


class PaymentListAPIView(ListAPIView):
    """
    Список платежей пользователя
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = (
        "course",
        "lesson",
        "payment_method",
    )
    ordering_fields = ("payment_date",)
    permission_classes = [IsAuthenticated]


class PaymentRetrieveAPIView(RetrieveAPIView):
    """
    Платеж подробно
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]


class PaymentUpdateAPIView(UpdateAPIView):
    """
    Обновление информации о платеже
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]


class PaymentDestroyAPIView(DestroyAPIView):
    """
    Удаление платежа
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]


class UserTokenObtainPairView(TokenObtainPairView):
    """
    Получение токена доступа и токена сброса
    """

    serializer_class = UserTokenObtainPairSerializer
    permission_classes = [AllowAny]


class UserTokenRefreshView(TokenRefreshView):
    """
    Обновление токена сброса
    """

    serializer_class = UserTokenRefreshSerializer
    permission_classes = [AllowAny]


class PaymentStatusAPIView(APIView):
    """
    Проверка статуса платежа по session_id.
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, pk):
        try:
            payment = Payment.objects.get(pk=pk, user=request.user)
        except Payment.DoesNotExist:
            return Response({"error": "Платёж не найден"}, status=status.HTTP_404_NOT_FOUND)

        if not payment.session_id:
            return Response({"error": "У платежа нет session_id"}, status=status.HTTP_400_BAD_REQUEST)

        session = retrieve_session(payment.session_id)

        data = {
            "session_id": session.id,
            "status": session.status,
            "payment_status": session.payment_status,
            "amount_total": session.amount_total,
            "currency": session.currency,
        }

        serializer = PaymentStatusSerializer(data)
        return Response(serializer.data)
