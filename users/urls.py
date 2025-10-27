from django.urls import path
from rest_framework.routers import DefaultRouter

from users.apps import UsersConfig
from users.views import UserViewSet, PaymentListAPIView, PaymentCreateAPIView, PaymentRetrieveAPIView, \
    PaymentUpdateAPIView, PaymentDestroyAPIView

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"", UserViewSet, basename="users")

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payments-list"),
    path("payments/create/", PaymentCreateAPIView.as_view(), name="payments-create"),
    path("payments/<int:pk>/", PaymentRetrieveAPIView.as_view(), name="payments-retrieve"),
    path("payments/<int:pk>/update/", PaymentUpdateAPIView.as_view(), name="payments-update"),
    path("payments/<int:pk>/delete/", PaymentDestroyAPIView.as_view(), name="payments-delete"),
]
urlpatterns += router.urls
