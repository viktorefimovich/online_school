from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet

router = DefaultRouter()
router.register(r"profiles", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]