"""Интерактивный HTML-дашборд (Plotly) по результатам SQL-анализа: reports/dashboard.html."""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

OUT = Path(__file__).resolve().parents[1] / "reports"
kpi = pd.read_csv(OUT / "monthly_kpi.csv", parse_dates=["month"])
coh = pd.read_csv(OUT / "cohort_retention.csv")
seg = pd.read_csv(OUT / "rfm_segment_summary.csv")
NAVY, LIGHT = "#1f3a5f", "#9fb3c8"

fig = make_subplots(
    rows=3, cols=2, row_heights=[0.28, 0.42, 0.30], vertical_spacing=0.09,
    specs=[[{"colspan": 2}, None], [{"colspan": 2}, None], [{}, {}]],
    subplot_titles=("Выручка по месяцам, £", "Retention по когортам, %",
                    "Доля клиентов и выручки по RFM-сегментам, %", "Средний чек по месяцам, £"),
)
fig.add_bar(x=kpi.month, y=kpi.revenue, marker_color=NAVY, name="Выручка",
            customdata=kpi[["orders", "customers", "aov"]],
            hovertemplate="%{x|%b %Y}<br>Выручка: £%{y:,.0f}<br>Заказы: %{customdata[0]:,}"
                          "<br>Клиенты: %{customdata[1]:,}<br>Средний чек: £%{customdata[2]:.0f}<extra></extra>",
            row=1, col=1)
heat = coh[coh.month_number <= 12].pivot(index="cohort_month", columns="month_number", values="retention_pct")
heat.index = pd.to_datetime(heat.index).strftime("%Y-%m")
labels = heat.map(lambda v: "" if pd.isna(v) else f"{v:.0f}")
fig.add_heatmap(z=heat.values, x=heat.columns, y=heat.index, colorscale="Blues", zmax=50, showscale=False,
                text=labels.values, texttemplate="%{text}", textfont={"size": 9},
                hovertemplate="Когорта %{y}<br>Месяц %{x}: %{z:.1f}%<extra></extra>", row=2, col=1)
fig.update_yaxes(autorange="reversed", type="category", row=2, col=1)
fig.update_xaxes(dtick=1, row=2, col=1)
fig.add_bar(x=seg.segment, y=seg.customer_share, name="Доля клиентов", marker_color=LIGHT, row=3, col=1)
fig.add_bar(x=seg.segment, y=seg.revenue_share, name="Доля выручки", marker_color=NAVY, row=3, col=1)
fig.add_scatter(x=kpi.month, y=kpi.aov, mode="lines+markers", line_color=NAVY, name="Средний чек", row=3, col=2)
fig.update_layout(title="Online Retail II: выручка, удержание и RFM-сегменты (дек 2009 — ноя 2011)",
                  height=1250, template="plotly_white", barmode="group", showlegend=False,
                  font_family="Arial", margin=dict(t=90, l=60, r=30, b=40))
fig.write_html(OUT / "dashboard.html", include_plotlyjs="cdn")
print("saved", OUT / "dashboard.html")
