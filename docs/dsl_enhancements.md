# DSL Enhancement Guide

This document outlines potential enhancements to the DashSpec DSL, organized by complexity level and use case.

## Level 0 — Tabular & Summaries

### 0.1 Data Table

**Purpose**: Inspect rows; slice/filter/sort

**Roles**:
- `dataframe`: Source dataframe

**Parameters**:
- **Required**: None
- **Optional**: `columns[]`, `sort_by`, `limit`, `filters[]`

**Validation**:
- Selected columns exist in dataframe

**Notes**:
- Enable row count display
- Show dtype badges for columns

### 0.2 Summary Statistics

**Purpose**: Descriptive statistics

**Roles**:
- `dataframe`: Source dataframe

**Parameters**:
- **Required**: `columns[]`
- **Optional**: `by` (group-by field), `percentiles[]`

**Validation**:
- Numeric columns for numeric statistics
- Categorical columns for count statistics

---

## Level 1 — Distributions

### 1.1 Histogram

**Purpose**: Univariate distribution

**Roles**:
- `x`: Distribution variable

**Parameters**:
- **Required**: `x`
- **Optional**: `bins`, `log_x`, `by` (facet or color)

**Validation**:
- `x` must be numeric (or treat categorical as count)

### 1.2 ECDF (Empirical CDF)

**Purpose**: Compare distributions, show tails

**Roles**:
- `x`: Distribution variable

**Parameters**:
- **Required**: `x`
- **Optional**: `by` (grouping variable)

**Validation**:
- `x` must be numeric

### 1.3 Box Plot

**Purpose**: Spread & outliers per group

**Roles**:
- `y`: Numeric variable
- `by`: Categorical grouping variable

**Parameters**:
- **Required**: `y`
- **Optional**: `by`, `whisker_method`

**Validation**:
- `y` must be numeric
- `by` must be categorical

### 1.4 Violin Plot

**Purpose**: Density + quantiles per group

**Roles**:
- `y`: Numeric variable
- `by`: Categorical grouping variable

**Parameters**:
- **Required**: `y`
- **Optional**: `by`, `inner` (quartiles display)

**Validation**:
- `y` must be numeric

### 1.5 KDE Density (1D)

**Purpose**: Smooth distribution

**Roles**:
- `x`: Distribution variable

**Parameters**:
- **Required**: `x`
- **Optional**: `bandwidth`, `by`

**Validation**:
- `x` must be numeric
- Adequate sample size (N > 30 recommended)

---

## Level 2 — Relationships

### 2.1 Scatter Plot

**Purpose**: Relationship between two variables

**Roles**:
- `x`: Independent variable
- `y`: Dependent variable

**Parameters**:
- **Required**: `x`, `y`
- **Optional**: `color`, `size`, `trendline` (ols/loess), `alpha`

**Validation**:
- `x`, `y` must be numeric
- If `size` provided, must be numeric

### 2.2 Hexbin / 2D Histogram

**Purpose**: Dense scatter aggregation

**Roles**:
- `x`: First dimension
- `y`: Second dimension

**Parameters**:
- **Required**: `x`, `y`
- **Optional**: `bins`, `agg` (count/mean/median of z)

**Validation**:
- `x`, `y` must be numeric

### 2.3 2D KDE

**Purpose**: Smooth joint density

**Roles**:
- `x`: First dimension
- `y`: Second dimension

**Parameters**:
- **Required**: `x`, `y`
- **Optional**: `levels`, `bandwidth`

**Validation**:
- `x`, `y` must be numeric
- Sample size N > 200 recommended

---

## Level 3 — Time & Categoricals

### 3.1 Time Series Line

**Purpose**: Trends over time

**Roles**:
- `time`: Time axis
- `y`: Value axis

**Parameters**:
- **Required**: `time`, `y`
- **Optional**: `by`, `rolling_window`, `resample` (e.g., "1H", "1D")

**Validation**:
- `time` parseable as datetime or numeric seconds

### 3.2 Aggregated Bar/Column

**Purpose**: Totals per category

**Roles**:
- `x`: Category
- `y`: Numeric aggregation

**Parameters**:
- **Required**: `x`, `agg` (count/sum/mean on target column)
- **Optional**: `stack_by`, `sort`

**Validation**:
- `x` must be categorical

### 3.3 Heatmap (Pivot)

**Purpose**: 2D aggregation table

**Roles**:
- `x`: Category (columns)
- `y`: Category (rows)
- `z`: Numeric aggregation value

