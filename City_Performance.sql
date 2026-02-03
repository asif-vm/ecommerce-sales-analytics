SELECT
    c.city,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_id) AS unique_customers,
    ROUND(SUM(p.price * oi.quantity * (1 - oi.discount_percent / 100)), 2) AS total_revenue,
    ROUND(SUM(p.price * oi.quantity * (1 - oi.discount_percent / 100)) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.status = 'Delivered'
GROUP BY c.city
ORDER BY total_revenue DESC;