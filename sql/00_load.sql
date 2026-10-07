-- Загрузка сырых данных. Запуск: psql -h localhost -U retail_analyst -d retail -f sql/00_load.sql
DROP TABLE IF EXISTS raw_transactions CASCADE;
CREATE TABLE raw_transactions (
    invoice      TEXT,
    stock_code   TEXT,
    description  TEXT,
    quantity     INTEGER,
    invoice_date TIMESTAMP,
    price        NUMERIC(10, 2),
    customer_id  INTEGER,
    country      TEXT
);
\copy raw_transactions FROM 'data/online_retail_ii.csv' WITH (FORMAT csv, HEADER true)
SELECT COUNT(*) AS loaded_rows FROM raw_transactions;
