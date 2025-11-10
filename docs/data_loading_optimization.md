# Data Loading Optimization for DashSpec

## Overview

DashSpec includes intelligent data loading optimizations to provide excellent UX when working with large datasets in Streamlit. The system automatically handles caching, sampling, and progress indicators to ensure responsive performance.

## Key Features

### 1. **Automatic Caching**
- All data loads are cached using `@st.cache_data`
- Default TTL: 1 hour (3600 seconds)
- Reduces repeated load times to < 1 second
- Memory-efficient: only loads what's needed

### 2. **Smart Sampling**
Large datasets are automatically sampled for optimal performance while preserving statistical properties:

**Thresholds:**
- **< 100K rows**: Full dataset loaded
- **100K - 1M rows**: Sampled to 50K rows
- **> 1M rows**: Sampled to 100K rows

**Sampling Strategy:**
- Deterministic random sampling (seed=42)
- Preserves temporal ordering where possible
- Maintains statistical representativeness

### 3. **Load Time Estimation**
Before loading, the system shows:
- Dataset size (rows and MB)
- Estimated load time
- Loading strategy (full or sampled)

### 4. **Progress Indicators**
- Spinner with row count during load
- Dataset info after load (expandable)
- Sample percentage displayed if applicable

### 5. **Visualization Limits**
Each visualization can specify a `limit` parameter:
```yaml
visualization:
  chart_type: "scatter"
  roles:
    x: "feature1"
    y: "feature2"
  params:
    limit: 10000  # Sample to 10K rows for this viz
```

## Architecture

### DataLoader Class

Located in `dsl/data_loader.py`, provides:

```python
# Load data with automatic optimization
df, load_info = DataLoader.load_data(
    file_path="data/processed/dataset.parquet",
    max_rows=50000,         # Optional limit
    columns=['col1', 'col2'], # Optional column selection
    force_full_load=False,   # Override sampling
    show_progress=True       # Show loading UI
)

# Display loading information
DataLoader.show_dataset_info(load_info, position="expander")
```

### Integration Points

**1. Adapter (`dsl/adapter.py`)**
- Main data loading happens in `execute()` function
- Uses DataLoader for initial dataset load
- Shows expandable loading info

**2. Viz Renderers (`dsl/viz_renderers.py`)**
- Each renderer calls `apply_limit()` before visualization
- Respects `limit` param in visualization spec
- Uses deterministic sampling for consistency

## Performance Characteristics

### Load Times (Approximate)

| Dataset Size | Full Load | Sampled Load | Memory Usage |
|--------------|-----------|--------------|--------------|
| 100K rows | ~0.2s | N/A (full) | ~10 MB |
| 500K rows | ~1s | ~0.3s | ~25 MB |
| 1M rows | ~2s | ~0.5s | ~50 MB |
| 5M rows | ~10s | ~0.8s | ~80 MB |
| 10M rows | ~20s | ~1s | ~100 MB |

*Note: Times vary based on number of columns and data types*

### Caching Benefits

After first load:
- Subsequent page loads: **< 0.1s**
- Changing filters: **< 0.5s** (apply filters only)
- Switching visualizations: **Instant** (data already in memory)

## Usage Guidelines

### For Dashboard Developers

**1. Always specify limits for heavy visualizations:**
```yaml
# Good: Explicit limit for scatter plot
visualization:
  chart_type: "scatter"
  roles:
    x: "feature1"
    y: "feature2"
  params:
    limit: 10000
    alpha: 0.5
```

**2. Use appropriate limits by chart type:**
- **Tables**: 100-1000 rows
- **Histograms**: 50K-100K rows (already binned)
- **Scatter plots**: 10K-20K rows
- **Hexbin/KDE**: 20K-50K rows (density-based)
- **Box/Violin**: 30K-50K rows

**3. Avoid limits on aggregated visualizations:**
```yaml
# No limit needed - already aggregated
visualization:
  chart_type: "summary"
  params:
    columns: ["col1", "col2"]
    by: "category"
```

### For End Users

**1. Understanding Loading Messages:**
- "Loading X rows..." = Full dataset
- "Loading sample of X rows..." = Sampled dataset
- Loading info shows actual vs total rows

**2. When Sampling is Used:**
- Automatically for datasets > 100K rows
- Per-visualization limits override dataset sampling
- Can see sample % in info expander

**3. Statistical Validity:**
- Samples preserve distribution properties
- Visualizations remain representative
- Aggregations computed on full data where possible

## Advanced Configuration

### Customizing Thresholds

Edit `dsl/data_loader.py`:
```python
class DataLoader:
    LARGE_DATASET_ROWS = 100_000   # Adjust threshold
    HUGE_DATASET_ROWS = 1_000_000  # Adjust threshold
    DEFAULT_SAMPLE_SIZE = 50_000   # Adjust sample size
    CACHE_TTL = 3600               # Adjust cache duration
```

### Force Full Load

For specific dashboards requiring full data:
```python
df, load_info = DataLoader.load_data(
    file_path=data_path,
    force_full_load=True  # Skip automatic sampling
)
```

### Progressive Loading

For loading multiple datasets:
```python
from dsl.data_loader import ProgressiveLoader

items = ['dataset1.parquet', 'dataset2.parquet', 'dataset3.parquet']

for df in ProgressiveLoader.load_with_progress(items, DataLoader.load_data, "Loading datasets"):
    process(df)
```

## Troubleshooting

### Issue: "Out of Memory" errors

**Solution:** Reduce sample sizes or add more aggressive limits:
```python
# In DataLoader class
DEFAULT_SAMPLE_SIZE = 30_000  # Reduce from 50K
LARGE_SAMPLE_SIZE = 60_000    # Reduce from 100K
```

### Issue: Visualizations look different after sampling

**Cause:** Natural variation in random samples

**Solution:**
1. Increase sample size for that visualization
2. Use `force_full_load=True` if needed
3. Use aggregated visualizations (summary, boxplot)

### Issue: Slow initial load despite sampling

**Cause:** Parquet file may not be optimized

**Solution:** Re-process with better compression:
```python
df.to_parquet(
    path,
    compression='snappy',  # Fast compression
    index=False,
    engine='pyarrow'
)
```

## Best Practices

1. **Profile your dashboards**: Test with full-size datasets
2. **Set appropriate limits**: Balance between UX and statistical validity
3. **Use summary stats**: Prefer aggregations over raw data displays
4. **Monitor memory**: Keep dashboard memory < 1GB
5. **Cache aggressively**: Leverage Streamlit's caching
6. **Provide context**: Use expanders to show loading details

## Future Enhancements

Potential improvements:
- **Incremental loading**: Load pages progressively
- **Background loading**: Pre-load next page while viewing current
- **Adaptive sampling**: Adjust sample size based on device capability
- **Smart aggregation**: Pre-compute common aggregations during ETL
- **Streaming**: Support for data streams and real-time updates
