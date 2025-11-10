# DashSpec v1.1 User Guide

## What's New in v1.1

DashSpec v1.1 introduces significant enhancements while maintaining backward compatibility with v1.0 specifications:

### New Features

1. **Role-Based Visualization Specs** - Clearer, more semantic field mappings
2. **15+ New Chart Types** - ECDF, violin plots, hexbin, correlation heatmaps, and more
3. **Code Generation System** - Auto-generate Python code from specs with version tracking
4. **Custom Renderer Framework** - Easy extension system for custom visualizations
5. **Enhanced Schema** - Support for additional parameters and validation

### Backward Compatibility

All v1.0.x specifications continue to work with v1.1 renderers. The system automatically detects and handles both:
- Legacy field-based specs (`x_field`, `y_field`, etc.)
- New role-based specs (`roles: {x: "field", y: "field"}`)

## Upgrading from v1.0 to v1.1

### Update DSL Version

```yaml
# Change from:
dsl_version: "1.0.0"

# To:
dsl_version: "1.1.0"
```

### Migrate to Role-Based Specs (Optional but Recommended)

**v1.0 Style (still supported):**
```yaml
visualization:
  chart_type: "scatter"
  x_field: "amount"
  y_field: "time"
  color_field: "class"
```

**v1.1 Style (recommended):**
```yaml
visualization:
  chart_type: "scatter"
  roles:
    x: "amount"
    y: "time"
    color: "class"
  params:
    trendline: "ols"
    alpha: 0.7
```

## New Visualization Types

### Level 0: Tables & Summaries

#### Summary Statistics

```yaml
visualization:
  chart_type: "summary"
  params:
    columns: ["amount", "v1", "v2"]
    by: "class"  # Group by field (optional)
    percentiles: [25, 50, 75]
```

### Level 1: Distributions

#### ECDF (Empirical Cumulative Distribution)

```yaml
visualization:
  chart_type: "ecdf"
  roles:
    x: "amount"
    by: "class"  # Optional grouping
```

#### Violin Plot

```yaml
visualization:
  chart_type: "violin"
  roles:
    y: "amount"
    by: "class"
  params:
    inner: "box"  # Options: box, quartiles, points
```

#### Kernel Density Estimate

```yaml
visualization:
  chart_type: "kde"
  roles:
    x: "amount"
    by: "class"
  params:
    bandwidth: 0.5  # Optional
```

### Level 2: Relationships

#### Hexbin (2D Histogram)

```yaml
visualization:
  chart_type: "hexbin"
  roles:
    x: "v1"
    y: "v2"
  params:
    bins: 30
```

#### 2D Kernel Density

```yaml
visualization:
  chart_type: "kde2d"
  roles:
    x: "v1"
    y: "v2"
```

#### Enhanced Scatter with Trendline

```yaml
visualization:
  chart_type: "scatter"
  roles:
    x: "v1"
    y: "v2"
    color: "class"
    size: "amount"
  params:
    trendline: "ols"  # Options: ols, loess, none
    alpha: 0.6
```

### Level 3: Time Series & Categoricals

#### Correlation Heatmap

```yaml
visualization:
  chart_type: "corr_heatmap"
  params:
    columns: ["v1", "v2", "v3", "amount"]
    method: "pearson"  # Options: pearson, spearman, kendall
    mask_upper: true
```

## Code Generation

### Auto-Generate Dashboard Code

DashSpec v1.1 can generate Python code from your specifications:

```bash
# Generate renderer class
python -m dsl.codegen generate spec.yaml output.py CustomRenderer

# The generated file includes:
# - DSL version metadata
# - Regeneration instructions
# - Customization hooks
```

### Generated Code Structure

```python
"""
AUTO-GENERATED CODE - DO NOT MODIFY

DSL Version: 1.1.0
Generated: 2025-01-10T...
Spec Hash: abc123...

To Regenerate:
    python -m dsl.codegen generate spec.yaml output.py
"""

class GeneratedRenderer:
    DSL_VERSION = "1.1.0"
    GENERATED_AT = "2025-01-10T..."

    # Customization hooks
    CUSTOM_RENDERERS = {}
    CUSTOM_TRANSFORMS = []
    CUSTOM_VALIDATORS = []

    # ... generated methods ...
```

### Benefits of Generated Code

1. **Version Tracking** - Know exactly which DSL version generated the code
2. **Regeneration Guidance** - Clear instructions for updating
3. **Custom Overrides** - Extension points for custom behavior
4. **No Manual Sync** - Regenerate when spec changes

## Custom Renderers

### Creating Custom Visualizations

1. **Copy the template:**
   ```bash
   cp dsl/custom_renderers_template.py dsl/custom_renderers.py
   ```

2. **Implement your renderer:**
   ```python
   def render_custom_gauge(df, viz, st_module):
       """Custom gauge chart"""
       value = df[viz['roles']['value']].iloc[0]
       max_val = viz.get('params', {}).get('max', 100)

       fig = go.Figure(go.Indicator(
           mode="gauge+number",
           value=value,
           gauge={'axis': {'range': [None, max_val]}}
       ))
       st_module.plotly_chart(fig)

   # Register
   CUSTOM_RENDERERS['gauge'] = render_custom_gauge
   ```

3. **Use in your spec:**
   ```yaml
   visualization:
     chart_type: "gauge"
     roles:
       value: "total_amount"
     params:
       max: 10000
   ```

### Custom Data Transforms

Add custom data transformations that run before rendering:

