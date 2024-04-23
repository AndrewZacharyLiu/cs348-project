"""orderfood URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from app.views import *
from django.views.generic.base import TemplateView

urlpatterns = [
    path("", restaurant_list, name="home"),
    path('admin/', admin.site.urls),
    path('restaurants/', restaurant_list, name='restaurant_list'),
    path('menus_detail/', menu_detail, name='menu_detail'),
    path('menus/', menu_list, name='menu_list'),
    path('add_to_cart/', add_to_cart, name='add_to_cart'),
    path('view_order/', view_order, name='view_order'),
    path('place_order/', place_order, name='place_order'),
    path('order_history/', order_history, name='order_history'),
    path('edit_order/', edit_order, name='edit_order'),
    path('edit_order_submit/', edit_order_submit, name='edit_order_submit'),
    path('delete_order/', delete_order, name='delete_order'),
    path('order_confirmation/',  TemplateView.as_view(template_name="order_confirmation.html"), name='order_confirmation'),
    path('report/', report, name='report'),
]