**Parameters**:
- **Required**: `x`, `y`, `z`, `agg`
- **Optional**: `norm` (row/col normalization), `annot` (show values)

**Validation**:
- `z` must be numeric
- Handle sparse combinations gracefully

### 3.4 Correlation Matrix Heatmap

**Purpose**: Linear correlation overview

**Roles**:
- `columns[]`: Columns to correlate

**Parameters**:
- **Required**: `columns[]`
- **Optional**: `method` (pearson/spearman), `mask_upper`

**Validation**:
- All columns must be numeric

---

## Level 4 — Model & Performance

*(Great for fraud detection datasets)*

### 4.1 Precision-Recall Curve (PR)

**Purpose**: Classifier quality under imbalance

**Roles**:
- `y_true`: True labels
- `y_score`: Predicted scores

**Parameters**:
- **Required**: `y_true`, `y_score`
- **Optional**: `baseline` (positive rate), `area` (AUPRC)

**Validation**:
- Labels must be 0/1
- Scores must be in [0,1]

### 4.2 ROC Curve

**Purpose**: TPR-FPR tradeoff

**Roles**:
- `y_true`: True labels
- `y_score`: Predicted scores

**Parameters**:
- **Required**: `y_true`, `y_score`
- **Optional**: `area` (AUROC)

**Validation**:
- Same as PR curve

### 4.3 Threshold Sweep Table

**Purpose**: Metrics by threshold grid

**Roles**:
- `y_true`: True labels
- `y_score`: Predicted scores

**Parameters**:
- **Required**: `y_true`, `y_score`
- **Optional**: `thresholds[]` or `n_thresholds`

**Validation**:
- Compute precision, recall, F1, specificity
- Mark optimal threshold

### 4.4 Confusion Matrix @ Threshold

**Purpose**: TP/FP/FN/TN at chosen operating point

**Roles**:
- `y_true`: True labels
- `y_score`: Predicted scores

**Parameters**:
- **Required**: `y_true`, `y_score`, `threshold`
- **Optional**: `normalize` (true/pred/all)

**Validation**:
- Threshold must be in [0,1]

### 4.5 Calibration Curve

**Purpose**: Reliability of predicted probabilities

**Roles**:
- `y_true`: True labels
- `y_score`: Predicted scores

**Parameters**:
- **Required**: `y_true`, `y_score`
- **Optional**: `n_bins`

**Validation**:
- Ensure enough positives per bin

### 4.6 Lift / Cumulative Gains

**Purpose**: Prioritization power by score

**Roles**:
- `y_true`: True labels
- `y_score`: Predicted scores

**Parameters**:
- **Required**: `y_true`, `y_score`
- **Optional**: `bins` (deciles/percentiles)

**Validation**:
- Monotonic ordering by score

### 4.7 PR by Segment

**Purpose**: Fairness/segment performance analysis

**Roles**:
- `y_true`: True labels
- `y_score`: Predicted scores
- `segment`: Segmentation variable

**Parameters**:
- **Required**: `y_true`, `y_score`, `segment`
- **Optional**: `top_k` segments by volume

**Validation**:
- Per-segment support ≥ N_min

---

## Level 5 — Multivariate Structure

### 5.1 PCA Biplot

**Purpose**: Low-dimensional projection + loadings

**Roles**:
- `X_columns[]`: Numeric columns for PCA
- `components`: Precomputed or compute on-the-fly

**Parameters**:
- **Required**: List of numeric columns
- **Optional**: `color`, `scale`

**Validation**:
- Standardize data
- Show explained variance

### 5.2 Feature Importance Bar

**Purpose**: Explain model drivers

**Roles**:
- `feature`: Feature names
- `importance`: Importance values

**Parameters**:
- **Required**: Table of importances
- **Optional**: `top_k`

**Validation**:
- Sum to 1 if normalized

### 5.3 Parallel Coordinates

**Purpose**: Compare many features across classes

**Roles**:
- `columns[]`: Numeric columns
- `color`: Class/category variable

**Parameters**:
- **Required**: Numeric columns
- **Optional**: `sampling` to maintain performance

**Validation**:
- Scale features to comparable ranges

---

## Level 6 — Advanced Density/Structure

### 6.1 UMAP/t-SNE Scatter

**Purpose**: Visual cluster structure

**Roles**:
- `x`: First embedding dimension
- `y`: Second embedding dimension
- `color`: Class/category variable

**Parameters**:
- **Required**: Columns for 2D embedding
- **Optional**: `alpha`, `size`

**Validation**:
- Advise subsampling for > 100k points

