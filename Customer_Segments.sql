SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(total_spent), 2) AS avg_spend
FROM (
    SELECT
        c.customer_id,
        ROUND(SUM(p.price * oi.quantity * (1 - oi.discount_percent / 100)), 2) AS total_spent,
        CASE
            WHEN SUM(p.price * oi.quantity * (1 - oi.discount_percent / 100)) >= 20000 THEN 'High Value'
            WHEN SUM(p.price * oi.quantity * (1 - oi.discount_percent / 100)) >= 8000 THEN 'Mid Value'
            ELSE 'Low Value'
        END AS segment
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id
) AS customer_segments
GROUP BY segment
ORDER BY avg_spend DESC;