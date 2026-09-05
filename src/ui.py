from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st


ACTION_COLORS = {
    "Invest": "#0B5CAD",
    "Scale": "#2384C6",
    "Build Capability": "#7A5AF8",
    "Localise First": "#C27A14",
    "Monitor": "#667085",
    "Deprioritise": "#B42318",
}

BLUE_SCALE = ["#DDEEFF", "#A7D3F4", "#5AAAE0", "#2384C6", "#0B5CAD"]


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root { --cs-blue:#0B5CAD; --cs-ink:#102A43; --cs-muted:#667085; --cs-border:#E4E7EC; }
        .stApp { background: #F7F9FC; }
        .block-container { padding-top: 1.15rem; padding-bottom: 3rem; max-width: 1500px; }
        [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E4E7EC; }
        [data-testid="stMetric"] {
            background: #FFFFFF; border: 1px solid #E4E7EC; border-radius: 16px;
            padding: 0.9rem 1rem; box-shadow: 0 4px 12px rgba(16,42,67,0.04);
        }
        [data-testid="stMetricLabel"] { color:#667085; }
        .cs-hero {
            padding: 1.35rem 1.5rem; border-radius: 20px; margin-bottom: 1.1rem;
            background: linear-gradient(120deg,#062B4F 0%,#0B5CAD 62%,#2384C6 100%);
            color: white; box-shadow: 0 12px 30px rgba(11,92,173,.18);
        }
        .cs-hero h1 { color:white; margin:0; font-size:2rem; letter-spacing:-0.02em; }
        .cs-hero p { margin:.35rem 0 0 0; color:#DDEEFF; font-size:1rem; }
        .cs-card {
            background:#FFFFFF; border:1px solid #E4E7EC; border-radius:16px;
            padding:1rem 1.05rem; margin:.35rem 0 .85rem 0; box-shadow:0 4px 12px rgba(16,42,67,.04);
        }
        .cs-label { font-size:.76rem; color:#667085; text-transform:uppercase; letter-spacing:.08em; font-weight:700; }
        .cs-title { font-size:1.1rem; color:#102A43; font-weight:700; margin:.2rem 0; }
        .cs-muted { color:#667085; font-size:.9rem; }
        .cs-pill { display:inline-block; padding:.2rem .55rem; border-radius:999px; background:#EAF4FF; color:#0B5CAD; font-weight:700; font-size:.78rem; }
        div[data-testid="stDataFrame"] { border:1px solid #E4E7EC; border-radius:14px; overflow:hidden; }
        h1,h2,h3 { color:#102A43; letter-spacing:-.015em; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="cs-hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def section_card(label: str, title: str, body: str, pill: str | None = None) -> None:
    badge = f'<span class="cs-pill">{pill}</span>' if pill else ''
    st.markdown(
        f'<div class="cs-card"><div class="cs-label">{label}</div><div class="cs-title">{title}</div>{badge}<div class="cs-muted" style="margin-top:.5rem">{body}</div></div>',
        unsafe_allow_html=True,
    )


def style_figure(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=55, b=35),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#344054"),
        title_font=dict(color="#102A43", size=17),
        legend=dict(bgcolor="rgba(255,255,255,0.8)"),
    )
    fig.update_xaxes(gridcolor="#EEF2F6", zerolinecolor="#D0D5DD")
    fig.update_yaxes(gridcolor="#EEF2F6", zerolinecolor="#D0D5DD")
    return fig


def get_controls() -> dict:
    st.sidebar.markdown("## ClimaScope")
    st.sidebar.caption("HVAC Strategy & Forecasting Platform")
    st.sidebar.markdown("---")
    scenario = st.sidebar.selectbox("Planning scenario", ["Downside", "Base", "Upside"], index=1)
    horizon = st.sidebar.slider("Forecast horizon", 2029, 2031, 2031, 1)
    share_mode = st.sidebar.radio("Target-share assumption", ["Category defaults", "Common target share"], horizontal=False)
    common_share = None
    if share_mode == "Common target share":
        common_share = st.sidebar.slider("Common target share", 5, 30, 15, 1) / 100

    with st.sidebar.expander("Market-attractiveness weights"):
        size = st.slider("Market size", 0, 100, 40, 5, key="mw_size")
        growth = st.slider("Forecast growth", 0, 100, 35, 5, key="mw_growth")
        energy = st.slider("Energy relevance", 0, 100, 25, 5, key="mw_energy")
    total = size + growth + energy
    if total == 0:
        weights = {"size": .40, "growth": .35, "energy": .25}
    else:
        weights = {"size": size / total, "growth": growth / total, "energy": energy / total}

    st.sidebar.markdown("---")
    st.sidebar.caption("Public demo values are illustrative. Proprietary source data are intentionally excluded from GitHub.")
    return {"scenario": scenario, "horizon": horizon, "target_share": common_share, "market_weights": weights}
