# DashSpec Data Quality Management Design

## Overview

A generalized, declarative approach to data quality management that allows users to specify how to handle missing values, outliers, duplicates, and validation rules directly in the dashboard YAML specification.

## Design Principles

1. **Declarative** - Rules defined in YAML, not code
2. **Composable** - Multiple rules can be applied in sequence
3. **Transparent** - All transformations logged and reported
4. **Reversible** - Original data preserved, transformations applied at render time
5. **Validated** - Rules validated against schema before execution

## Schema Extension (v1.3)

### New `data_quality` Section

```yaml
data_source:
  type: "parquet"
  path: "data.parquet"

  data_quality:
    # Strategy for missing values
    missing_values:
      strategy: "auto"  # auto|drop|fill|flag
      rules:
        - fields: ["inflation", "inflation_filled"]
          action: "fill_forward"  # drop|fill_forward|fill_backward|fill_value|interpolate
          limit: 12  # Max consecutive fills

        - fields: ["close", "open", "high", "low"]
          action: "drop_rows"  # Drop rows with any missing OHLC

        - fields: ["daily_volatility"]
          action: "fill_value"
          value: 0.0

    # Outlier detection and handling
    outliers:
      enabled: true
      rules:
        - fields: ["inflation_filled"]
          method: "iqr"  # iqr|zscore|percentile|custom
          threshold: 3.0  # IQR multiplier or z-score threshold
          action: "cap"  # cap|drop|flag|none

        - fields: ["daily_volatility"]
          method: "percentile"
          lower: 0.5
          upper: 99.5
          action: "cap"

    # Duplicate handling
    duplicates:
      enabled: true
      subset: ["date", "country"]  # Fields to check for duplicates
      keep: "last"  # first|last|none
      action: "drop"  # drop|flag|aggregate

    # Value validation
    validation:
      rules:
        - field: "inflation_filled"
          constraint: "range"
          min: -100
          max: 1000
          action: "flag"  # flag|drop|coerce

        - field: "year"
          constraint: "in_set"
          values: [2007, 2008, 2009, ..., 2023]
          action: "drop"

        - field: "country"
          constraint: "not_null"
          action: "drop"

    # Type coercion
    coercion:
      rules:
        - fields: ["year", "month", "quarter"]
          target_type: "integer"
          on_error: "coerce"  # coerce|raise|ignore

        - fields: ["date"]
          target_type: "datetime"
          format: "%Y-%m-%d"

    # Transformation pipeline
    transformations:
      - name: "remove_early_months"
        description: "Remove first 12 months per country (no YoY data)"
        type: "custom_filter"
        operation: "group_rank"
        group_by: ["country"]
        order_by: "date"
        keep_ranks: [13, -1]  # Keep from 13th month onwards

      - name: "impute_missing_inflation"
        description: "Calculate inflation from prices when missing"
        type: "custom_compute"
        field: "inflation_filled"
        formula: "pct_change(close, periods=12) * 100"
        condition: "inflation_filled.isnull()"

    # Reporting
    reporting:
      log_level: "info"  # debug|info|warn|error
      show_summary: true
      show_details: false
      metrics:
        - "total_rows"
        - "rows_dropped"
        - "rows_modified"
        - "missing_values_filled"
        - "outliers_capped"
        - "duplicates_removed"
```

## Implementation Architecture

### 1. DataQualityProcessor Class

```python
class DataQualityProcessor:
    """
    Process data quality rules and transformations
    """

    def __init__(self, rules: Dict):
        self.rules = rules
        self.report = DataQualityReport()

    def process(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Apply all DQ rules and return cleaned data + report"""
        df = df.copy()

        # Phase 1: Type coercion
        df = self._apply_coercion(df)

        # Phase 2: Missing value handling
        df = self._handle_missing_values(df)

        # Phase 3: Duplicate detection/removal
        df = self._handle_duplicates(df)

        # Phase 4: Outlier detection/handling
        df = self._handle_outliers(df)

        # Phase 5: Validation
        df = self._apply_validations(df)

        # Phase 6: Custom transformations
        df = self._apply_transformations(df)

        return df, self.report.to_dict()
```

### 2. Integration Points

**In `adapter.py` execute():**
```python
def execute(ir: dict, inputs: dict) -> dict:
    # Load data
    df = load_data(data_path)

    # Apply data quality rules
    dq_rules = ir.get('data_quality_rules')
    if dq_rules:
        dq_processor = DataQualityProcessor(dq_rules)
        df, dq_report = dq_processor.process(df)

        # Include DQ report in results
        results['data_quality'] = dq_report

    # Continue with normal processing...
```

### 3. Reporting & Visualization

**DQ Summary in UI:**
```python
if 'data_quality' in results:
    with st.expander("📊 Data Quality Report", expanded=False):
        dq = results['data_quality']

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows Processed", f"{dq['total_rows']:,}")
        with col2:
            st.metric("Rows Modified", f"{dq['rows_modified']:,}")
        with col3:
            st.metric("Issues Found", f"{dq['issues_detected']:,}")

        # Detailed breakdown
        if dq.get('show_details'):
            st.dataframe(dq['details'])
```

## Example Usage Patterns

### Pattern 1: Conservative (Minimal Transformation)
```yaml
data_quality:
  missing_values:
    strategy: "flag"  # Just flag, don't modify
  outliers:
    enabled: false
  duplicates:
    action: "flag"
  reporting:
    show_details: true
```

### Pattern 2: Aggressive Cleaning
```yaml
data_quality:
  missing_values:
    strategy: "auto"  # Intelligent handling
  outliers:
    enabled: true
    action: "drop"
  duplicates:
    action: "drop"
  reporting:
    show_summary: true
```

### Pattern 3: Domain-Specific (Financial)
```yaml
data_quality:
  missing_values:
    rules:
      - fields: ["price", "volume"]
        action: "drop_rows"  # Never impute financial data
  outliers:
    rules:
      - fields: ["return"]
        method: "zscore"
        threshold: 5.0  # Wide threshold for returns
        action: "flag"
  validation:
    rules:
      - field: "price"
        constraint: "range"
        min: 0
        max: 999999
        action: "drop"
```

## Benefits

1. **Transparency** - All DQ decisions documented in YAML
2. **Reproducibility** - Same YAML = same transformations
3. **Auditability** - Full report of what was changed
4. **Flexibility** - Easy to adjust rules without code changes
5. **Reusability** - DQ templates can be shared across dashboards
6. **Testing** - DQ rules can be validated independently

## Backward Compatibility

- All DQ rules are **optional**
- Dashboards without `data_quality` section work unchanged
- Default behavior: No transformations applied
- Can gradually adopt DQ rules

## Future Enhancements

- **DQ Templates** - Pre-built rule sets for common domains
- **Interactive DQ** - UI to adjust rules and see effects
- **ML-Based DQ** - Anomaly detection using models
- **DQ Monitoring** - Track DQ metrics over time
- **DQ Validation** - Test DQ rules against sample data
