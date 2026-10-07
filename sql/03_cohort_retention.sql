-- Когортный анализ: когорта = месяц первой покупки клиента.
-- retention_pct = доля клиентов когорты, совершивших покупку через N месяцев после первой.
WITH customer_months AS (
    SELECT DISTINCT customer_id, DATE_TRUNC('month', invoice_date)::date AS month
    FROM sales
    WHERE invoice_date < '2011-12-01'
),
cohorts AS (
    SELECT customer_id,
           month,
           MIN(month) OVER (PARTITION BY customer_id) AS cohort_month
    FROM customer_months
),
cohort_activity AS (
    SELECT cohort_month,
           (EXTRACT(YEAR FROM AGE(month, cohort_month)) * 12
            + EXTRACT(MONTH FROM AGE(month, cohort_month)))::int AS month_number,
           COUNT(DISTINCT customer_id)                           AS active_customers
    FROM cohorts
    GROUP BY 1, 2
)
SELECT cohort_month,
       month_number,
       active_customers,
       FIRST_VALUE(active_customers) OVER w                                   AS cohort_size,
       ROUND(100.0 * active_customers / FIRST_VALUE(active_customers) OVER w, 1) AS retention_pct
FROM cohort_activity
WINDOW w AS (PARTITION BY cohort_month ORDER BY month_number)
ORDER BY cohort_month, month_number;
