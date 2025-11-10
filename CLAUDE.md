# DashSpec Project Guide for Claude

## Project Overview

**DashSpec** is a declarative Domain-Specific Language (DSL) for creating interactive analytics dashboards. It enables users to define complete dashboards in YAML that are automatically rendered using Streamlit and Plotly.

**Current Version:** DashSpec v1.2.0
**Python Version:** 3.11+
**Primary Framework:** Streamlit
**Visualization:** Plotly Express/Graph Objects

## Project Structure

```
/Volumes/SSD/Essentials/
├── dsl/                          # Core DSL implementation
│   ├── schema.json               # v1.0 schema
│   ├── schema_v1.1.json          # v1.1 schema (role-based)
│   ├── schema_v1.2.json          # v1.2 schema (formatting + DQ) ⭐
│   ├── adapter.py                # Parse, validate, execute dashboards
│   ├── viz_renderers.py          # 15+ chart type renderers
│   ├── streamlit_renderer.py    # Main Streamlit integration
│   ├── formatting.py             # Number/currency formatting ⭐
│   ├── data_loader.py            # Optimized data loading with caching
│   ├── data_quality.py           # Data quality processor ⭐
│   └── examples/                 # Example dashboard specs
│       ├── fraud_detection_v1.1.yaml
│       ├── food_price_inflation_v1.2.yaml ⭐
│       └── [8 other dashboards]
├── data/
│   ├── raw/                      # Raw downloaded data
│   └── processed/                # Cleaned parquet files
├── docs/                         # Documentation
│   ├── dashspec_v1.2_enhancements.md ⭐
│   ├── data_quality_design.md ⭐
│   └── data_loading_optimization.md
├── app.py                        # Unified dashboard gallery
├── run_dashboard.py              # Single dashboard runner
├── Makefile                      # Common commands
└── config/datasets.yaml          # Dataset registry
```

## Key Concepts

### 1. DSL Versions

**v1.0** - Original DSL (field-based)
- Direct field references: `x_field`, `y_field`, `color_field`

**v1.1** - Role-based enhancements
- Semantic roles: `roles: {x: "field", y: "field"}`
- 15+ chart types (ECDF, violin, KDE, hexbin, etc.)

**v1.2** - Formatting & Data Quality ⭐ CURRENT
- Currency symbols (40+ currencies)
- Number formatting (precision, thousands separators)
- Human-readable column labels
- Data quality management system
- Dataset narratives

### 2. Dashboard Specification Structure

```yaml
dsl_version: "1.2.0"

dashboard:
  id: "unique_id"
  title: "Dashboard Title"

  metadata:
    dataset_name: "Dataset Name"
    source: "Data Source"
    rows: 10000
    description: "Brief description"
    narrative: "Detailed multi-paragraph description..."  # v1.2
    currency: "USD"  # v1.2 default currency
    tags: ["tag1", "tag2"]
    use_cases: ["Use case 1", "Use case 2"]

  data_source:
    type: "parquet"
    path: "data/processed/file.parquet"

    schema:  # Data types
      field1: "string"
      field2: "integer"
      field3: "float"
      field4: "datetime"

    column_labels:  # v1.2 Human-readable labels
      field1: "Field 1 Label"
      field2: "Field 2 Label"

    formatting:  # v1.2 Default formatting
      field1:
        type: "currency"
        precision: 2
        currency_code: "USD"
      field2:
        type: "percent"
        precision: 1

    data_quality:  # v1.2 DQ rules
      missing_values:
        strategy: "auto"
        rules:
          - fields: ["critical_field"]
            action: "drop_rows"
      outliers:
        enabled: true
        rules:
          - fields: ["numeric_field"]
            method: "iqr"
            threshold: 3.0
            action: "cap"
      duplicates:
        enabled: true
        subset: ["key_field"]
        action: "drop"
      validation:
        rules:
          - field: "year"
            constraint: "range"
            min: 2000
            max: 2025
            action: "drop"

  pages:
    - id: "page1"
      title: "Page Title"

      filters:
        - id: "filter1"
          label: "Filter Label"
          type: "multiselect"  # range|slider|select|multiselect|date_range
          field: "field_name"
          default: ["value1"]

      metrics:
        - id: "metric1"
          label: "Metric Label"
          field: "field_name"
          aggregation: "sum"  # count|count_unique|mean|median|min|max|std
          format:  # v1.2 enhanced format
            type: "currency"
            precision: 2
            currency_code: "USD"
          filter:  # Optional metric filter
            field: "status"
            operator: "eq"
            value: "active"

      layout:
        type: "grid"  # single|grid|tabs
        components:
          - id: "viz1"
            type: "visualization"
            title: "Chart Title"
            visualization:
              chart_type: "scatter"  # See chart types below
              roles:  # v1.1 role-based
                x: "field1"
                y: "field2"
                color: "field3"
                size: "field4"
              params:
                limit: 10000  # Row limit for viz
                trendline: "ols"
                alpha: 0.7
                formatting:  # v1.2 viz-specific formatting
                  field1:
                    type: "number"
                    precision: 2
                column_labels:  # v1.2 viz-specific labels
                  field1: "Custom Label"
```

