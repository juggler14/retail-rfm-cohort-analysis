"""Конвертирует исходный Excel (2 листа: 2009–2010 и 2010–2011) в один CSV для загрузки в PostgreSQL."""
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"

sheets = pd.read_excel(DATA / "online_retail_II.xlsx", sheet_name=None, dtype={"Invoice": str, "StockCode": str})
df = pd.concat(sheets.values(), ignore_index=True)
df.columns = ["invoice", "stock_code", "description", "quantity", "invoice_date", "price", "customer_id", "country"]
df["customer_id"] = df["customer_id"].astype("Int64")
df.to_csv(DATA / "online_retail_ii.csv", index=False)
print(f"rows: {len(df):,}; period: {df.invoice_date.min()} — {df.invoice_date.max()}")
