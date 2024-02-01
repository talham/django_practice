from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import CartItem
from django.contrib import messages
from .forms import OrderForm
from .models import Order
from decimal import Decimal
import datetime
# payment payment integration
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.urls import reverse


def makepayment(request):
# hold code for paypal integration
    host = request.get_host()  # get website domain
    amount = 0 # place 
    paypal_checkout =  {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': amount,
        'item_name': 'test',
        'invoice': uuid.uuid4(),
        'currency_code': 'USD',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('payment-success')}", # need to define
        'cancel_url': f"http://{host}{reverse('payment-failed')}"
    }

    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)

    context = {
        'product': 'product',
        'paypal': paypal_payment  
            }
    return HttpResponse('payment processed')


def payment(request):
    return render(request,'orders/payment.html')

def place_order(request, quantity=0,total=0):
    """creates and stores the place-order form"""
    # check if there are items in cart if not return user to the cart / checkout page
    # log-in is required for checkout, thus to place order user is logged-in

    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        messages.info(request,'Your shopping cart is empty. Please select some items prior to placing an order.')
        return redirect('store')
    
    # initialize values
    tax=0
    grand_total=0

    for item in cart_items:
        total += (item.product.price * item.quantity)
        quantity += item.quantity
        # calculate tax and total
    tax = round(Decimal('0.075') * total,2)
    grand_total = round(total + tax,2)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.street_address = form.cleaned_data['street_address']
            data.apt_address = form.cleaned_data['apt_address']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.zip_code = form.cleaned_data['zip_code']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip_address = request.META.get('REMOTE_ADDR')
            data.save()
            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)

            context = {
                'order' : order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,
            }

            return render(request,'orders/payment.html', context)
        
        else: 
            print('not valid')
            return redirect('checkout')    
    else: 
        print('not POST')
        return redirect('checkout')