### 3. Supported Chart Types

**Level 0: Tables & Summaries**
- `table` - Data table with formatting
- `summary` - Summary statistics

**Level 1: Distributions**
- `histogram` - Univariate distribution
- `ecdf` - Empirical CDF
- `boxplot` - Box and whisker
- `violin` - Violin plot (density + quantiles)
- `kde` - 1D kernel density estimate

**Level 2: Relationships**
- `scatter` - Scatter plot with optional trendline
- `hexbin` - 2D histogram (density)
- `kde2d` - 2D kernel density contours

**Level 3: Time Series & Categories**
- `line` - Time series line chart
- `bar` - Bar chart for categories
- `heatmap` - Pivot table heatmap
- `corr_heatmap` - Correlation matrix
- `pie` - Pie chart

### 4. Data Quality Management (v1.2)

DQ rules are applied automatically after data load:

**Missing Values:**
- `drop_rows` - Remove rows
- `fill_forward` / `fill_backward` - Fill from adjacent
- `fill_value` - Fill with constant
- `interpolate` - Linear interpolation
- `flag` - Create indicator column

**Outliers:**
- Methods: `iqr`, `zscore`, `percentile`
- Actions: `cap`, `drop`, `flag`

**Duplicates:**
- Based on `subset` of columns
- Keep: `first`, `last`, `none`

**Validation:**
- Constraints: `range`, `in_set`, `not_null`, `unique`
- Actions: `flag`, `drop`, `coerce`

### 5. Formatting System (v1.2)

**Format Types:**
- `integer` - Whole numbers with commas: 1,234,567
- `number` - Float with precision: 1,234.57
- `currency` - With symbol: $1,234.56
- `percent` - Percentage: 15.4%
- `date` / `datetime` - Date formatting

**Format Specification:**
```yaml
field_name:
  type: "currency"
  precision: 2
  use_thousands_separator: true
  currency_code: "USD"
  significant_digits: null  # Alternative to precision
  date_format: "%Y-%m-%d"
```

**Currency Symbols:** 40+ supported (USD: $, EUR: €, GBP: £, JPY: ¥, etc.)

## Common Tasks

### Creating a New Dashboard

1. **Prepare data:**
   ```bash
   # Download from Kaggle
   kaggle datasets download -d <dataset-id> -p data/raw/<name>

   # Process to parquet
   python process_data.py  # Custom script or ETL
   ```

2. **Create YAML spec:**
   ```bash
   cp dsl/examples/template_v1.2.yaml dsl/examples/my_dashboard_v1.2.yaml
   # Edit the YAML file
   ```

3. **Validate:**
   ```python
   from dsl.adapter import parse, validate
   model = parse(yaml_content)
   violations = validate(model)
   ```

4. **Test:**
   ```bash
   make dashboard-<name>
   # Or
   streamlit run run_dashboard.py -- dsl/examples/my_dashboard_v1.2.yaml
   ```

5. **Add to gallery:**
   - Update `app.py` DASHBOARDS dict
   - Add Makefile command
   - Update `config/datasets.yaml`

### Modifying Existing Dashboards

1. **Read the spec:**
   ```bash
   cat dsl/examples/dashboard_v1.2.yaml
   ```

2. **Test changes:**
   ```bash
   streamlit run run_dashboard.py -- dsl/examples/dashboard_v1.2.yaml
   ```

3. **Validate:**
   ```python
   from dsl.adapter import parse, validate
   # Validation happens automatically
   ```

### Adding Data Quality Rules

```yaml
data_source:
  data_quality:
    missing_values:
      rules:
        - fields: ["critical_field"]
          action: "drop_rows"

    outliers:
      enabled: true
      rules:
        - fields: ["metric_field"]
          method: "iqr"
          threshold: 3.0
          action: "cap"

    validation:
      rules:
        - field: "year"
          constraint: "range"
          min: 2000
          max: 2025
          action: "drop"
```

### Adding Formatting Rules

```yaml
data_source:
  column_labels:
    raw_field_name: "Human Readable Name"

  formatting:
    price_field:
      type: "currency"
      precision: 2
      currency_code: "USD"

    rate_field:
      type: "percent"
      precision: 1

    count_field:
      type: "integer"
      use_thousands_separator: true
```

## Best Practices

