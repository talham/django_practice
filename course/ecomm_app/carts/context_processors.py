from .models import Cart, CartItem
from .views import _cart_id


def counter(request): 
    """counts the number of items in the cart"""
    if 'admin' in request.path:
        return {} # empty dictionary
    else: 
        try: 
            cart_count=0
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            cart_items = CartItem.objects.all().filter(cart=cart[:1]) # only one result
            for item in cart_items:
                cart_count += item.quantity
        except Cart.DoesNotExist:
            cart_count=0
    return dict(cart_count=cart_count)