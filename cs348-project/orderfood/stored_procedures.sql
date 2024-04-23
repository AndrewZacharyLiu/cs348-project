CREATE PROCEDURE CalculateTotalPrice(order_id INTEGER)
AS
BEGIN
    SELECT SUM(app_food.price) AS total_price
    FROM app_order
    JOIN app_orderjoinfood ON app_orderjoinfood.order_id = app_order.id
    JOIN app_food ON app_orderjoinfood.food_id = app_food.id
    WHERE app_order.id = order_id;
END;