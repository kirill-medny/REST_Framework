from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import filters, generics, permissions, serializers, status, viewsets
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from lms.models import Course, Lesson
from payments.services import (
    PaymentError,
    create_stripe_checkout_session,
    create_stripe_price,
    create_stripe_product,
    stripe,
    PaymentError,
)
from users.models import Payment, User
from users.permissions import IsOwner
from users.serializers import (
    MyTokenObtainPairSerializer,
    PaymentSerializer,
    PublicUserSerializer,
    RegistrationSerializer,
    UserSerializer,
    PaymentStatusResponse,
)


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
        if self.action == "retrieve" and self.request.user != self.get_object():
            return PublicUserSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        elif self.action in ["update", "partial_update"]:
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


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        course_id = self.request.data.get("paid_course")
        lesson_id = self.request.data.get("paid_lesson")

        if not (course_id or lesson_id):
            raise ParseError("Either paid_course or paid_lesson must be provided.")

        # Получение объекта курса/урока
        product = (
            get_object_or_404(Course, pk=course_id)
            if course_id
            else get_object_or_404(Lesson, pk=lesson_id)
        )
        amount = product.price  # Предполагается, что есть поле price в модели
        stripe_product_id = create_stripe_product(
            name=product.name, description=product.description
        )

        if not stripe_product_id:
            raise PaymentError("Failed to create product")

        # Создание цены в Stripe
        stripe_price_id = create_stripe_price(
            product_id=stripe_product_id, amount=amount
        )
        if not stripe_price_id:
            raise PaymentError("Failed to create price")

        # Создание сессии Checkout
        success_url = self.request.build_absolute_uri(f"/payment/success/{user.id}/")
        cancel_url = self.request.build_absolute_uri("/payment/cancel/")
        checkout_url = create_stripe_checkout_session(
            price_id=stripe_price_id, success_url=success_url, cancel_url=cancel_url
        )

        if not checkout_url:
            raise PaymentError("Failed to create checkout session")

        # Сохранение данных о платеже
        serializer.save(
            user=user,
            payment_amount=amount,
            payment_method="stripe",
            paid_course=course_id if course_id else None,
            paid_lesson=lesson_id if lesson_id else None,
            payment_url=checkout_url,
        )


@extend_schema(responses={200: PaymentStatusResponse}, tags=["Payments"])
@extend_schema(
    description="Получение статуса платежа по ID сессии Stripe",
    responses={
        200: PaymentStatusResponse,
        400: {"description": "Bad Request"},
        404: {"description": "Payment not found"},
    },
    tags=["Payments"],
)
class PaymentStatusAPIView(generics.RetrieveAPIView):
    """
    Получение статуса платежа по ID сессии Stripe.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentStatusResponse  # Добавляем сериализатор для документации
    lookup_field = "session_id"  # Указываем поле для поиска

    def get(self, request, session_id):
        """
        Получение статуса платежа по ID сессии Stripe.
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            payment = Payment.objects.get(
                stripe_checkout_session_id=session_id
            )  # Получаем платеж

            if session.payment_status == "paid":
                payment.is_paid = True
                payment.save()

            serializer = self.get_serializer(
                data={"status": session.payment_status, "payment_id": payment.id}
            )
            serializer.is_valid(raise_exception=True)  # Валидируем сериализатор

            return Response(
                {"status": session.payment_status, "payment_id": payment.id},
                status=status.HTTP_200_OK,
            )
        except stripe.error.StripeError as e:
            raise ParseError(str(e))  # Меняем на ParseError
        except Payment.DoesNotExist:
            raise NotFound()  # Используем NotFound
