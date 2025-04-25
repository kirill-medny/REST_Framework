from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # Фильтрация по курсу и уроку
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]

    # Сортировка по дате
    ordering_fields = ["payment_date"]
