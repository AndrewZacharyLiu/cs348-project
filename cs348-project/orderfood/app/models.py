from django.db import models

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    menu_name = models.CharField(max_length=100)
    class Meta:
        indexes = [
            models.Index(fields=['restaurant_id'])
        ]

class Food(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class Order(models.Model):
    time_placed = models.DateTimeField()
    delivery_time = models.DateTimeField()
    delivery_location = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=['time_placed'])
        ]

class MenuJoinFood(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)

class OrderJoinFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)