```python
def custom_transform_outliers(page):
    """Remove outliers from data"""
    # Your logic here
    return page

CUSTOM_TRANSFORMS.append(custom_transform_outliers)
```

### Custom Validators

Add custom validation rules:

```python
def custom_validator_min_rows(spec, df):
    """Ensure minimum row count"""
    violations = []
    if len(df) < 100:
        violations.append({
            "code": "INSUFFICIENT_DATA",
            "message": f"Only {len(df)} rows, need 100+",
            "path": "/data",
            "repair": "Add more data"
        })
    return violations

CUSTOM_VALIDATORS.append(custom_validator_min_rows)
```

## Migration Strategy

### Recommended Approach

1. **Test with v1.0 specs** - Ensure backward compatibility
2. **Update dsl_version** - Change to "1.1.0"
3. **Add new features gradually** - Use new chart types where beneficial
4. **Migrate to role-based specs** - For better clarity (optional)
5. **Regenerate code** - If using code generation

### Rollback Plan

If issues arise:
1. Change `dsl_version` back to "1.0.0"
2. Remove v1.1-specific features
3. Use legacy field-based specs

## Best Practices

### 1. Use Role-Based Specs

```yaml
# ✅ Good - Clear and semantic
roles:
  x: "amount"
  y: "time"
  color: "class"

# ❌ Avoid - Less clear
x_field: "amount"
y_field: "time"
color_field: "class"
```

### 2. Leverage Params for Configuration

```yaml
# ✅ Good - Organized parameters
visualization:
  chart_type: "histogram"
  roles: {x: "amount"}
  params:
    bins: 50
    log_x: true
    show_marginal: true
```

### 3. Document Custom Renderers

```python
def render_custom_chart(df, viz, st_module):
    """
    Custom chart description

    Roles:
        x: primary dimension
        y: secondary dimension

    Params:
        threshold: cutoff value (default: 0.5)
        show_legend: display legend (default: true)
    """
    pass
```

### 4. Version Your Specs

```yaml
# Always specify exact version
dsl_version: "1.1.0"  # ✅ Good
# dsl_version: "1.1"  # ❌ Avoid - be specific
```

### 5. Use Code Generation for Production

```bash
# Generate production code
python -m dsl.codegen generate dashboard.yaml \
    generated/dashboard_v1.py DashboardV1

# Commit generated code to version control
# Regenerate when spec changes
```

## Troubleshooting

### Chart Type Not Found

**Error:** `Unknown chart type: 'custom_chart'`

**Solution:**
1. Check chart type spelling
2. Verify it's in supported list: `list_supported_charts()`
3. For custom charts, ensure `dsl/custom_renderers.py` exists
4. Check `CUSTOM_RENDERERS` registration

### Role Field Missing

**Error:** `Histogram requires 'x' role`

**Solution:**
```yaml
# Ensure required roles are provided
visualization:
  chart_type: "histogram"
  roles:
    x: "amount"  # ✅ Required role provided
```

### Custom Renderer Not Loading

**Solution:**
1. Verify file name: `dsl/custom_renderers.py` (not `_template.py`)
2. Check syntax errors in custom_renderers.py
3. Ensure registration: `CUSTOM_RENDERERS['type'] = function`

### Version Mismatch

**Error:** `DSL version 2.0.0 not supported`

**Solution:**
```yaml
# Use supported version
dsl_version: "1.1.0"  # Supported: 1.0.x, 1.1.x
```

## Examples

### Complete Enhanced Dashboard

See: `dsl/examples/enhanced_fraud_analysis.yaml`

This example demonstrates:
- Role-based specifications
- New chart types (ECDF, violin, hexbin)
- Enhanced parameters
- Multiple pages with different visualization types

### Custom Renderer Example

See: `dsl/custom_renderers_template.py`

Includes examples for:
- Custom metric cards
- Annotated heatmaps
- Data transforms
- Custom validators

## API Reference

### Supported Chart Types (v1.1)

**Level 0-1:** `table`, `summary`, `histogram`, `ecdf`, `boxplot`, `violin`, `kde`

**Level 2:** `scatter`, `hexbin`, `kde2d`

**Level 3:** `line`, `bar`, `heatmap`, `corr_heatmap`, `pie`

### Renderer Function Signature

```python
def render_chart(df: pd.DataFrame, viz: Dict[str, Any], st_module) -> None:
    """
    Args:
        df: Filtered and sorted DataFrame
        viz: Visualization specification with roles/params
        st_module: Streamlit module for rendering
    """
    pass
```

### Common Roles

- `x`: Primary dimension (usually horizontal axis)
- `y`: Secondary dimension (usually vertical axis)
- `color`: Color encoding field
- `size`: Size encoding field
- `by`: Grouping/faceting field
- `time`: Time dimension for time series

### Common Params

- `bins`: Number of bins (histograms, hexbin)
- `log_x`, `log_y`: Logarithmic scale
- `trendline`: Trend line type (ols, loess)
- `alpha`: Opacity (0-1)
- `method`: Calculation method (pearson, spearman)
- `limit`: Max data points
- `sampling`: Subsample size

## Future Roadmap

### Planned for v1.2

- Model performance visualizations (PR curves, ROC, confusion matrix)
- Advanced time series (resampling, rolling windows)
- Geographic visualizations
- Interactive filtering

### Planned for v2.0

- Multi-dataset support
- Real-time data sources
- Advanced interactivity
- Export capabilities

## Support

- Documentation: `/docs/`
- Examples: `/dsl/examples/`
- Issues: See project repository
- Template: `/dsl/custom_renderers_template.py`
