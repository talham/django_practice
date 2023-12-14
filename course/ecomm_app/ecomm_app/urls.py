"""ecomm_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from greatkart import views
from store import views as store_views
from carts import views as carts_views
from django.conf.urls.static import static 
from django.conf import settings 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name='home'),
    path('store/',store_views.store, name='store'),
    path('store/category/<slug:category_slug>/',store_views.store,name='products_by_category'),
    path('store/category/<slug:category_slug>/<slug:product_slug>/',store_views.product_detail,name='product_detail'),
    path('store/search/', store_views.search, name='search'),
    path('cart/', carts_views.cart, name='cart'),
    path('cart/add_cart/<int:product_id>/', carts_views.add_cart,name='add_cart'),
    path('cart/remove_cart/<int:product_id>/<int:cart_item_id>', carts_views.remove_cart, name='remove_cart'),
    path('cart/remove_cart_product/<int:product_id>/<int:cart_item_id>', carts_views.remove_cart_product, name='remove_cart_product'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
