-- Концентрация выручки (Парето): какая доля клиентов даёт какую долю выручки.
WITH customer_revenue AS (
    SELECT customer_id, SUM(revenue) AS revenue
    FROM sales
    GROUP BY customer_id
),
ranked AS (
    SELECT customer_id,
           revenue,
           ROW_NUMBER() OVER (ORDER BY revenue DESC)                     AS rnk,
           COUNT(*)     OVER ()                                          AS n_customers,
           SUM(revenue) OVER (ORDER BY revenue DESC
                              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_revenue,
           SUM(revenue) OVER ()                                          AS total_revenue
    FROM customer_revenue
)
SELECT customer_id,
       ROUND(revenue, 2)                                   AS revenue,
       ROUND(100.0 * rnk / n_customers, 2)                 AS customer_share_pct,
       ROUND(100.0 * cum_revenue / total_revenue, 2)       AS cum_revenue_share_pct
FROM ranked
ORDER BY rnk;
