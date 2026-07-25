from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
PRIVATE_XLSX = APP_DIR / "private_input" / "India_HVAC_Market_Prioritisation_Dashboard.xlsx"
PRODUCTS_CSV = APP_DIR / "data" / "carrier_products_public.csv"
DEMO_CSV = APP_DIR / "data" / "market_demo.csv"

st.set_page_config(
    page_title="Carrier HVAC Market Prioritisation",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
      [data-testid="stMetric"] {
        border: 1px solid #d9e2ec;
        border-radius: 12px;
        padding: 0.75rem 0.9rem;
        background: #ffffff;
      }
      .section-card {
        border: 1px solid #d9e2ec;
        border-radius: 12px;
        padding: 1rem;
        background: #ffffff;
        margin-bottom: 0.75rem;
      }
      .small-muted {color: #52606d; font-size: 0.88rem;}
      .source-note {
        border-left: 4px solid #1f6f8b;
        background: #f5f9fb;
        padding: 0.75rem 1rem;
        border-radius: 4px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_products() -> pd.DataFrame:
    return pd.read_csv(PRODUCTS_CSV)


@st.cache_data
def load_demo_data() -> pd.DataFrame:
    df = pd.read_csv(DEMO_CSV)
    return df


def read_private_workbook(source: str | Path | BinaryIO) -> pd.DataFrame:
    """Read the Market Data sheet created in the companion Excel model."""
    raw = pd.read_excel(source, sheet_name="Market Data", header=3, usecols="A:M")
    raw = raw.iloc[:6].copy()
    raw.columns = [
        "Product Category",
        "2024 Value",
        "2025 Value",
        "2026 Value",
        "Annual Change",
        "Absolute Growth",
        "2026 Market Share",
        "Market Size Score",
        "Growth Score",
        "Energy Relevance",
        "Opportunity Score",
        "Priority Rank",
        "Scoring Rationale",
    ]
    numeric_cols = [
        "2024 Value",
        "2025 Value",
        "2026 Value",
        "Annual Change",
        "Absolute Growth",
        "2026 Market Share",
        "Market Size Score",
        "Growth Score",
        "Energy Relevance",
        "Opportunity Score",
        "Priority Rank",
    ]
    for col in numeric_cols:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    return raw.dropna(subset=["Product Category", "2026 Value"]).reset_index(drop=True)


def minmax_score(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce").fillna(0.0)
    spread = series.max() - series.min()
    if spread == 0:
        return pd.Series(np.full(len(series), 3.0), index=series.index)
    return 1.0 + 4.0 * (series - series.min()) / spread


def calculate_scores(
    df: pd.DataFrame,
    size_weight: float,
    growth_weight: float,
    energy_weight: float,
) -> pd.DataFrame:
    out = df.copy()
    out["Market Size Score"] = minmax_score(out["2026 Value"])
    out["Growth Score"] = minmax_score(out["Annual Change"])
    out["Energy Relevance"] = pd.to_numeric(out["Energy Relevance"], errors="coerce").fillna(3.0)

    weight_sum = size_weight + growth_weight + energy_weight
    if weight_sum <= 0:
        size_weight, growth_weight, energy_weight, weight_sum = 0.4, 0.35, 0.25, 1.0

    out["Opportunity Score"] = (
        out["Market Size Score"] * size_weight
        + out["Growth Score"] * growth_weight
        + out["Energy Relevance"] * energy_weight
    ) / weight_sum
    out["Priority Rank"] = out["Opportunity Score"].rank(method="dense", ascending=False).astype(int)
    return out.sort_values(["Priority Rank", "Product Category"]).reset_index(drop=True)


def format_market_value(value: float, is_demo: bool) -> str:
    if is_demo:
        return f"{value:,.0f} index"
    return f"USD {value:,.1f} mn"


products = load_products()

st.sidebar.title("Analysis controls")
mode = st.sidebar.radio(
    "Data mode",
    ["Public portfolio demo", "Private BSRIA analysis"],
    help=(
        "Use the public demo for GitHub/Streamlit Cloud. Use private mode locally with the supplied Excel workbook."
    ),
)

uploaded_file = None
private_source_label = ""
if mode == "Private BSRIA analysis":
    uploaded_file = st.sidebar.file_uploader(
        "Upload the private Excel model",
        type=["xlsx"],
        help="The file is processed in the current session and is not included in the public repository.",
    )

size_weight = st.sidebar.slider("Market size weight", 0, 100, 40, 5) / 100
growth_weight = st.sidebar.slider("Growth weight", 0, 100, 35, 5) / 100
energy_weight = st.sidebar.slider("Energy-efficiency weight", 0, 100, 25, 5) / 100

if mode == "Private BSRIA analysis":
    try:
        if uploaded_file is not None:
            market_df = read_private_workbook(uploaded_file)
            private_source_label = "uploaded private workbook"
        elif PRIVATE_XLSX.exists():
            market_df = read_private_workbook(PRIVATE_XLSX)
            private_source_label = "local private workbook"
        else:
            st.warning(
                "Private mode is selected, but no workbook is available. Upload the Excel file or place it in "
                "private_input/India_HVAC_Market_Prioritisation_Dashboard.xlsx. Showing demo data instead."
            )
            market_df = load_demo_data()
            mode = "Public portfolio demo"
    except Exception as exc:
        st.error(f"The workbook could not be read: {exc}")
        market_df = load_demo_data()
        mode = "Public portfolio demo"
else:
    market_df = load_demo_data()

is_demo = mode == "Public portfolio demo"
market_df = calculate_scores(market_df, size_weight, growth_weight, energy_weight)

st.title("India HVAC Market & Carrier Portfolio Prioritisation")
st.caption(
    "A decision-support dashboard linking HVAC market attractiveness, energy-efficiency relevance, "
    "Carrier's public product portfolio, and supply-chain implications."
)

if is_demo:
    st.info(
        "Public demo mode uses illustrative indexed data. It is suitable for GitHub and Streamlit Cloud. "
        "Use private mode locally to analyse the BSRIA-based Excel model."
    )
else:
    st.warning(
        f"Private analysis mode is using the {private_source_label}. Do not publish proprietary values or report extracts."
    )

overview_tab, priority_tab, portfolio_tab, operations_tab, methodology_tab = st.tabs(
    [
        "Executive overview",
        "Market prioritisation",
        "Carrier product explorer",
        "Energy & supply chain",
        "Methodology & sources",
    ]
)

with overview_tab:
    top_row = market_df.sort_values("Priority Rank").iloc[0]
    growth_row = market_df.loc[market_df["Annual Change"].idxmax()]
    size_row = market_df.loc[market_df["2026 Value"].idxmax()]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Top opportunity", top_row["Product Category"], f"Score {top_row['Opportunity Score']:.2f}/5")
    c2.metric("Fastest growth", growth_row["Product Category"], f"{growth_row['Annual Change']:.1%}")
    c3.metric("Largest 2026 segment", size_row["Product Category"], format_market_value(size_row["2026 Value"], is_demo))
    c4.metric("Carrier categories mapped", f"{products['Portfolio Category'].nunique()}", "public product families")

    year_df = market_df.melt(
        id_vars="Product Category",
        value_vars=["2024 Value", "2025 Value", "2026 Value"],
        var_name="Year",
        value_name="Market Value",
    )
    year_df["Year"] = year_df["Year"].str.extract(r"(2024|2025|2026)")
    fig = px.bar(
        year_df,
        x="Product Category",
        y="Market Value",
        color="Year",
        barmode="group",
        title="Market trajectory by HVAC category",
        labels={"Market Value": "Market index" if is_demo else "Market value (USD mn)"},
    )
    fig.update_layout(height=450, legend_title_text="Year", xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns([1.35, 1])
    with left:
        scatter = px.scatter(
            market_df,
            x="2026 Value",
            y="Annual Change",
            size="Energy Relevance",
            color="Opportunity Score",
            hover_name="Product Category",
            text="Product Category",
            size_max=45,
            title="Market size–growth opportunity matrix",
            labels={
                "2026 Value": "2026 market index" if is_demo else "2026F market value (USD mn)",
                "Annual Change": "Annual growth",
            },
        )
        scatter.update_traces(textposition="top center")
        scatter.update_yaxes(tickformat=".0%")
        scatter.update_layout(height=430)
        st.plotly_chart(scatter, use_container_width=True)

    with right:
        st.subheader("Decision summary")
        for _, row in market_df.sort_values("Priority Rank").head(3).iterrows():
            st.markdown(
                f"""
                <div class="section-card">
                  <strong>#{int(row['Priority Rank'])} {row['Product Category']}</strong><br>
                  <span class="small-muted">Opportunity score: {row['Opportunity Score']:.2f}/5 · "
                  Annual growth: {row['Annual Change']:.1%} · Energy relevance: {row['Energy Relevance']:.1f}/5</span><br>
                  {row.get('Scoring Rationale', '')}
                </div>
                """,
                unsafe_allow_html=True,
            )

with priority_tab:
    st.subheader("Adjustable prioritisation model")
    st.write(
        "The model recalculates category ranking using the three weights selected in the sidebar. "
        "This makes the assumptions visible rather than hard-coding a single answer."
    )

    rank_fig = px.bar(
        market_df.sort_values("Opportunity Score"),
        x="Opportunity Score",
        y="Product Category",
        orientation="h",
        text="Opportunity Score",
        title="Weighted opportunity ranking",
        hover_data=["Market Size Score", "Growth Score", "Energy Relevance", "Priority Rank"],
    )
    rank_fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    rank_fig.update_layout(height=430, xaxis_range=[0, 5.3])
    st.plotly_chart(rank_fig, use_container_width=True)

    display_cols = [
        "Priority Rank",
        "Product Category",
        "2024 Value",
        "2025 Value",
        "2026 Value",
        "Annual Change",
        "Market Size Score",
        "Growth Score",
        "Energy Relevance",
        "Opportunity Score",
        "Scoring Rationale",
    ]
    formatted = market_df[display_cols].copy()
    formatted["Annual Change"] = formatted["Annual Change"].map(lambda x: f"{x:.1%}")
    for col in ["Market Size Score", "Growth Score", "Energy Relevance", "Opportunity Score"]:
        formatted[col] = formatted[col].map(lambda x: f"{x:.2f}")
    st.dataframe(formatted, use_container_width=True, hide_index=True)

    st.download_button(
        "Download prioritisation results",
        market_df.to_csv(index=False).encode("utf-8"),
        file_name="hvac_prioritisation_results.csv",
        mime="text/csv",
    )

with portfolio_tab:
    st.subheader("Carrier product explorer")
    st.write(
        "The explorer maps publicly listed Carrier India product families and representative offerings to applications, "
        "energy features, and the corresponding market category."
    )

    filter_cols = st.columns(3)
    with filter_cols[0]:
        selected_portfolio = st.multiselect(
            "Portfolio category",
            sorted(products["Portfolio Category"].unique()),
        )
    with filter_cols[1]:
        selected_application = st.multiselect(
            "Application",
            sorted(products["Primary Application"].unique()),
        )
    with filter_cols[2]:
        selected_market = st.multiselect(
            "Mapped market category",
            sorted(products["Mapped Market Category"].unique()),
        )

    filtered = products.copy()
    if selected_portfolio:
        filtered = filtered[filtered["Portfolio Category"].isin(selected_portfolio)]
    if selected_application:
        filtered = filtered[filtered["Primary Application"].isin(selected_application)]
    if selected_market:
        filtered = filtered[filtered["Mapped Market Category"].isin(selected_market)]

    st.dataframe(
        filtered[
            [
                "Portfolio Category",
                "Representative Product / Offering",
                "Product Type",
                "Primary Application",
                "Energy / Controls Relevance",
                "India Manufacturing / Presence",
                "Mapped Market Category",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    coverage = (
        products.assign(Coverage=1)
        .pivot_table(
            index="Mapped Market Category",
            columns="Portfolio Category",
            values="Coverage",
            aggfunc="max",
            fill_value=0,
        )
        .sort_index()
    )
    heatmap = go.Figure(
        data=go.Heatmap(
            z=coverage.values,
            x=coverage.columns,
            y=coverage.index,
            colorscale=[[0, "#eef2f6"], [1, "#1f6f8b"]],
            showscale=False,
            hovertemplate="Market: %{y}<br>Carrier portfolio: %{x}<extra></extra>",
        )
    )
    heatmap.update_layout(title="Carrier portfolio coverage across market categories", height=430)
    st.plotly_chart(heatmap, use_container_width=True)

with operations_tab:
    st.subheader("Energy-efficiency and supply-chain implications")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="section-card">
              <strong>Public Carrier India operating footprint</strong><br><br>
              Carrier India states that its Gurugram facility includes automated manufacturing, R&D, and a quality clinic. "
              The facility manufactures products including cassettes, ducted splits, package units, screw and reciprocating "
              chillers, fan coils, and air handling units.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="section-card">
              <strong>Energy and controls lens</strong><br><br>
              Portfolio analysis should distinguish equipment efficiency from system efficiency. Chillers, VRF, AHUs, "
              controls, and fan-wall solutions can be assessed through part-load performance, variable-speed operation, "
              airflow control, filtration, monitoring, and building-management integration.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="section-card">
              <strong>Supply-chain questions generated by the model</strong><br><br>
              • Which high-growth categories need supplier-capacity expansion?<br>
              • Which components create import or lead-time exposure?<br>
              • Where do inverter, VFD, controls, sensor, or refrigerant transitions require supplier development?<br>
              • Which categories justify higher safety stock versus make-to-order planning?<br>
              • How should quality gates change for new energy-efficiency requirements?
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="section-card">
              <strong>Process-improvement applications</strong><br><br>
              The dashboard can support portfolio reviews, supplier scorecards, demand-planning discussions, localisation "
              roadmaps, and Six Sigma problem definition. A later version can add forecast error, inventory turns, supplier "
              on-time delivery, defect rates, and cost-of-poor-quality metrics.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Recommended next data layer")
    next_layer = pd.DataFrame(
        [
            ["Demand planning", "Monthly unit/value demand, forecast, actuals", "MAPE, bias, seasonality"],
            ["Inventory", "Opening stock, receipts, consumption, closing stock", "Days inventory, stockout rate, ageing"],
            ["Suppliers", "Lead time, quality rejects, price, delivery adherence", "OTD, PPM, PPV, risk score"],
            ["Manufacturing", "Cycle time, downtime, throughput, rework", "FPY, utilisation, bottleneck loss"],
            ["Energy", "kWh, cooling output, run hours, load profile", "kWh/TRh, COP/IPLV proxy, peak demand"],
        ],
        columns=["Module", "Required data", "Example KPIs"],
    )
    st.dataframe(next_layer, use_container_width=True, hide_index=True)

with methodology_tab:
    st.subheader("Methodology")
    st.markdown(
        """
        1. **Market attractiveness:** compare category size and growth.
        2. **Energy relevance:** assign a documented 1–5 score based on efficiency, controls, IAQ, and regulatory exposure.
        3. **Weighted prioritisation:** combine size, growth, and energy relevance using adjustable weights.
        4. **Portfolio mapping:** connect Carrier's public product families to the corresponding HVAC market categories.
        5. **Operations interpretation:** translate market signals into demand-planning, localisation, supplier, quality, and process-improvement questions.
        """
    )

    st.markdown(
        """
        <div class="source-note">
          <strong>Confidentiality design:</strong> the repository contains only illustrative public-demo market data. "
          The private BSRIA-based Excel workbook is loaded locally or through session upload and is excluded by .gitignore. "
          Do not publish report screenshots, extracts, or proprietary values without permission.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Public sources used for Carrier mapping")
    for _, row in products[["Source Label", "Source URL"]].drop_duplicates().iterrows():
        st.markdown(f"- [{row['Source Label']}]({row['Source URL']})")

    st.caption(
        "This is an independent analytical project inspired by a Carrier India factory visit. It is not an official Carrier dashboard, "
        "and public product availability should be rechecked before external publication."
    )
