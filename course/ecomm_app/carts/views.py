from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from decimal import Decimal
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def _cart_id(request):
    """private function to access the cart id"""
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart 

def _get_variation(request, product):
    """get a particular products selected variation"""
    assert request.method=='POST', "use POST request"
    product_variation = []
    for item in request.POST:
        key = item
        value = request.POST[key]
    
        try:
            variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
            product_variation.append(variation)
        except: 
            pass
        
    return product_variation

def _get_variation_item_id(cart_item):
    """get all existing variations and cart_items id """
    curr_var_list = []
    prod_id = []
    for item in cart_item: # get variations and ids for each product
        existing_variation = item.variations.all()
        curr_var_list.append(list(existing_variation))
        prod_id.append(item.id)
    return curr_var_list, prod_id

def _create_or_get_cart(request):
    """function to create or get cart"""
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # get cart using the cart_id present in session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    return cart



def add_cart(request,product_id):
    """add to cart function and increment cart items"""
    current_user = request.user
    product = Product.objects.get(id=product_id)
    
    # check if current user is authenticated 
    if current_user.is_authenticated and request.method == 'POST':
        product_variation = _get_variation(request,product)
        
        #get cart items
        cart_item_exists = CartItem.objects.filter(product=product,user=current_user).exists()

        if cart_item_exists: 
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            curr_var_list, prod_id = _get_variation_item_id(cart_item) 
            
            if product_variation in curr_var_list: 
                # increase the cart item quantity if variation already in cart
                index = curr_var_list.index(product_variation)
                item_id = prod_id[index]
                item = CartItem.objects.get(product=product,id=item_id)
                item.quantity += 1
                item.save()
            
            else: 
                # add a new item if variation not already in cart
                print('does not exist=')
                item = CartItem.objects.create(product=product,quantity=1,user=current_user)
            
                if len(product_variation) > 0: # check length of variations and add to database
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else: # if cart_item does not exist 
            cart = _create_or_get_cart(request)               
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
                cart = cart,
            )

            if len(product_variation) > 0: # check length of variations and add to database
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')

    else:    # if the user is not authenticated 
        if request.method == 'POST':
            product_variation = _get_variation(request,product)
            cart = _create_or_get_cart(request)    
            cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()

            if cart_item_exists: # update cart items
                cart_item = CartItem.objects.filter(product=product, cart=cart)
                curr_var_list, prod_id = _get_variation_item_id(cart_item)                 
                
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

            else: # cart item does not exist
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
        
        product = get_object_or_404(Product,id=product_id)
        if request.user.is_authenticated:
           cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
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
       
       product = get_object_or_404(Product, id=product_id)
       if request.user.is_authenticated:
          cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)    
       else: 
           cart = Cart.objects.get(cart_id=_cart_id(request))       
           cart_item = CartItem.objects.get(product=product,cart=cart, id=cart_item_id)
       cart_item.delete()
       print('test item')

    except Cart.DoesNotExist or CartItem.DoesNotExist:
        print('test except item')
        pass
    return redirect('cart')
 
def cart(request, total=0, quantity=0, tax=0, grand_total=0, cart_items=None):
    """function to calculate totals and return items"""
    
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else: # non-authenticated users
            cart = Cart.objects.get(cart_id=_cart_id(request)) 
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for item in cart_items:
            total += (item.product.price * item.quantity)
            quantity += item.quantity
            # calculate tax and total
        tax = round(Decimal('0.075') * total,2)
        grand_total = round(total + tax,2)

    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
        
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)

@login_required(login_url= 'login')
def checkout(request, total=0, quantity=0,tax=0, grand_total=0, cart_items=None):
    
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else: # non-authenticated users
            cart = Cart.objects.get(cart_id=_cart_id(request)) 
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:
            total += (item.product.price * item.quantity)
            quantity += item.quantity
        # calculate tax and total
        tax = round(Decimal('0.075') * total,2)
        grand_total = round(total + tax,2)

    except CartItem.DoesNotExist or Cart.DoesNotExist:
        pass # just ignore
        #  if Cart.DoesNotExist:
        #    cart = _create_or_get_cart(request)
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request,'store/checkout.html', context)