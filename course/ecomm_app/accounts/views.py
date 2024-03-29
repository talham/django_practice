from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
# verification email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
# carts
from carts.models import Cart, CartItem
from carts.views import _cart_id, _get_variation_item_id
# requests library
import requests


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name = first_name,last_name = last_name,
            email=email, username=username, password = password
            )
            user.phone_number = phone_number
            user.save()
            
            # USER Activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            messages.success(request, 'Registration Successful! Please verify your account by clicking on the verification link in your email')
            #user.is_active = True
            #user.save()
            return redirect('login')
    else: 
        form = RegistrationForm()
        
    context = {
        'form': form,
    }
    return render(request,'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(email=email,password=password)

        if user is not None:
            try: 
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if cart_item_exists:
                    # getting product variations by cart id
                    cart_item = CartItem.objects.filter(cart=cart)
                    curr_var_list, prod_id = _get_variation_item_id(cart_item)

                    # get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    usr_var_list, usr_prod_id = _get_variation_item_id(cart_item)

                    for pr in curr_var_list: 
                        if pr in usr_var_list:
                            item_id = usr_prod_id(usr_var_list.index(pr))
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()

                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            print('check for cartitem')
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request,user)
            messages.success(request,'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try: 
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except: 
                return redirect('dashboard')
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login')

    return render(request,'accounts/login.html')

@login_required(login_url= 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You have been logged out')
    return redirect('login')

@login_required(login_url= 'login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')


def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError,ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Thank you for activating your account!')
        return redirect('login')
    else: 
        messages.error(request, 'Activation link has expired or was invalid')
        return redirect('register')
    
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)
            # reset password email
            current_site = get_current_site(request)
            mail_subject = 'Please reset your password!'
            message = render_to_string('accounts/account_forgotpassword_email.html',{
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message, to=[to_email])
            send_email.send()
            messages.success(request,'Password reset email has been sent to your email address')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist! Please register')
            return redirect('register')
    return render(request,'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError,ValueError, OverflowError, Account.DoesNotExist):
        user = None 
    
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']= uid
        messages.success(request,'Please reset your password')
        return redirect('resetPassword')
    else: 
        messages.error(request,'This link has expired!')
        return redirect('forgotPassword')
    
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password: 
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('login')
        else: 
            messages.error(request, 'Passwords do not match! Please try again')
            return redirect('resetPassword')
    else: 
        return render(request,'accounts/resetPassword.html')

