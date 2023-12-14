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

    cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()

    if cart_item_exists: # update cart items
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        curr_var_list = []
        prod_id = []
        for item in cart_item: # get variations and ids for each product
            existing_variation = item.variations.all()
            curr_var_list.append(list(existing_variation))
            prod_id.append(item.id)
        
        print(curr_var_list)
        
        if product_variation in curr_var_list: 
            # increase the cart item quantity if variation already in cart
            index = curr_var_list.index(product_variation)
            item_id = prod_id[index]
            item = CartItem.objects.get(product=product,id=item_id)
            item.quantity += 1
            item.save()

        
        else: 
            # add a new item if variation not already in cart
            item = CartItem.objects.create(product=product,quantity=1,cart=cart)
           
            if len(product_variation) > 0: # check length of variations and add to database
                item.variations.clear()
                item.variations.add(*product_variation)
            item.save()

    else:
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )

        if len(product_variation) > 0: # check length of variations and add to database
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    """remove from cart functionality and decrement cart items"""
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product,id=product_id)
        cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)

        if cart_item.quantity >1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except Cart.DoesNotExist or CartItem.DoesNotExist:
        pass

    return redirect('cart')

def remove_cart_product(request,product_id, cart_item_id):
    """remove a product from cart"""
    try:
       cart = Cart.objects.get(cart_id=_cart_id(request))
       product = get_object_or_404(Product, id=product_id)
       cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)
       cart_item.delete()

    except Cart.DoesNotExist or CartItem.DoesNotExist:
        pass
    return redirect('cart')

 # my name is amal. i  like to play with my teddy bear.    

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