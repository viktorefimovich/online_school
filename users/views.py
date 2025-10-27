from rest_framework.viewsets import ModelViewSet
from .serializers import UserSerializer, PaymentSerializer
from .models import User, Payment


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "email"


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    lookup_field = "user"
