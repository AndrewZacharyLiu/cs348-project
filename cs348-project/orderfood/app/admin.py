from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(Food)
admin.site.register(Order)
admin.site.register(MenuJoinFood)
admin.site.register(OrderJoinFood)