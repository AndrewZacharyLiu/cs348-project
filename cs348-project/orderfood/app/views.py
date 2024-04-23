from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db import transaction
from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from django.http import Http404
# Create your views here.
from .models import *
import sqlite3
def calculate_food_report(start_datetime, end_datetime):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    try:
        # Define the SQL query
        sql_query = """
        SELECT app_food.name, COUNT(app_order.id) AS order_count
        FROM app_food
        LEFT JOIN app_orderjoinfood ON app_food.id = app_orderjoinfood.food_id
        LEFT JOIN app_order ON app_orderjoinfood.order_id = app_order.id
        WHERE app_order.time_placed >= ? AND app_order.time_placed <= ?
        GROUP BY app_food.id
        """

    # Execute the query with parameters
        cursor.execute(sql_query, (start_datetime, end_datetime))
        # Fetch all the results
        rows = cursor.fetchall()
        print(rows)
        # Create a list to store the results
        report_data = []
        for row in rows:
            food_name = row[0]
            order_count = row[1]
            report_data.append((food_name, order_count))

        return report_data
    finally:
        # Close the database connection
        conn.close()
def report(request):
    start_datetime = request.GET.get('start_datetime')
    end_datetime = request.GET.get('end_datetime')
    if start_datetime is None or start_datetime == '':
        # Default start_datetime to last week
        start_datetime = str(datetime.now() - timedelta(weeks=1))
        
    if end_datetime is None or end_datetime == '':
        # Default end_datetime to now
        end_datetime = str(datetime.now())
  
    report_data = calculate_food_report(start_datetime, end_datetime )
    
    return render(request, 'report.html', {'report_data': report_data, 'start_datetime': start_datetime, 'end_datetime': end_datetime})
    # Connect to the SQLite database
    

def calculate_total_price(order_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    try:
        # Define the SQL query with a placeholder for the order_id parameter
        sql_query = """
        SELECT SUM(app_food.price) AS total_price
        FROM app_order
        JOIN app_orderjoinfood ON app_orderjoinfood.order_id = app_order.id
        JOIN app_food ON app_orderjoinfood.food_id = app_food.id
        WHERE app_order.id = ?
        """
        ''''''

        # Execute the prepared statement with the order_id parameter
        cursor.execute(sql_query, (order_id,))

        # Fetch the result
        row = cursor.fetchone()
        if row:
            total_price = row[0]
            return total_price
        else:
            return None
    finally:
        # Close the database connection
        conn.close()
@transaction.atomic
def edit_order(request):
    order_id = request.POST.get('order_id')
    print(order_id + " is order_id")
    order = get_object_or_404(Order, id=order_id)
    total_price = calculate_total_price(order.id)
    order_info = {
            'order': order,
            'foods': OrderJoinFood.objects.filter(order=order),
            'total_price': total_price
        }
    return render(request, 'order_edit.html', {'order_info': order_info})

def edit_order_submit(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        
        # Update delivery_location and delivery_time
        order.delivery_location = request.POST.get('delivery_location')
        order.delivery_time = request.POST.get('delivery_time')
        order.save()
        
        messages.success(request, 'Order details updated successfully.')
        return redirect('order_history')
    else:
        # Handle invalid request method
        messages.error(request, 'Invalid request method.')
        return redirect('order_history')  # Redirect to order history or appropriate page

@csrf_protect
@transaction.atomic
def delete_order(request):
    order_id = request.POST.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Delete the order
        order.delete()
        messages.success(request, 'Order deleted successfully.')
        return redirect('order_history')
    
    return render(request, 'delete_order.html', {'order': order})

def order_history(request):
    # Retrieve order IDs stored in the session
    order_ids = request.session.get('order_ids', [])
    print(order_ids)
    
    # Retrieve order details based on the order IDs
    orders = Order.objects.filter(id__in=order_ids)
    
    # Create a dictionary to store order details along with associated food items and total price
    order_details = []
    for order in orders:
        # Retrieve associated food items
        foods = OrderJoinFood.objects.filter(order=order)
        
        # Calculate total price for the order using the calculate_total_price function
        total_price = calculate_total_price(order.id)
        print(str(total_price) + " is total_price")
        
        # Create a dictionary to store order info, food items, and total price
        order_info = {
            'order': order,
            'foods': foods,
            'total_price': total_price
        }
        order_details.append(order_info)
    
    return render(request, 'order_history.html', {'order_details': order_details})

@transaction.atomic
def place_order(request):
    if request.method == 'POST':
        # Retrieve form data
        delivery_time = request.POST.get('delivery_time')
        delivery_location = request.POST.get('delivery_location')
        
        # Create a new Order instance
        order = Order.objects.create(
            time_placed=timezone.now(),
            delivery_time=delivery_time,
            delivery_location=delivery_location
        )
        
        # Retrieve food items stored in the session
        food_ids = request.session.get('order_items', [])
        
        # Create OrderJoinFood instances for each food item
        for food_id in food_ids:
            food = Food.objects.get(id=food_id)
            OrderJoinFood.objects.create(order=order, food=food)
        
        # Store the order ID in the session for future reference
        if 'order_ids' in request.session:
            request.session['order_ids'].append(order.id)
        else:
            request.session['order_ids'] = [order.id]
        
        
        # Clear the order items from the session
        del request.session['order_items']
        
        return redirect('order_confirmation')  # You should define 'order_confirmation' URL pattern
    else:
        return redirect('view_order')  # Redirect to view_order if the request method is not POST
    
def add_to_cart(request):
    # Get the food item
    food_id = request.GET.get('food_id')
    print(food_id + " is food_id")
    food = get_object_or_404(Food, id=food_id)
    # Create or retrieve the order associated with the session
    if 'order_items' not in request.session:
        request.session['order_items'] = []
    order_items = request.session['order_items']
    
    # Add the food item to the order
    request.session['order_items'].append(food_id)
    request.session.modified = True  # Mark the session as modified
    
    # Return a JSON response indicating success
    return JsonResponse({'message': 'Food item has been successfully added to the cart.'})

def view_order(request):
    # Retrieve the food item IDs stored in the session
    food_ids = request.session.get('order_items', [])
    
    # Retrieve the Food objects corresponding to the food IDs
    order_items = Food.objects.filter(id__in=food_ids)
    
    # Display the order
    return render(request, 'order_detail.html', {'order_items': order_items})


def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurant_list.html', {'restaurants': restaurants})
def menu_detail(request):
    # Retrieve the menu object
    menu_id = request.GET.get('menu_id')
    menu = get_object_or_404(Menu, pk=menu_id)
    print(menu)
    # Retrieve all food items associated with this menu
    foods_ids = MenuJoinFood.objects.filter(menu_id=menu_id).values_list('food_id', flat=True)
    print(foods_ids)
    foods = Food.objects.filter(id__in=foods_ids)
    print(foods)
    
    return render(request, 'menu_detail.html', {'menu': menu, 'foods': foods})

def menu_list(request):
    restaurant_id = request.GET.get('restaurant_id')
    if restaurant_id:
        # Retrieve menus for the specified restaurant
        menus = Menu.objects.filter(restaurant_id=restaurant_id).select_related('restaurant')
        return render(request, 'menu_list.html', {'menus': menus, 'restaurant' : menus[0].restaurant})
    else:
        # Handle case where restaurant_id is not provided
        # For example, display all menus from all restaurants
        menus = Menu.objects.all().select_related('restaurant')
        return render(request, 'menu_listall.html', {'menus': menus})