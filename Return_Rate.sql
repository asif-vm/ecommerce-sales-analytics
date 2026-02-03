SELECT
    p.category,
    COUNT(oi.order_item_id) AS total_items_sold,
    COUNT(r.return_id) AS total_returns,
    ROUND(COUNT(r.return_id) * 100.0 / COUNT(oi.order_item_id), 2) AS return_rate_percent
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN returns r ON oi.order_item_id = r.order_item_id
WHERE o.status = 'Delivered'
GROUP BY p.category
ORDER BY return_rate_percent DESC;