# ClimaScope: India HVAC growth choices

A Streamlit project that helps compare Indian HVAC market categories, understand where Carrier already has product coverage, and identify the checks needed before an investment decision.

## What the app includes

- Leadership-first summary written in plain business language
- Adjustable market-size, growth, and energy-efficiency settings
- Six-category market ranking with a clear score breakdown
- Carrier product-family explorer using public official sources
- Portfolio-to-market coverage heatmap
- Supply, local-sourcing, quality, and energy questions for the next stage
- Downloadable input templates for market history, efficiency rules, suppliers, and financial assumptions
- Public demo mode and private workbook mode

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
streamlit run app.py
```

## Use the private Excel analysis

Place the workbook at:

```text
private_input/India_HVAC_Market_Prioritisation_Dashboard.xlsx
```

Alternatively, select **Private workbook** in the sidebar and upload the workbook during the session.

The app expects the workbook to contain a sheet named `Market Data`, with the same structure as the supplied Excel model.

## Deploy publicly on Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Confirm that the confidential workbook is not committed.
3. In Streamlit Community Cloud, choose the repository and set `app.py` as the entry point.
4. Keep the app in **Sample data** mode for public deployment.

## Run the checks

```bash
python -m unittest discover -s tests -v
```

## Prepare the next data layer

Blank input files are available in `data_templates/`. A plain-language guide is available in `docs/DATA_INPUT_GUIDE.md`.

## Confidentiality

The repository contains illustrative indexed market data only. The BSRIA-based workbook is intentionally excluded through `.gitignore`. Do not publish proprietary report values, screenshots, or extracts without permission.

## Public sources

- Carrier India commercial product portfolio: https://www.carrier.com/commercial/en/in/
- About Carrier India and Gurugram manufacturing: https://www.carrier.com/commercial/en/in/about/about-carrier-india/
- Carrier India data-centre solutions: https://www.carrier.com/commercial/en/in/data-centers/
- Carrier Midea India room AC catalogue: https://carriermideaindia.com/product-category/carrier-room-air-conditioners/
