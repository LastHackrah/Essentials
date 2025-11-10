# DashSpec

**A Declarative DSL for Building Analytics Dashboards**

DashSpec is a YAML-based domain-specific language (DSL) that transforms simple declarative specifications into rich, interactive Streamlit dashboards. Write dashboards in minutes, not hours.

```yaml
# This 15-line spec generates a complete interactive dashboard
dsl_version: "1.3.0"
dashboard:
  title: "Revenue Analytics"
  data_source:
    type: "parquet"
    path: "data/sales.parquet"
  pages:
    - title: "Overview"
      layout:
        components:
          - visualization:
              chart_type: "line"
              roles: { x: "date", y: "revenue", color: "region" }
```

## Key Features

### 🎨 **Declarative Dashboard Design**
- **15+ visualization types**: Line, bar, scatter, histogram, box, violin, heatmap, KDE, ECDF, and more
- **Semantic role mapping**: Use intuitive roles (`x`, `y`, `color`, `size`, `by`) instead of plotting APIs
- **Multi-page layouts**: Organize complex dashboards into logical sections
- **Flexible grid system**: Full-width, half-width, or custom component sizing

### 🚀 **Powerful DSL (v1.3)**
- **Default formatting**: Define formatting once, apply everywhere via inheritance
- **Rich metadata**: Dataset context, descriptions, and documentation built-in
- **JSON Schema validation**: Catch errors before rendering
- **Version migration tools**: Automatic upgrade from v1.2 → v1.3

### 📊 **Production-Ready Dashboards**
8 pre-built dashboards across diverse domains demonstrate the DSL's capabilities:

| Domain | Dashboard | Dataset | Key Insights |
|--------|-----------|---------|--------------|
| 🛡️ **Security** | [Fraud Detection](dsl/examples/fraud_detection.yaml) | 284K credit card transactions | Anomaly patterns, class imbalance, feature importance |
| 🎵 **Entertainment** | [Spotify Analytics](dsl/examples/spotify_tracks.yaml) | 114K tracks | Audio features, popularity trends, artist analysis |
| 🌍 **Environmental** | [Air Quality](dsl/examples/us_pollution.yaml) | 1.7M AQI readings | Pollutant distributions, geographic patterns, temporal trends |
| 🛒 **E-commerce** | [Amazon Reviews](dsl/examples/amazon_reviews.yaml) | 568K reviews | Rating patterns, helpfulness analysis, sentiment insights |
| 👔 **HR Analytics** | [Employee Attrition](dsl/examples/ibm_hr_attrition.yaml) | 1.5K employees | Retention factors, satisfaction drivers, compensation analysis |
| 🚗 **Transportation** | [US Accidents](dsl/examples/us_accidents.yaml) | 7.7M accidents | Severity patterns, weather impact, geographic hotspots |
| 🎬 **Media** | [TMDB Movies](dsl/examples/tmdb_movies.yaml) | 4.8K films | Box office trends, genre profitability, rating distributions |
| 🔒 **Cybersecurity** | [Network Intrusion](dsl/examples/network_intrusion.yaml) | 47K connections | Traffic analysis, protocol patterns, attack detection |

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd dashspec

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Dashboards

```bash
# Option 1: Dashboard gallery (browse all dashboards)
streamlit run app.py

# Option 2: Single dashboard
streamlit run run_dashboard.py -- dsl/examples/fraud_detection.yaml

# Option 3: Use make shortcuts
make dashboard-gallery    # Gallery view
make dashboard-fraud      # Fraud detection
make dashboard-spotify    # Spotify analytics
make help                 # See all options
```

### 3. Create Your Own Dashboard

Create a YAML file in `dsl/examples/`:

