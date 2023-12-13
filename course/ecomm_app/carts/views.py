from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from decimal import Decimal
from django.http import HttpResponse


def _cart_id(request):
    """private function to access the cart id"""
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart 

def add_cart(request,product_id):
    """add to cart function and increment cart items"""
    
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
       for item in request.POST:
            key = item
            value = request.POST[key]
           
            try:
               variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
               product_variation.append(variation)
            except: 
                pass

    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # get cart using the cart_id present in session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    try: # update cart items
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1 # increment cart item 
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )
        cart_item.save()

    return redirect('cart')

def remove_cart(request, product_id):
    """remove from cart functionality and decrement cart items"""
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product,id=product_id)
        cart_item = CartItem.objects.get(product=product,cart=cart)

        if cart_item.quantity >1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except Cart.DoesNotExist or CartItem.DoesNotExist:
        pass

    return redirect('cart')

def remove_cart_product(request,product_id):
    """remove a product from cart"""
    try:
       cart = Cart.objects.get(cart_id=_cart_id(request))
       product = get_object_or_404(Product, id=product_id)
       cart_item = CartItem.objects.get(product=product,cart=cart)
       cart_item.delete()

    except Cart.DoesNotExist or CartItem.DoesNotExist:
        pass
    return redirect('cart')

     

def cart(request, total=0, quantity=0, cart_items=None):
    """function to calculate totals and return items"""
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) 
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for item in cart_items:
            total += (item.product.price * item.quantity)
            quantity += item.quantity
        # calculate tax and total
        tax = round(Decimal('0.075') * total,2)
        grand_total = round(total + tax,2)
    except CartItem.DoesNotExist:
        pass # just ignore
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)