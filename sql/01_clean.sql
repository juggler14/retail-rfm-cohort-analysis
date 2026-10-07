-- Очистка: оставляем только реальные покупки идентифицированных клиентов.
DROP TABLE IF EXISTS sales CASCADE;
CREATE TABLE sales AS
SELECT DISTINCT                                   -- в исходных данных есть полные дубликаты строк
       invoice,
       stock_code,
       description,
       quantity,
       invoice_date,
       price,
       customer_id,
       country,
       quantity * price AS revenue
FROM raw_transactions
WHERE customer_id IS NOT NULL                     -- без ID клиента нельзя строить когорты и RFM
  AND invoice NOT LIKE 'C%'                       -- 'C' в номере = отмена заказа
  AND quantity > 0
  AND price > 0
  AND stock_code NOT IN ('POST', 'DOT', 'M', 'C2', 'D', 'S', 'B', 'BANK CHARGES',
                         'AMAZONFEE', 'ADJUST', 'ADJUST2', 'PADS', 'TEST001', 'TEST002', 'CRUK');  -- доставка, комиссии, корректировки

CREATE INDEX ON sales (customer_id);
CREATE INDEX ON sales (invoice_date);

-- Контроль качества: сколько строк и выручки отсеяли
SELECT (SELECT COUNT(*) FROM raw_transactions)                    AS raw_rows,
       (SELECT COUNT(*) FROM sales)                               AS clean_rows,
       (SELECT COUNT(DISTINCT customer_id) FROM sales)            AS customers,
       (SELECT COUNT(DISTINCT invoice) FROM sales)                AS orders,
       (SELECT ROUND(SUM(revenue)) FROM sales)                    AS revenue;
