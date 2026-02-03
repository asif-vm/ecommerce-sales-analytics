SELECT
    reason,
    COUNT(*) AS return_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM returns), 2) AS percentage
FROM returns
GROUP BY reason
ORDER BY return_count DESC;