```yaml
dsl_version: "1.3.0"

dashboard:
  id: "my_analysis"
  title: "My Data Analysis"

  metadata:
    dataset_name: "My Dataset"
    description: "Insightful analysis of my data"

  # Optional: Define default formatting for all visualizations
  default_formatting:
    numeric:
      format: ",.2f"
    currency:
      format: "$,.0f"

  data_source:
    type: "parquet"
    path: "data/processed/my_data.parquet"

  pages:
    - id: "overview"
      title: "Overview"

      layout:
        type: "grid"
        components:
          # Line chart
          - id: "trend"
            type: "visualization"
            title: "Trend Over Time"
            width: "full"
            visualization:
              chart_type: "line"
              roles:
                x: "date"
                y: "value"
                color: "category"

          # Histogram
          - id: "distribution"
            type: "visualization"
            title: "Value Distribution"
            width: "half"
            visualization:
              chart_type: "histogram"
              roles:
                x: "value"
              config:
                bins: 30

          # Scatter plot
          - id: "correlation"
            type: "visualization"
            title: "Feature Correlation"
            width: "half"
            visualization:
              chart_type: "scatter"
              roles:
                x: "feature1"
                y: "feature2"
                color: "category"
                size: "importance"
```

Then run:
```bash
streamlit run run_dashboard.py -- dsl/examples/my_analysis.yaml
```

## DSL Features

### Supported Visualizations

#### **Distribution Analysis**
- `histogram`: Frequency distributions with customizable bins
- `kde`: Kernel density estimation for smooth distributions
- `ecdf`: Empirical cumulative distribution functions
- `box`: Box plots for quartile analysis
- `violin`: Combined box plot and KDE

#### **Relationship Analysis**
- `scatter`: Bivariate relationships with color/size encoding
- `line`: Time series and trend analysis
- `heatmap`: Correlation matrices and 2D density

#### **Comparison**
- `bar`: Categorical comparisons (vertical)
- `barh`: Horizontal bar charts
- `count`: Frequency counts by category

#### **Tabular**
- `table`: Interactive data tables with search/sort
- `summary_statistics`: Automated statistical summaries

#### **Composition**
- `facet_grid`: Small multiples by category
- Multiple charts per dashboard with flexible layouts

### Role-Based Field Mapping

Instead of specifying plotting parameters, DashSpec uses semantic roles:

```yaml
roles:
  x: "date"           # X-axis variable
  y: "revenue"        # Y-axis variable
  color: "region"     # Color encoding
  size: "population"  # Size encoding (scatter plots)
  by: "category"      # Faceting/grouping variable
```

### Default Formatting (v1.3)

Define formatting once at the dashboard level, automatically inherited by all visualizations:

```yaml
default_formatting:
  numeric:
    format: ",.2f"      # Thousands separator, 2 decimals
  percentage:
    format: ".1%"       # Percentage with 1 decimal
  currency:
    format: "$,.0f"     # Currency with no decimals
  date:
    format: "%Y-%m-%d"  # ISO date format
```

Override at the field level when needed:

```yaml
visualization:
  chart_type: "bar"
  roles:
    x: "product"
    y: "profit"
  field_formats:
    profit:
      format: "$,.2f"   # Override default currency format
```

### Multi-Page Layouts

Organize complex analyses into logical sections:

```yaml
pages:
  - id: "overview"
    title: "Executive Summary"
    layout:
      components: [...]

  - id: "details"
    title: "Detailed Analysis"
    layout:
      components: [...]

  - id: "methodology"
    title: "Data & Methods"
    layout:
      components: [...]
```

## Data Pipeline (Optional)

DashSpec includes an ETL pipeline for processing Kaggle datasets:

```bash
# Configure Kaggle API (see docs/etl_pipeline_guide.md)
# ~/.kaggle/kaggle.json

# Process all datasets
python run_etl.py

# Process specific datasets
python run_etl.py --datasets credit_card_fraud spotify_tracks

# Use deployment config with sampling
python run_etl.py --config config/datasets_deploy.yaml

# Inspect processed data
python inspect_datasets.py --list
python inspect_datasets.py --show credit_card_fraud
```

