import stripe
from django.conf import settings

from lms.models import Lesson, Course

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_price(amount, product_id):
    """
    Получение цены для stripe на основе
    """

    stripe_price = stripe.Price.create(currency="rub", unit_amount=amount * 100, product=product_id)

    return stripe_price


def create_session(price):
    """
    Создание ссесии
    """
    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000/",
        cancel_url="http://127.0.0.1:8000/cancel/",
        line_items=[{"price": price, "quantity": 1}],
        mode="payment",
    )
    return session.get("id"), session.get("url")


def create_product(item: Lesson | Course):
    """
    Создание продукта
    """

    product = stripe.Product.create(name=item.name, description=item.description)
    return product.get("id")