### 6.2 2D Density-by-Time Heatmap

**Purpose**: Activity intensity over time & another axis

**Roles**:
- `time`: Time dimension
- `y`: Second dimension
- `agg`: Aggregation function

**Parameters**:
- **Required**: `time`, `y`, aggregation on count or amount
- **Optional**: `resample`, `bins`

**Validation**:
- Align resampling and binning

---

## Minimal DSL Schema Pattern

Your DSL can declare visuals like this (YAML):

```yaml
visuals:
  - id: tx_table
    kind: table
    source: main
    params:
      columns: ["Time", "Amount", "Class"]
      limit: 1000

  - id: amount_hist
    kind: histogram
    source: main
    roles: { x: "Amount" }
    params: { bins: 50, log_x: false }

  - id: amount_by_class_box
    kind: boxplot
    source: main
    roles: { y: "Amount", by: "Class" }

  - id: pr_curve
    kind: pr_curve
    source: scored   # a view with y_true, y_score
    roles: { y_true: "Class", y_score: "score" }
    params: { show_baseline: true }

  - id: corr_heatmap
    kind: corr_heatmap
    source: main
    params:
      columns: ["V1", "V2", "V3", "Amount"]
      method: "pearson"
```

## Validation Contract

Each visual should have a contract:

```yaml
visual_contract:
  required_roles: ["x", "y_true", ...]
  required_params: []
  role_types: { x: "numeric", by: "categorical" }
```

## Python Adapter Implementation

The Python adapter should:

1. **Check roles exist and types match**
2. **Apply optional transforms** (e.g., resampling, rolling)
3. **Render with chosen backend** (matplotlib/Altair/Plotly/Streamlit)
4. **Emit structured errors** as `{code, path, message, repair}`

Error codes:
- `ROLE_MISSING`
- `ROLE_TYPE_MISMATCH`
- `PARAM_INVALID`
- `INSUFFICIENT_SUPPORT`

### Type Definitions

```python
class VisualSpec(TypedDict, total=False):
    id: str
    kind: str
    source: str
    roles: dict[str, str]
    params: dict[str, Any]

def validate_visual(
    spec: VisualSpec,
    df_map: dict[str, pd.DataFrame]
) -> list[Violation]:
    ...

def render_visual(
    spec: VisualSpec,
    df_map: dict[str, pd.DataFrame]
) -> None:  # draws in Streamlit
    ...
```

## Suggested Chart Types Enum

Implement incrementally:

```python
CHART_TYPES = [
    # Level 0-1
    "table", "summary", "histogram", "ecdf", "boxplot", "violin", "kde1d",

    # Level 2
    "scatter", "hexbin", "kde2d",

    # Level 3
    "line", "bar", "heatmap", "corr_heatmap",

    # Level 4 (Model metrics)
    "pr_curve", "roc_curve", "threshold_sweep", "confusion_matrix",
    "calibration", "lift_curve", "segment_pr",

    # Level 5-6
    "pca_biplot", "feature_importance", "parallel_coords",
    "umap_scatter", "density_time_heatmap"
]
```

## Domain Example: Fraud Dataset

Quick mappings for fraud detection:

### Tables
- Recent transactions
- Top amounts
- Suspected frauds (score > τ)

### Distributions
- Histogram/violin of `Amount` by `Class`

### Relationships
- Scatter of `V1` vs `V2` colored by `Class`
- Hexbin for density visualization

### Time Series
- `Time` vs count (resample='1H')
- Separate traces by `Class`

### Model Metrics
- PR/ROC curves (requires `y_score`)
- Threshold sweep & confusion matrix at chosen τ
- Calibration curve
- Lift/gains curves
- PR by Amount decile

### Heatmaps
- Correlations among V1..V28 + Amount
- Pivot of hour-of-day × day-index fraud rate

---

## Implementation Tip

**Start with Level 0-3** (tables, histogram, box/violin, line, bar, heatmap, correlation) to cover 80% of needs.

**Then add Level 4** (PR/ROC/etc.) for the fraud use-case.

**Keep each renderer < 100 LoC** and gate them behind the validation contract above.

---

## Priority Recommendations

1. **Phase 1**: Level 0-1 (tables, histograms, box plots) ✅ *Partially implemented*
2. **Phase 2**: Level 3 time series + aggregated bars
3. **Phase 3**: Level 4 model performance metrics (critical for fraud detection)
4. **Phase 4**: Level 2 relationship charts (scatter enhancements, hexbin, KDE)
5. **Phase 5**: Level 5-6 advanced visualizations
