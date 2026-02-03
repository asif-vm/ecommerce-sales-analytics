SELECT
    order_month,
    monthly_revenue,
    ROUND(SUM(monthly_revenue) OVER (ORDER BY order_month ROWS UNBOUNDED PRECEDING), 2) AS cumulative_revenue
FROM (
    SELECT
        DATE_FORMAT(o.order_date, '%Y-%m') AS order_month,
        ROUND(SUM(p.price * oi.quantity * (1 - oi.discount_percent / 100)), 2) AS monthly_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status = 'Delivered'
    GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
) AS monthly
ORDER BY order_month;