import stripe
from django.conf import settings
from rest_framework.exceptions import APIException

stripe.api_key = settings.STRIPE_SECRET_KEY  # Загружаем секретный ключ из settings


class PaymentError(APIException):
    status_code = 503
    default_code = "payment_error"
    default_detail = "Payment error occurred"


def create_stripe_product(name: str, description: str) -> str | None:
    """
    Создает продукт в Stripe.
    :param name: Название продукта.
    :param description: Описание продукта.
    :return: ID продукта в Stripe.
    """
    try:
        product = stripe.Product.create(
            name=name,
            description=description,
        )
        return product.id
    except stripe.error.StripeError as e:
        # Обработка ошибок Stripe
        print(f"Stripe error creating product: {e}")
        return None


def create_stripe_price(
    product_id: str, amount: float, currency: str = "usd"
) -> str | None:
    """
    Создает цену в Stripe для продукта.
    :param product_id: ID продукта в Stripe.
    :param amount: Сумма в копейках (например, 199.99 -> 19999).
    :param currency: Валюта (например, 'usd', 'rub').
    :return: ID цены в Stripe.
    """
    try:
        price = stripe.Price.create(
            product=product_id,
            unit_amount=int(amount * 100),  # Преобразуем в копейки
            currency=currency,
            # recurring={"interval": "month"},  # Раскомментируйте для периодических платежей (подписок)
        )
        return price.id
    except stripe.error.StripeError as e:
        # Обработка ошибок Stripe
        print(f"Stripe error creating price: {e}")
        return None


def create_stripe_checkout_session(
    price_id: str, success_url: str, cancel_url: str
) -> str | None:
    """
    Создает сессию Checkout в Stripe.
    :param price_id: ID цены в Stripe.
    :param success_url: URL, на который перенаправляется пользователь после успешной оплаты.
    :param cancel_url: URL, на который перенаправляется пользователь после отмены оплаты.
    :return: URL для оплаты или None в случае ошибки.
    """
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            mode="payment",  # Или 'subscription' для подписок
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return checkout_session.url
    except stripe.error.StripeError as e:
        # Обработка ошибок Stripe
        print(f"Stripe error creating checkout session: {e}")
        return None
