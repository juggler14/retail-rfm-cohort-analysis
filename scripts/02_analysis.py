"""Выполняет SQL-запросы из папки sql/, сохраняет результаты, графики и ключевые цифры для README."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import psycopg
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
SQL, OUT, FIG = ROOT / "sql", ROOT / "reports", ROOT / "reports" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
DSN = "host=localhost dbname=retail user=retail_analyst"  # пароль берётся из ~/.pgpass

sns.set_theme(style="whitegrid", font_scale=1.0)
NAVY, ACCENT = "#1f3a5f", "#e07a1f"


def query(name: str) -> pd.DataFrame:
    with psycopg.connect(DSN) as conn:
        return pd.read_sql((SQL / name).read_text(), conn)


import warnings
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")

kpi = query("02_monthly_kpi.sql")
cohorts = query("03_cohort_retention.sql")
rfm = query("04_rfm_segments.sql")
pareto = query("05_pareto_ltv.sql")
for name, df in {"monthly_kpi": kpi, "cohort_retention": cohorts, "rfm_segments": rfm}.items():
    df.to_csv(OUT / f"{name}.csv", index=False)

# --- 1. Помесячная выручка и декомпозиция -----------------------------------------
kpi["month"] = pd.to_datetime(kpi["month"])
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.bar(kpi["month"], kpi["revenue"] / 1e3, width=20, color=NAVY)
ax.set_title("Выручка пикует в ноябре: сезонность сильнее, чем рост год к году", loc="left", fontweight="bold")
ax.set_ylabel("Выручка, тыс. £")
fig.tight_layout(); fig.savefig(FIG / "monthly_revenue.png", dpi=150); plt.close(fig)

# --- 2. Тепловая карта когорт ---------------------------------------------------
heat = (cohorts.assign(cohort=pd.to_datetime(cohorts["cohort_month"]).dt.strftime("%Y-%m"))
        .pivot(index="cohort", columns="month_number", values="retention_pct"))
heat = heat.loc[:, 0:12]
fig, ax = plt.subplots(figsize=(11, 8))
sns.heatmap(heat, annot=True, fmt=".0f", cmap="Blues", cbar_kws={"label": "Retention, %"}, ax=ax,
            annot_kws={"size": 7})
ax.grid(False)
ax.set_title("Retention по когортам (% клиентов когорты, купивших снова через N месяцев)", loc="left", fontweight="bold")
ax.set_xlabel("Месяцев с первой покупки"); ax.set_ylabel("Когорта (месяц первой покупки)")
fig.tight_layout(); fig.savefig(FIG / "cohort_retention.png", dpi=150); plt.close(fig)

# средний retention, взвешенный по размеру когорты (учитываем только когорты, которые «дожили» до месяца N)
# Когорта 2009-12 «левоцензурирована»: данные начинаются с декабря 2009, поэтому в неё попали все клиенты,
# покупавшие и раньше, и её retention завышен. Для средних значений берём когорты с 2010-01.
clean_cohorts = cohorts[pd.to_datetime(cohorts["cohort_month"]) >= "2010-01-01"]
weighted = (clean_cohorts.assign(w=clean_cohorts["retention_pct"] * clean_cohorts["cohort_size"])
            .groupby("month_number").agg(w=("w", "sum"), n=("cohort_size", "sum")))
avg_ret = (weighted["w"] / weighted["n"]).round(1)

# --- 3. RFM-сегменты ------------------------------------------------------------
seg = (rfm.groupby("segment")
       .agg(customers=("customer_id", "count"), revenue=("monetary", "sum"),
            avg_recency=("recency_days", "mean"), avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"))
       .assign(customer_share=lambda d: 100 * d.customers / d.customers.sum(),
               revenue_share=lambda d: 100 * d.revenue / d.revenue.sum())
       .sort_values("revenue", ascending=False).round(1))
seg.to_csv(OUT / "rfm_segment_summary.csv")

fig, ax = plt.subplots(figsize=(10, 4.5))
x = range(len(seg))
ax.bar([i - 0.2 for i in x], seg["customer_share"], width=0.4, color="#9fb3c8", label="Доля клиентов, %")
ax.bar([i + 0.2 for i in x], seg["revenue_share"], width=0.4, color=NAVY, label="Доля выручки, %")
ax.set_xticks(list(x)); ax.set_xticklabels(seg.index, rotation=20, ha="right")
ch = seg.loc["Champions"]
ax.set_title(f"Champions: {ch.customer_share:.0f}% клиентов приносят {ch.revenue_share:.0f}% выручки", loc="left", fontweight="bold")
ax.legend(); fig.tight_layout(); fig.savefig(FIG / "rfm_segments.png", dpi=150); plt.close(fig)

# --- 4. Кривая Парето -----------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(pareto["customer_share_pct"], pareto["cum_revenue_share_pct"], color=NAVY, lw=2)
top20 = pareto.loc[pareto["customer_share_pct"] <= 20, "cum_revenue_share_pct"].max()
ax.axvline(20, color=ACCENT, ls="--"); ax.axhline(top20, color=ACCENT, ls="--")
ax.set_xlabel("Доля клиентов (по убыванию выручки), %"); ax.set_ylabel("Накопленная доля выручки, %")
ax.set_title(f"Топ-20% клиентов дают {top20:.0f}% выручки", loc="left", fontweight="bold")
fig.tight_layout(); fig.savefig(FIG / "pareto.png", dpi=150); plt.close(fig)

# --- Ключевые цифры -------------------------------------------------------------
one_time = 100 * (rfm["frequency"] == 1).mean()
k2010 = kpi[kpi["month"].dt.year == 2010]; k2011 = kpi[(kpi["month"].dt.year == 2011)]
ytd10 = k2010[k2010["month"].dt.month <= 11]["revenue"].sum()
ytd11 = k2011[k2011["month"].dt.month <= 11]["revenue"].sum()
metrics = {
    "top20_revenue_share": round(float(top20), 1),
    "top1_revenue_share": round(float(pareto.loc[pareto["customer_share_pct"] <= 1, "cum_revenue_share_pct"].max()), 1),
    "retention_m1": float(avg_ret.get(1)), "retention_m3": float(avg_ret.get(3)),
    "retention_m6": float(avg_ret.get(6)), "retention_m12": float(avg_ret.get(12)),
    "one_time_buyers_pct": round(float(one_time), 1),
    "customers": int(len(rfm)),
    "revenue_jan_nov_2011_vs_2010_pct": round(100 * (ytd11 / ytd10 - 1), 1),
    "nov_share_of_2011": round(float(100 * k2011.loc[k2011["month"].dt.month == 11, "revenue"].sum() / k2011["revenue"].sum()), 1),
    "segments": seg[["customers", "customer_share", "revenue_share", "avg_recency", "avg_frequency", "avg_monetary"]].to_dict("index"),
}
(OUT / "key_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2))
print(json.dumps(metrics, ensure_ascii=False, indent=2))
print(kpi.to_string())
