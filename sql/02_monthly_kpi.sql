-- Помесячные KPI: выручка = клиенты × заказов на клиента × средний чек.
-- Декабрь 2011 неполный (данные до 9 декабря), исключаем.
WITH orders AS (
    SELECT invoice,
           customer_id,
           DATE_TRUNC('month', MIN(invoice_date))::date AS month,
           SUM(revenue)                                 AS order_revenue
    FROM sales
    GROUP BY invoice, customer_id
)
SELECT month,
       ROUND(SUM(order_revenue))                                        AS revenue,
       COUNT(*)                                                         AS orders,
       COUNT(DISTINCT customer_id)                                      AS customers,
       ROUND(SUM(order_revenue) / COUNT(*), 2)                          AS aov,
       ROUND(COUNT(*)::numeric / COUNT(DISTINCT customer_id), 2)        AS orders_per_customer,
       ROUND(100.0 * (SUM(order_revenue) / LAG(SUM(order_revenue), 12) OVER (ORDER BY month) - 1), 1) AS revenue_yoy_pct
FROM orders
WHERE month < '2011-12-01'
GROUP BY month
ORDER BY month;
