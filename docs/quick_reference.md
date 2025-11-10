# ETL Pipeline Quick Reference

## Common Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure Kaggle API (one-time setup)
# Place kaggle.json in ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

### Running Pipeline
```bash
# Process all datasets
python run_etl.py

# Process one dataset
python run_etl.py --datasets credit_card_fraud

# Process multiple datasets
python run_etl.py --datasets credit_card_fraud us_accidents spotify_tracks

# Reprocess existing
python run_etl.py --no-skip-existing

# Debug mode
python run_etl.py --verbose
```

### Inspecting Data
```bash
# List all processed datasets
python inspect_datasets.py --list

# View dataset info
python inspect_datasets.py --dataset credit_card_fraud

# View specific column
python inspect_datasets.py --dataset credit_card_fraud --column amount
```

## Available Datasets

| Name | Kaggle ID | Category |
|------|-----------|----------|
| `credit_card_fraud` | mlg-ulb/creditcardfraud | Fraud Detection |
| `amazon_food_reviews` | snap/amazon-fine-food-reviews | Sentiment Analysis |
| `us_pollution` | sogun3/uspollution | Air Quality |
| `ibm_hr_attrition` | pavansubhasht/ibm-hr-analytics-attrition-dataset | Employee Retention |
| `power_consumption` | uciml/electric-power-consumption-data-set | Energy Forecasting |
| `us_accidents` | sobhanmoosavi/us-accidents | Traffic Analysis |
| `tmdb_movies` | tmdb/tmdb-movie-metadata | Movie Analysis |
| `network_intrusion` | sampadab17/network-intrusion-detection | Cybersecurity |
| `spotify_tracks` | maharshipandya/-spotify-tracks-dataset | Music Analysis |

## Using Parquet Files

### Python
```python
import pandas as pd

# Read Parquet file
df = pd.read_parquet('data/processed/credit_card_fraud.parquet')

# Read specific columns
df = pd.read_parquet('data/processed/credit_card_fraud.parquet',
                     columns=['amount', 'class'])
```

### Using the Loader
```python
from etl.config import load_config
from etl.loader import ParquetLoader

config = load_config()
loader = ParquetLoader(
    config.processed_data_dir,
    config.metadata_dir,
    config.compression
)

# Load dataset
df = loader.load_parquet('credit_card_fraud')

# Load metadata
metadata = loader.load_metadata('credit_card_fraud')
```

## File Locations

- **Configuration**: `config/datasets.yaml`
- **Raw data**: `data/raw/{dataset_name}/`
- **Processed data**: `data/processed/{dataset_name}.parquet`
- **Metadata**: `data/metadata/{dataset_name}_metadata.json`
- **Logs**: `logs/etl_pipeline.log`

## Adding New Datasets

1. Edit `config/datasets.yaml`
2. Add new entry:
   ```yaml
   - name: my_dataset
     kaggle_id: username/dataset-name
     description: My Dataset
     project_category: my_category
     url: https://www.kaggle.com/datasets/username/dataset-name
     enabled: true
   ```
3. Run pipeline: `python run_etl.py --datasets my_dataset`

## Troubleshooting

### Kaggle API Not Found
```bash
# Install kaggle package
pip install kaggle

# Set up credentials
mkdir -p ~/.kaggle
cp /path/to/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Dataset Not Found (404)
- Verify kaggle_id in config/datasets.yaml
- Check dataset exists on Kaggle
- Accept dataset terms on Kaggle website

### Memory Error
```bash
# Process datasets one at a time
python run_etl.py --datasets credit_card_fraud
```

## Pipeline Components

| Module | Purpose |
|--------|---------|
| `etl/config.py` | Configuration management |
| `etl/extractor.py` | Kaggle API downloads |
| `etl/transformer.py` | Data transformations |
| `etl/loader.py` | Parquet file operations |
| `etl/pipeline.py` | Pipeline orchestration |

## Data Transformations

The pipeline automatically:
1. Standardizes column names (lowercase, underscores)
2. Handles missing values (drops >50% missing columns)
3. Optimizes data types (categorical, downcasting)
4. Removes duplicates
5. Adds metadata columns

## Next Steps

After processing:
1. Use `inspect_datasets.py` to explore data
2. Load Parquet files in Jupyter notebooks
3. Build dashboards with processed data
4. Use metadata files for documentation
