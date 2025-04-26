from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets, permissions
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer, MyTokenObtainPairSerializer, RegistrationSerializer, \
    PublicUserSerializer
from users.permissions import IsOwner

class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.request.user != self.get_object():
            return PublicUserSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsOwner]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]



class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # Фильтрация по курсу и уроку
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]

    # Сортировка по дате
    ordering_fields = ["payment_date"]
