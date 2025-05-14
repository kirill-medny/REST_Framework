from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from lms import serializers
from lms.models import Course, Lesson
from payments.services import (
    create_stripe_checkout_session,
    create_stripe_price,
    create_stripe_product,
    stripe,
)
from users.models import Payment, User
from users.permissions import IsOwner
from users.serializers import (
    MyTokenObtainPairSerializer,
    PaymentSerializer,
    PublicUserSerializer,
    RegistrationSerializer,
    UserSerializer,
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
            raise serializers.ValidationError(
                "Either paid_course or paid_lesson must be provided."
            )

        # Получение объекта курса/урока
        paid_course = get_object_or_404(Course, pk=course_id) if course_id else None
        paid_lesson = get_object_or_404(Lesson, pk=lesson_id) if lesson_id else None
        amount = (
            paid_course.price if paid_course else paid_lesson.price
        )  # Предполагается, что есть поле price в модели

        # Создание продукта в Stripe
        product_name = paid_course.name if paid_course else paid_lesson.name
        product_description = (
            paid_course.description if paid_course else paid_lesson.description
        )
        stripe_product_id = create_stripe_product(
            name=product_name, description=product_description
        )

        if not stripe_product_id:
            raise serializers.ValidationError("Could not create Stripe product.")

        # Создание цены в Stripe
        stripe_price_id = create_stripe_price(
            product_id=stripe_product_id, amount=amount
        )
        if not stripe_price_id:
            raise serializers.ValidationError("Could not create Stripe price.")

        # Создание сессии Checkout
        success_url = self.request.build_absolute_uri(f"/payment/success/{user.id}/")
        cancel_url = self.request.build_absolute_uri("/payment/cancel/")
        checkout_url = create_stripe_checkout_session(
            price_id=stripe_price_id, success_url=success_url, cancel_url=cancel_url
        )

        if not checkout_url:
            raise serializers.ValidationError(
                "Could not create Stripe checkout session."
            )

        # Сохранение данных о платеже
        payment = serializer.save(
            user=user,
            payment_amount=amount,
            payment_method="stripe",
            paid_course=paid_course,
            paid_lesson=paid_lesson,
            payment_url=checkout_url,
            stripe_checkout_session_id=checkout_session_id,  # Сохраняем ID сессии
        )
        return payment


@extend_schema(tags=["Payments"], description="Get payment status by session ID")
class PaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

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

            return Response(
                {"status": session.payment_status, "payment_id": payment.id},
                status=status.HTTP_200_OK,
            )
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )
