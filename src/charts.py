from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


NAVY = "#103B4A"
BLUE = "#1F6F8B"
GOLD = "#D6A84B"
LIGHT_BLUE = "#83B8C9"
LIGHT_GREY = "#E8EEF2"


def apply_chart_style(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=70, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#17324D", family="Arial"),
        title_font=dict(size=18, color=NAVY),
        legend_title_text="",
        hoverlabel=dict(bgcolor="white", font_color="#17324D"),
    )
    fig.update_xaxes(gridcolor="#EDF2F5", zeroline=False)
    fig.update_yaxes(gridcolor="#EDF2F5", zeroline=False)
    return fig


def market_change_chart(market_df: pd.DataFrame, is_demo: bool) -> go.Figure:
    values = market_df.melt(
        id_vars="Product Category",
        value_vars=["2024 Value", "2025 Value", "2026 Value"],
        var_name="Year",
        value_name="Market Value",
    )
    values["Year"] = values["Year"].str.extract(r"(2024|2025|2026)")
    fig = px.bar(
        values,
        x="Product Category",
        y="Market Value",
        color="Year",
        barmode="group",
        title="How each market category changes from 2024 to 2026",
        labels={
            "Product Category": "Market category",
            "Market Value": "Market index" if is_demo else "Market value (USD mn)",
        },
        color_discrete_map={"2024": LIGHT_GREY, "2025": LIGHT_BLUE, "2026": BLUE},
    )
    fig.update_layout(xaxis_tickangle=-18)
    return apply_chart_style(fig, height=440)


def priority_breakdown_chart(market_df: pd.DataFrame) -> go.Figure:
    plot_df = market_df.sort_values("Opportunity Score", ascending=True)
    fig = go.Figure()
    parts = [
        ("Market size contribution", "Market size", BLUE),
        ("Growth contribution", "Growth", GOLD),
        ("Energy contribution", "Importance of energy efficiency", LIGHT_BLUE),
    ]
    for column, label, color in parts:
        fig.add_bar(
            x=plot_df[column],
            y=plot_df["Product Category"],
            name=label,
            orientation="h",
            marker_color=color,
            hovertemplate=f"{label}: %{{x:.2f}}<extra></extra>",
        )
    fig.update_layout(
        barmode="stack",
        title="Why each category ranks where it does",
        xaxis_title="Priority score out of 5",
        yaxis_title="",
        xaxis_range=[0, 5.15],
    )
    return apply_chart_style(fig, height=430)


def portfolio_coverage_chart(products: pd.DataFrame) -> go.Figure:
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
    fig = go.Figure(
        data=go.Heatmap(
            z=coverage.values,
            x=coverage.columns,
            y=coverage.index,
            colorscale=[[0, "#F1F4F6"], [1, BLUE]],
            showscale=False,
            hovertemplate="Market: %{y}<br>Carrier range: %{x}<extra></extra>",
            xgap=2,
            ygap=2,
        )
    )
    fig.update_layout(
        title="Where Carrier already has a product range",
        xaxis_title="Carrier product range",
        yaxis_title="Market category",
    )
    return apply_chart_style(fig, height=440)
