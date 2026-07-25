# India HVAC Market & Carrier Portfolio Prioritisation

A Streamlit decision-support project that connects HVAC market attractiveness, energy-efficiency relevance, Carrier India's public product portfolio, and supply-chain implications.

## What the app includes

- Adjustable market-size, growth, and energy-efficiency weights
- HVAC category ranking and opportunity matrix
- Carrier product-family explorer using public official sources
- Portfolio-to-market coverage heatmap
- Supply-chain, localisation, quality, and process-improvement interpretation
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

Alternatively, select **Private BSRIA analysis** in the sidebar and upload the workbook during the session.

The app expects the workbook to contain a sheet named `Market Data`, with the same structure as the supplied Excel model.

## Deploy publicly on Streamlit Community Cloud

1. Push this project to a GitHub repository.
2. Confirm that the confidential workbook is not committed.
3. In Streamlit Community Cloud, choose the repository and set `app.py` as the entry point.
4. Keep the app in **Public portfolio demo** mode for public deployment.

## Confidentiality

The repository contains illustrative indexed market data only. The BSRIA-based workbook is intentionally excluded through `.gitignore`. Do not publish proprietary report values, screenshots, or extracts without permission.

## Public sources

- Carrier India commercial product portfolio: https://www.carrier.com/commercial/en/in/
- About Carrier India and Gurugram manufacturing: https://www.carrier.com/commercial/en/in/about/about-carrier-india/
- Carrier India data-centre solutions: https://www.carrier.com/commercial/en/in/data-centers/
- Carrier Midea India room AC catalogue: https://carriermideaindia.com/product-category/carrier-room-air-conditioners/

## Resume positioning

**Project: India HVAC Market & Carrier Portfolio Prioritisation**

Built a Streamlit decision-support dashboard to rank HVAC product categories using market size, growth, and energy-efficiency relevance, map Carrier's public product portfolio, and translate demand signals into supply-chain, localisation, and process-improvement priorities.

## Interview explanation

- The app separates the scoring logic from the assumptions through adjustable weights.
- Market categories are mapped to public Carrier product families rather than claiming access to internal product strategy.
- Private BSRIA data can be analysed locally without publishing proprietary figures.
- The next extension would add monthly demand, inventory, supplier performance, manufacturing quality, and energy-consumption data.
