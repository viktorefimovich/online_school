from django.urls import path

from users.apps import UsersConfig
from users.views import (
    PaymentCreateAPIView,
    PaymentDestroyAPIView,
    PaymentListAPIView,
    PaymentRetrieveAPIView,
    PaymentUpdateAPIView,
    UserRetrieveAPIView,
    UserTokenObtainPairView,
    UserTokenRefreshView,
    UserListAPIView,
    UserRegisterAPIView,
    UserUpdateAPIView,
    UserDestroyAPIView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("list/", UserListAPIView.as_view(), name="user-list"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user-retrieve"),
    path("delete/", UserDestroyAPIView.as_view(), name="user-delete"),
    path("login/", UserTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token_refresh"),
    path("payments/", PaymentListAPIView.as_view(), name="payments-list"),
    path("payments/create/", PaymentCreateAPIView.as_view(), name="payments-create"),
    path("payments/<int:pk>/", PaymentRetrieveAPIView.as_view(), name="payments-retrieve"),
    path("payments/<int:pk>/update/", PaymentUpdateAPIView.as_view(), name="payments-update"),
    path("payments/<int:pk>/delete/", PaymentDestroyAPIView.as_view(), name="payments-delete"),
]
