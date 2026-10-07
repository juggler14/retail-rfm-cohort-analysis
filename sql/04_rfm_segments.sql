-- RFM-сегментация на дату анализа 2011-12-10 (день после последней транзакции).
-- R, F, M оцениваются квинтилями 1–5 (5 = лучший).
WITH customer_stats AS (
    SELECT customer_id,
           ('2011-12-10'::date - MAX(invoice_date)::date) AS recency_days,
           COUNT(DISTINCT invoice)                         AS frequency,
           SUM(revenue)                                    AS monetary
    FROM sales
    GROUP BY customer_id
),
scored AS (
    SELECT *,
           NTILE(5) OVER (ORDER BY recency_days DESC) AS r,   -- недавние покупатели получают 5
           NTILE(5) OVER (ORDER BY frequency)         AS f,
           NTILE(5) OVER (ORDER BY monetary)          AS m
    FROM customer_stats
)
SELECT customer_id, recency_days, frequency, ROUND(monetary, 2) AS monetary, r, f, m,
       CASE
           WHEN r >= 4 AND f >= 4                 THEN 'Champions'
           WHEN r >= 3 AND f >= 3                 THEN 'Loyal'
           WHEN r >= 4 AND f <= 2                 THEN 'New / Promising'
           WHEN r = 3  AND f <= 2                 THEN 'Need attention'
           WHEN r <= 2 AND f >= 4                 THEN 'Can''t lose them'
           WHEN r <= 2 AND f = 3                  THEN 'At risk'
           ELSE                                        'Hibernating'
       END AS segment
FROM scored;