### Pipeline Features
- **Automated downloads** from Kaggle
- **Smart transformations**: Column standardization, missing value handling, type optimization
- **Data profiling**: Comprehensive statistics and quality metrics
- **Efficient storage**: Parquet format with Snappy compression
- **Deployment sampling**: Configurable sampling strategies for cloud deployment

## Project Structure

```
dashspec/
├── dsl/
│   ├── examples/              # 14 dashboard specifications
│   ├── schemas/               # JSON schemas (v1.0, v1.1, v1.2, v1.3)
│   ├── core/                  # DSL core (parser, validators)
│   └── renderers/             # Rendering engines
│       └── streamlit/         # Streamlit renderer
├── etl/                       # ETL pipeline modules
│   ├── config.py              # Configuration models
│   ├── extractor.py           # Kaggle downloader
│   ├── transformer.py         # Data transformations
│   ├── sampler.py             # Sampling strategies
│   ├── loader.py              # Parquet writer
│   └── pipeline.py            # Pipeline orchestrator
├── config/
│   ├── datasets.yaml          # Full dataset configuration
│   └── datasets_deploy.yaml   # Deployment config with sampling
├── data/
│   ├── processed/             # Parquet files (122MB)
│   └── metadata/              # Dataset metadata
├── app.py                     # Dashboard gallery
├── run_dashboard.py           # Single dashboard runner
├── run_etl.py                 # ETL pipeline runner
└── tests/                     # Test suite
```

## Documentation

- **[DSL Guide](docs/dsl_guide.md)**: Complete DSL reference with examples
- **[ETL Pipeline Guide](docs/etl_pipeline_guide.md)**: Data processing workflow
- **[Migration Guide](docs/migration_v1.2_to_v1.3.md)**: Upgrading dashboards to v1.3
- **[Data Sources](docs/datasources.md)**: Available datasets and descriptions

## Advanced Usage

### Validation

Validate dashboard specs before rendering:

```bash
python -c "from dsl.core.validators import validate_dashboard_spec; \
          validate_dashboard_spec('dsl/examples/my_dashboard.yaml')"
```

### Migration

Upgrade v1.2 dashboards to v1.3 with default formatting:

```bash
python scripts/migrate_v1.2_to_v1.3.py dsl/examples/old_dashboard.yaml
```

### Custom Renderers

DashSpec's modular architecture allows custom rendering backends:

```python
from dsl.core.parser import DashboardParser
from dsl.renderers.streamlit.renderer import StreamlitRenderer

# Parse dashboard spec
parser = DashboardParser()
dashboard_ir = parser.parse("my_dashboard.yaml")

# Render with Streamlit
renderer = StreamlitRenderer()
renderer.render(dashboard_ir)
```

## Example: Complete Dashboard

See [fraud_detection.yaml](dsl/examples/fraud_detection.yaml) for a production-ready example featuring:
- Multi-page layout (Overview, Patterns, Correlations)
- 8 different visualization types
- Default formatting with field-level overrides
- Rich metadata and documentation
- Advanced chart configurations

## Testing

```bash
# Run all tests
make test

# Run specific test suites
pytest tests/test_dsl_v13.py          # DSL v1.3 tests
pytest tests/test_formatting.py       # Formatting tests
pytest tests/test_dashboards_v13.py   # Dashboard integration tests

# Run with coverage
make test-coverage
```

## Deployment

Ready for Streamlit Cloud deployment:
- **122MB** processed data (sampled for cloud limits)
- **Streamlit configuration** included (`.streamlit/config.toml`)
- **Requirements.txt** with pinned versions
- **No external dependencies** beyond Python packages

## Contributing

Contributions welcome! Areas of interest:
- New visualization types
- Additional rendering backends (Plotly Dash, Bokeh, etc.)
- Enhanced validation and error messages
- Dashboard templates for specific domains

## License

See [LICENSE](LICENSE) for details.

---

**Built with:** Python 3.11+ • Streamlit • Pandas • Plotly • Pydantic
