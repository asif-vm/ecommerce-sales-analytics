SELECT
    YEAR(o.order_date) AS order_year,
    MONTH(o.order_date) AS order_month,
    ROUND(SUM(p.price * oi.quantity * (1 - oi.discount_percent / 100)), 2) AS monthly_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY YEAR(o.order_date), MONTH(o.order_date)
ORDER BY order_year, order_month;