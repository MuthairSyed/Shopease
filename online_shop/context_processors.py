from cart.utils.cart import Cart
from shop.models import Category
from django.conf import settings

def return_cart(request):
    cart = Cart(request)
    try:
        cart_count = len(cart)
    except (TypeError, ValueError):
        # Handle case where cart is not properly initialized
        cart_count = 0
    return {'cart_count': cart_count}


def return_categories(request):
    categories = Category.objects.all()
    return {'categories': categories}


def media_processor(request):
    return {'MEDIA_URL': settings.MEDIA_URL}