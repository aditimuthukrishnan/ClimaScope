from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.charts import (
    market_change_chart,
    portfolio_coverage_chart,
    priority_breakdown_chart,
)
from src.data import (
    DataValidationError,
    load_market_csv,
    load_products_csv,
    read_private_workbook,
)
from src.scoring import calculate_scores, category_action


APP_DIR = Path(__file__).resolve().parent
PRIVATE_XLSX = APP_DIR / "private_input" / "India_HVAC_Market_Prioritisation_Dashboard.xlsx"
PRODUCTS_CSV = APP_DIR / "data" / "carrier_products_public.csv"
DEMO_CSV = APP_DIR / "data" / "market_demo.csv"
TEMPLATE_DIR = APP_DIR / "data_templates"


st.set_page_config(
    page_title="ClimaScope | India HVAC growth choices",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.3rem; padding-bottom: 2rem; max-width: 1500px;}
      [data-testid="stMetric"] {
        border: 1px solid #d7e0e5;
        border-radius: 10px;
        padding: 0.8rem 0.9rem;
        background: #ffffff;
        box-shadow: 0 2px 8px rgba(16, 59, 74, 0.05);
      }
      [data-testid="stMetricLabel"] {color: #526874;}
      .decision-banner {
        border-left: 6px solid #d6a84b;
        background: #f8fbfc;
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin: 0.4rem 0 1rem 0;
      }
      .decision-banner h3 {color: #103b4a; margin: 0 0 0.35rem 0;}
      .plain-card {
        border: 1px solid #d7e0e5;
        border-radius: 10px;
        padding: 1rem;
        background: #ffffff;
        min-height: 155px;
        margin-bottom: 0.75rem;
      }
      .plain-card strong {color: #103b4a;}
      .muted {color: #607580; font-size: 0.9rem;}
      .source-note {
        border-left: 4px solid #1f6f8b;
        background: #f4f8fa;
        padding: 0.8rem 1rem;
        border-radius: 5px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_public_market_data() -> pd.DataFrame:
    return load_market_csv(DEMO_CSV)


@st.cache_data
def load_product_data() -> pd.DataFrame:
    return load_products_csv(PRODUCTS_CSV)


def format_market_value(value: float, is_demo: bool) -> str:
    if is_demo:
        return f"{value:,.0f} index"
    return f"USD {value:,.1f} mn"


def top_category_message(top_row: pd.Series) -> str:
    return (
        f"Based on the current inputs, <strong>{top_row['Product Category']}</strong> "
        "should be studied first. It combines market growth, market size and the "
        "importance of energy efficiency better than the other categories in this view."
    )


st.sidebar.title("Choose your view")
data_mode = st.sidebar.radio(
    "Data to use",
    ["Sample data", "Private workbook"],
    help="Sample data is safe for the public demo. The private workbook is used only in the current session.",
)

uploaded_file = None
if data_mode == "Private workbook":
    uploaded_file = st.sidebar.file_uploader(
        "Upload the BSRIA-based workbook",
        type=["xlsx"],
        help="The workbook is read for this session and is not added to the repository.",
    )

with st.sidebar.expander("Change what matters most"):
    st.caption("These settings change the ranking. The standard view uses 40%, 35% and 25%.")
    size_weight = st.slider("Market size", 0, 100, 40, 5) / 100
    growth_weight = st.slider("Growth", 0, 100, 35, 5) / 100
    energy_weight = st.slider("Energy efficiency", 0, 100, 25, 5) / 100
    selected_total = size_weight + growth_weight + energy_weight
    if selected_total > 0:
        st.caption(
            "Used in the ranking: "
            f"size {size_weight / selected_total:.0%}, "
            f"growth {growth_weight / selected_total:.0%}, "
            f"energy {energy_weight / selected_total:.0%}."
        )
    else:
        st.caption("All settings are zero, so the standard mix will be used.")


try:
    products = load_product_data()
    if data_mode == "Sample data":
        market_df = load_public_market_data()
        is_demo = True
        source_label = "illustrative public data"
    elif uploaded_file is not None:
        market_df = read_private_workbook(uploaded_file)
        is_demo = False
        source_label = "uploaded private workbook"
    elif PRIVATE_XLSX.exists():
        market_df = read_private_workbook(PRIVATE_XLSX)
        is_demo = False
        source_label = "local private workbook"
    else:
        st.error(
            "No private workbook was found. Upload it in the sidebar or switch back to Sample data."
        )
        st.stop()
except (DataValidationError, ValueError, OSError) as exc:
    st.error(f"This data cannot be used yet. {exc}")
    st.stop()


market_df = calculate_scores(
    market_df,
    size_weight=size_weight,
    growth_weight=growth_weight,
    energy_weight=energy_weight,
)
top_row = market_df.iloc[0]


st.title("ClimaScope")
st.subheader("India HVAC growth choices")
st.caption(
    "A clear view of where Carrier could focus, why each market ranks where it does, "
    "and what information is still needed before investment."
)

if is_demo:
    st.info(
        "This public view uses sample index values. It demonstrates the decision process, not Carrier's actual market forecast."
    )
else:
    st.warning(
        f"This private view uses the {source_label}. Do not publish licensed values or report extracts."
    )


leadership_tab, markets_tab, products_tab, supply_tab, sources_tab = st.tabs(
    [
        "Leadership view",
        "Compare markets",
        "Carrier product coverage",
        "Supply and energy",
        "Sources and assumptions",
    ]
)


with leadership_tab:
    st.markdown(
        f"""
        <div class="decision-banner">
          <h3>Where to focus first</h3>
          {top_category_message(top_row)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("First market to study", top_row["Product Category"])
    c2.metric(
        "Expected annual growth",
        f"{top_row['Annual Change']:.1%}",
    )
    c3.metric(
        "2026 market level",
        format_market_value(top_row["2026 Value"], is_demo),
    )
    c4.metric(
        "Carrier product ranges mapped",
        f"{products['Portfolio Category'].nunique()}",
    )

    st.plotly_chart(
        priority_breakdown_chart(market_df),
        use_container_width=True,
        config={"displayModeBar": False},
        key="leadership_priority_chart",
    )
    st.caption(
        "The full bar is the priority score. Its three parts show how market size, growth and energy efficiency shape the result."
    )

    st.plotly_chart(
        market_change_chart(market_df, is_demo),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    st.subheader("What leadership should do next")
    actions = market_df.head(3).copy()
    actions["Next step"] = actions.apply(category_action, axis=1)
    actions["Why now"] = actions["Scoring Rationale"]
    actions = actions.rename(
        columns={"Priority Rank": "Rank", "Product Category": "Market"}
    )
    st.dataframe(
        actions[["Rank", "Market", "Why now", "Next step"]],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("What is still needed before approval")
    missing_cols = st.columns(3)
    with missing_cols[0]:
        st.markdown(
            """
            <div class="plain-card">
              <strong>Profit case</strong><br><br>
              Estimate achievable sales, margin, investment and payback for the leading categories.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with missing_cols[1]:
        st.markdown(
            """
            <div class="plain-card">
              <strong>Supply check</strong><br><br>
              Confirm local availability, supplier capacity, lead times and single-supplier risks.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with missing_cols[2]:
        st.markdown(
            """
            <div class="plain-card">
              <strong>Product and rule check</strong><br><br>
              Verify product gaps and upcoming efficiency requirements before committing investment.
            </div>
            """,
            unsafe_allow_html=True,
        )


with markets_tab:
    st.subheader("Compare the six market categories")
    st.write(
        "The ranking changes when leadership gives more importance to size, growth or energy efficiency. "
        "Use the sidebar only when you want to test a different view."
    )

    st.plotly_chart(
        priority_breakdown_chart(market_df),
        use_container_width=True,
        config={"displayModeBar": False},
        key="market_comparison_priority_chart",
    )

    table = market_df[
        [
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
    ].copy()
    table["Annual Change"] = table["Annual Change"].map(lambda value: f"{value:.1%}")
    score_columns = [
        "Market Size Score",
        "Growth Score",
        "Energy Relevance",
        "Opportunity Score",
    ]
    for column in score_columns:
        table[column] = table[column].map(lambda value: f"{value:.2f}")
    table = table.rename(
        columns={
            "Priority Rank": "Rank",
            "Product Category": "Market",
            "2024 Value": "2024",
            "2025 Value": "2025",
            "2026 Value": "2026",
            "Annual Change": "Annual growth",
            "Market Size Score": "Size rating",
            "Growth Score": "Growth rating",
            "Energy Relevance": "Energy importance",
            "Opportunity Score": "Priority score",
            "Scoring Rationale": "Why it matters",
        }
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.download_button(
        "Download the market comparison",
        market_df.to_csv(index=False).encode("utf-8"),
        file_name="climascope_market_comparison.csv",
        mime="text/csv",
    )


with products_tab:
    st.subheader("Where Carrier already has product coverage")
    st.write(
        "This view links publicly listed Carrier product ranges with the six market categories. "
        "It shows presence, not sales strength or market share."
    )

    filter_cols = st.columns(3)
    with filter_cols[0]:
        selected_portfolio = st.multiselect(
            "Carrier product range",
            sorted(products["Portfolio Category"].unique()),
        )
    with filter_cols[1]:
        selected_application = st.multiselect(
            "Main use",
            sorted(products["Primary Application"].unique()),
        )
    with filter_cols[2]:
        selected_market = st.multiselect(
            "Market category",
            sorted(products["Mapped Market Category"].unique()),
        )

    filtered = products.copy()
    if selected_portfolio:
        filtered = filtered[
            filtered["Portfolio Category"].isin(selected_portfolio)
        ]
    if selected_application:
        filtered = filtered[
            filtered["Primary Application"].isin(selected_application)
        ]
    if selected_market:
        filtered = filtered[
            filtered["Mapped Market Category"].isin(selected_market)
        ]

    if filtered.empty:
        st.warning("No products match the selected filters.")
    else:
        product_table = filtered[
            [
                "Portfolio Category",
                "Representative Product / Offering",
                "Product Type",
                "Primary Application",
                "Energy / Controls Relevance",
                "India Manufacturing / Presence",
                "Mapped Market Category",
            ]
        ].rename(
            columns={
                "Portfolio Category": "Carrier range",
                "Representative Product / Offering": "Example product",
                "Product Type": "Product type",
                "Primary Application": "Main use",
                "Energy / Controls Relevance": "Energy features",
                "India Manufacturing / Presence": "India presence",
                "Mapped Market Category": "Market category",
            }
        )
        st.dataframe(product_table, use_container_width=True, hide_index=True)

    st.plotly_chart(
        portfolio_coverage_chart(products),
        use_container_width=True,
        config={"displayModeBar": False},
    )
    st.caption(
        "A dark square means at least one public Carrier product range is mapped to that market. "
        "The next version will replace this yes/no view with a product-fit rating."
    )


with supply_tab:
    st.subheader("Questions that must be answered before investment")
    st.write(
        "The current public data can point to attractive markets. It cannot yet prove that Carrier can supply them at the right cost and quality."
    )

    question_cols = st.columns(3)
    with question_cols[0]:
        st.markdown(
            """
            <div class="plain-card">
              <strong>Can we make enough?</strong><br><br>
              Compare expected demand with factory and supplier capacity for each leading product range.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with question_cols[1]:
        st.markdown(
            """
            <div class="plain-card">
              <strong>Can more parts be sourced locally?</strong><br><br>
              Find imported parts with high cost, long lead times or suitable Indian alternatives.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with question_cols[2]:
        st.markdown(
            """
            <div class="plain-card">
              <strong>Will delivery and quality hold?</strong><br><br>
              Check late deliveries, rejected parts and dependence on a single supplier.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Information to add next")
    next_data = pd.DataFrame(
        [
            ["Expected demand", "Monthly sales and demand by product", "How much capacity is needed"],
            ["Factory capacity", "Available output and current use", "Where production may fall short"],
            ["Supplier delivery", "Planned and actual delivery dates", "Which suppliers may delay growth"],
            ["Part quality", "Delivered and rejected quantities", "Where quality problems create cost"],
            ["Local sourcing", "Imported parts, cost and Indian alternatives", "Where local sourcing can reduce risk"],
            ["Energy rules", "Required efficiency level and effective date", "Which products need an update"],
        ],
        columns=["Area", "Information needed", "Decision it supports"],
    )
    st.dataframe(next_data, use_container_width=True, hide_index=True)


with sources_tab:
    st.subheader("How the current ranking works")
    st.markdown(
        """
        1. Compare the expected 2026 size of each market.
        2. Compare how quickly each market is growing.
        3. Add the importance of energy efficiency for that category.
        4. Combine the three ratings using the selected importance settings.
        5. Rank the categories from highest to lowest.
        """
    )

    with st.expander("Show the calculation detail"):
        st.write(
            "Market size and growth are each converted to a rating from 1 to 5 within the six categories. "
            "The energy rating is already provided on the same scale. The three ratings are multiplied by "
            "their selected weights and added together. This is a relative comparison, so adding a new category "
            "can change the ratings."
        )

    st.markdown(
        """
        <div class="source-note">
          <strong>Data use:</strong> the public repository contains only illustrative market values. The private
          workbook can be uploaded for an authorised review and is excluded from Git. Product availability and
          public sources should be checked again before an external presentation.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Public Carrier sources")
    for _, row in products[["Source Label", "Source URL"]].drop_duplicates().iterrows():
        st.markdown(f"- [{row['Source Label']}]({row['Source URL']})")

    st.subheader("Input templates for the next build")
    st.write(
        "These blank files show exactly what information is required for market history, efficiency rules, suppliers and the financial case."
    )
    template_names = {
        "Market history": "market_history_template.csv",
        "Efficiency rules": "regulations_template.csv",
        "Supplier readiness": "supplier_readiness_template.csv",
        "Financial assumptions": "financial_assumptions_template.csv",
    }
    download_cols = st.columns(4)
    for column, (label, filename) in zip(download_cols, template_names.items()):
        path = TEMPLATE_DIR / filename
        with column:
            if path.exists():
                st.download_button(
                    label,
                    path.read_bytes(),
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True,
                )

    st.caption(
        "ClimaScope is an independent project inspired by a Carrier India industrial visit. It is not an official Carrier dashboard."
    )
