#!/usr/bin/env bash
# Создаёт в локальном PostgreSQL базу retail и пользователя retail_analyst.
# Пароли вводятся вручную и сохраняются только в ~/.pgpass (права 600), чтобы скрипты подключались без ввода пароля.
set -euo pipefail
PSQL=/Library/PostgreSQL/17/bin/psql

read -rsp "Придумайте пароль для нового пользователя retail_analyst: " APP_PW; echo
echo "Сейчас psql попросит пароль суперпользователя postgres (тот, что задавали при установке PostgreSQL)."
"$PSQL" -h localhost -U postgres -v ON_ERROR_STOP=1 -v pw="$APP_PW" <<'SQL'
SELECT 'CREATE ROLE retail_analyst LOGIN' WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'retail_analyst') \gexec
ALTER ROLE retail_analyst PASSWORD :'pw';
SELECT 'CREATE DATABASE retail OWNER retail_analyst' WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'retail') \gexec
SQL

touch ~/.pgpass && chmod 600 ~/.pgpass
grep -v '^localhost:5432:retail:retail_analyst:' ~/.pgpass > ~/.pgpass.tmp || true
echo "localhost:5432:retail:retail_analyst:${APP_PW}" >> ~/.pgpass.tmp
mv ~/.pgpass.tmp ~/.pgpass && chmod 600 ~/.pgpass
"$PSQL" -h localhost -U retail_analyst -d retail -c "SELECT 'Готово: подключение к retail работает' AS status;"
