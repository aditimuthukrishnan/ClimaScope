# ClimaScope input guide

The dashboard is being built in two layers:

- The public demo uses sample market values and public Carrier product information.
- The private view can use licensed market research and approved company inputs.

Do not add licensed BSRIA extracts or confidential company data to the public repository.

## Market history

Use `market_history_template.csv` for market values over time. One row should represent one date, market category, region and customer segment.

Use the same unit throughout a comparison. Mark every row as `Actual` or `Forecast`, name the scenario when relevant, and include the source date.

## Efficiency rules

Use `regulations_template.csv` to connect an efficiency requirement to the products it affects. Keep the official source link and the date on which the requirement was checked.

Use simple status values such as:

- Meets requirement
- Update needed
- Not checked

## Supplier readiness

Use `supplier_readiness_template.csv` to record whether the parts needed for growth can be supplied at the required volume, cost, quality and speed.

If real supplier data is unavailable, keep the file empty or label every sample row as illustrative. Do not present sample suppliers as Carrier suppliers.

## Financial assumptions

Use `financial_assumptions_template.csv` to build the business case for each market category. Every assumption should include either a source or a short explanation.

Create at least three scenarios:

- Base
- Upside
- Downside

## Checks before using a file

- No repeated category-and-date rows
- No mixed currencies or units in the same comparison
- Percentages entered consistently
- Source and source date completed
- Sample and confidential data clearly separated
- Totals checked against the original source