### 1. Dashboard Design
- Start with 1-3 pages max, expand later
- Put most important metrics first
- Use filters to enable exploration
- Limit visualizations to 5-8 per page
- Use appropriate chart types for data

### 2. Data Quality
- Always define DQ rules for production dashboards
- Drop rows with missing critical fields
- Cap outliers in user-facing metrics
- Validate data ranges and constraints
- Flag (don't drop) expected missing values

### 3. Formatting
- Define global formatting in `data_source`
- Override per-visualization only when needed
- Use currency inference when possible
- Provide column labels for all displayed fields
- Set appropriate precision (2 for money, 1 for %)

### 4. Performance
- Use `limit` param for large visualizations
- Enable data sampling for >100K rows (automatic)
- Specify column subset when loading data
- Cache is automatic (1 hour TTL)
- Tables: 100-1000 rows max
- Scatter plots: 10K-20K points max

### 5. Testing
- Validate YAML before committing
- Test with filters at different values
- Check metrics with known answers
- Verify formatting displays correctly
- Review data quality report

## Troubleshooting

### Dashboard Won't Load
1. Check YAML syntax: `yamllint dashboard.yaml`
2. Validate against schema: `python -c "from dsl.adapter import parse, validate; ..."`
3. Check file paths are correct
4. Verify data file exists and is readable

### Metrics Show NaN or 0
1. Check field names match data columns
2. Verify aggregation type is appropriate
3. Check filter conditions aren't too restrictive
4. Ensure data has non-null values
5. Review data quality rules (might be dropping data)

### Formatting Not Working
1. Verify `dsl_version: "1.2.0"`
2. Check formatting syntax in schema
3. Ensure field names are correct
4. Verify currency codes are valid (ISO 4217)

### Data Quality Issues
1. Review DQ report in dashboard expander
2. Check `rows_dropped` metric
3. Verify DQ rules aren't too aggressive
4. Test with `action: "flag"` first
5. Check for unexpected data patterns

## File Locations

**Schemas:** `dsl/schema_v1.2.json` (use this for v1.2)
**Examples:** `dsl/examples/*.yaml` (10 dashboards)
**Docs:** `docs/dashspec_v1.2_enhancements.md` (full v1.2 guide)
**Data:** `data/processed/*.parquet` (processed datasets)
**Tests:** Run `make test` (if tests exist)

## Common Commands

```bash
# Launch gallery
make dashboard-gallery

# Launch specific dashboard
make dashboard-food
make dashboard-fraud
make dashboard-power

# Run tests
make test

# Format code
make format

# Clean cache
make clean

# Get help
make help
```

## Extension Points

### Custom Renderers
Create `dsl/custom_viz_renderers.py`:
```python
from dsl.viz_renderers import VizRenderers

class CustomVizRenderers(VizRenderers):
    def render_custom_chart(self, df, viz, st_module):
        # Your implementation
        pass

# Register
CUSTOM_RENDERERS = {
    'custom_chart': CustomVizRenderers.render_custom_chart
}
```

### Custom Validators
Create custom validation rules in `dsl/custom_validators.py`

### Custom Transformations
Add to `data_quality.py` transformation pipeline

## Version History

- **v1.0.0** (2024) - Initial release, field-based
- **v1.1.0** (2024) - Role-based specs, 15+ chart types
- **v1.2.0** (2025-01) - Formatting, DQ, labels, narratives ⭐

## Key Insights for Claude

1. **Always use v1.2.0** for new dashboards
2. **Schema validation is automatic** - just parse and validate
3. **DQ rules are optional** but highly recommended
4. **Formatting cascade:** data_source → visualization → renderer
5. **Backward compatible:** v1.0/v1.1 dashboards still work
6. **Performance:** DataLoader handles caching/sampling automatically
7. **Extension:** Easy to add custom chart types
8. **Testing:** Load and validate before running Streamlit

## Quick Reference

**Create Dashboard:** Copy template → Edit YAML → Validate → Test
**Fix NaN Metrics:** Check field names, aggregations, DQ rules
**Add Formatting:** Use `formatting` dict with format specs
**Add DQ Rules:** Use `data_quality` section in data_source
**Debug:** Check validation errors, review DQ report
**Deploy:** Add to `app.py` DASHBOARDS dict

## Documentation References

- Schema: `dsl/schema_v1.2.json`
- V1.2 Guide: `docs/dashspec_v1.2_enhancements.md`
- DQ Design: `docs/data_quality_design.md`
- Data Loading: `docs/data_loading_optimization.md`
- Examples: `dsl/examples/food_price_inflation_v1.2.yaml`

---

**Remember:** DashSpec v1.2 is the current version. Use it for all new work. The system handles data loading, quality, formatting, and rendering automatically based on declarative YAML specifications.
