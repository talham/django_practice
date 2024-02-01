from django import forms 
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name',  'email','phone', 'street_address', 'apt_address',
                  'city', 'state', 'zip_code','country', 'order_note']