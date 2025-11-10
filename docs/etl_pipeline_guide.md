# ETL Pipeline Guide

## Overview

This generalized ETL pipeline downloads, transforms, and saves Kaggle datasets as Parquet files. The pipeline takes advantage of Kaggle metadata artifacts and applies standardized transformations to ensure data quality and consistency.

## Features

- **Automated Downloads**: Downloads datasets directly from Kaggle API
- **Metadata Extraction**: Extracts and stores Kaggle metadata artifacts
- **Data Transformation**:
  - Standardizes column names
  - Handles missing values intelligently
  - Optimizes data types for memory efficiency
  - Removes duplicates
  - Adds tracking metadata
- **Parquet Output**: Saves processed data in efficient Parquet format with compression
- **Data Profiling**: Generates comprehensive data profiles for each dataset
- **Logging**: Detailed logging to both console and file

## Prerequisites

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Kaggle API

You need Kaggle API credentials to download datasets. Follow these steps:

1. Create a Kaggle account at [kaggle.com](https://www.kaggle.com)
2. Go to your account settings: https://www.kaggle.com/account
3. Scroll to "API" section and click "Create New API Token"
4. This downloads `kaggle.json` with your credentials
5. Place the file in the appropriate location:
   - **Linux/Mac**: `~/.kaggle/kaggle.json`
   - **Windows**: `C:\Users\<username>\.kaggle\kaggle.json`
6. Set permissions (Linux/Mac only):
   ```bash
   chmod 600 ~/.kaggle/kaggle.json
   ```

## Project Structure

```
Essentials/
├── config/
│   └── datasets.yaml          # Dataset configuration
├── data/
│   ├── raw/                   # Downloaded raw data
│   ├── processed/             # Processed Parquet files
│   └── metadata/              # Dataset metadata
├── docs/
│   ├── datasources.md         # Dataset source information
│   └── etl_pipeline_guide.md  # This guide
├── etl/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── extractor.py           # Kaggle API and download logic
│   ├── transformer.py         # Data transformation logic
│   ├── loader.py              # Parquet file operations
│   └── pipeline.py            # Main pipeline orchestration
├── logs/
│   └── etl_pipeline.log       # Pipeline logs
├── run_etl.py                 # Main pipeline runner
├── inspect_datasets.py        # Dataset inspection utility
└── requirements.txt           # Python dependencies
```

## Usage

### Running the Pipeline

#### Process All Datasets

```bash
python run_etl.py
```

#### Process Specific Datasets

```bash
python run_etl.py --datasets credit_card_fraud us_accidents
```

#### Force Reprocess Existing Datasets

```bash
python run_etl.py --no-skip-existing
```

#### Verbose Output

```bash
python run_etl.py --verbose
```

### Inspecting Processed Data

#### List All Processed Datasets

```bash
python inspect_datasets.py --list
```

#### View Dataset Details

```bash
python inspect_datasets.py --dataset credit_card_fraud
```

#### View Column Information

```bash
python inspect_datasets.py --dataset credit_card_fraud --column amount
```

## Configuration

### Dataset Configuration (`config/datasets.yaml`)

The dataset configuration file defines all datasets to be processed:

```yaml
datasets:
  - name: credit_card_fraud              # Internal dataset name
    kaggle_id: mlg-ulb/creditcardfraud  # Kaggle dataset identifier
    description: Credit Card Fraud Detection
    project_category: fraud_detection
    url: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
    enabled: true                        # Set to false to skip
```

### Adding New Datasets

1. Open `config/datasets.yaml`
2. Add a new entry under `datasets:`
3. Run the pipeline

Example:

```yaml
  - name: my_new_dataset
    kaggle_id: username/dataset-name
    description: My New Dataset
    project_category: my_category
    url: https://www.kaggle.com/datasets/username/dataset-name
    enabled: true
```

## Data Transformations

The pipeline applies the following transformations automatically:

### 1. Column Name Standardization
- Converts to lowercase
- Replaces spaces with underscores
- Removes special characters
- Example: `Transaction Amount` → `transaction_amount`

### 2. Missing Value Handling
- Identifies columns with >50% missing values
- Logs missing value percentages
- Drops extremely sparse columns

### 3. Data Type Optimization
- Attempts numeric conversion for object columns
- Attempts datetime conversion where appropriate
- Converts low-cardinality columns to categorical
- Downcasts numeric types to save memory

### 4. Duplicate Removal
- Identifies and removes exact duplicate rows
- Logs number of duplicates removed

### 5. Metadata Addition
- Adds `_dataset_name` column for tracking
- Adds `_dataset_category` column for categorization

## Output Files

### Parquet Files
- Location: `data/processed/`
- Format: `{dataset_name}.parquet`
- Compression: Snappy (default)
- Features:
  - Columnar storage format
  - High compression ratio
  - Fast read/write performance
  - Schema preservation

### Metadata Files
- Location: `data/metadata/`
- Format: `{dataset_name}_metadata.json`
- Contents:
  - Kaggle dataset information
  - File list and sizes
  - Data profile (statistics, dtypes, missing values)
  - Column-level statistics

## Reading Parquet Files

### Using Pandas

```python
import pandas as pd

# Read Parquet file
df = pd.read_parquet('data/processed/credit_card_fraud.parquet')

# Read with specific columns
df = pd.read_parquet(
    'data/processed/credit_card_fraud.parquet',
    columns=['amount', 'class']
)
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

## Troubleshooting

### Kaggle API Authentication Error

**Error**: `OSError: Could not find kaggle.json`

**Solution**: Ensure `kaggle.json` is in the correct location with proper permissions (see Prerequisites)

### Dataset Not Found

**Error**: `404 - Not Found`

**Solution**:
- Verify the `kaggle_id` in `config/datasets.yaml`
- Check that the dataset exists on Kaggle
- Ensure you have accepted the dataset's terms on Kaggle website

### Memory Error

**Error**: `MemoryError` or system runs out of RAM

**Solution**:
- Process datasets one at a time: `python run_etl.py --datasets dataset_name`
- Reduce `chunk_size` in `config/datasets.yaml`
- Close other applications to free up memory

### No CSV Files Found

**Error**: `No CSV files found in {directory}`

**Solution**:
- Some Kaggle datasets may contain only JSON, Excel, or other formats
- Check the downloaded files in `data/raw/{dataset_name}/`
- Modify `etl/extractor.py` to support additional file formats if needed

## Performance Tips

1. **Parallel Processing**: The pipeline processes datasets sequentially by default. For parallel processing, modify `config.max_workers`

2. **Skip Existing**: Use default behavior to skip already processed datasets

3. **Selective Processing**: Process only needed datasets using `--datasets` flag

4. **Monitor Logs**: Check `logs/etl_pipeline.log` for detailed progress

## Extending the Pipeline

### Adding Custom Transformations

Edit `etl/transformer.py` and add your transformation logic to the `transform_dataframe` method:

```python
def transform_dataframe(self, df, dataset_name, metadata):
    # Existing transformations...

    # Add your custom transformation
    df = self._your_custom_transformation(df)

    return df
```

### Supporting Additional File Formats

Edit `etl/extractor.py` to add support for JSON, Excel, etc.:

```python
def get_dataset_files(self, dataset_dir: Path) -> List[Path]:
    csv_files = list(dataset_dir.glob("*.csv"))
    json_files = list(dataset_dir.glob("*.json"))
    excel_files = list(dataset_dir.glob("*.xlsx"))

    return csv_files + json_files + excel_files
```

## Datasets Included

The pipeline is configured to process the following datasets from `docs/datasources.md`:

| Dataset | Kaggle ID | Category |
|---------|-----------|----------|
| Credit Card Fraud Detection | mlg-ulb/creditcardfraud | Fraud Detection |
| Amazon Fine Food Reviews | snap/amazon-fine-food-reviews | Sentiment Analysis |
| Air Quality Data | sogun3/uspollution | Air Quality |
| HR Employee Attrition | pavansubhasht/ibm-hr-analytics-attrition-dataset | Employee Retention |
| Global Power Consumption | uciml/electric-power-consumption-data-set | Energy Forecasting |
| US Traffic Accidents | sobhanmoosavi/us-accidents | Traffic Analysis |
| TMDB Box Office Data | tmdb/tmdb-movie-metadata | Movie Analysis |
| Network Intrusion Detection | sampadab17/network-intrusion-detection | Cybersecurity |
| Spotify Songs Dataset | maharshipandya/-spotify-tracks-dataset | Music Analysis |

## Next Steps

After running the pipeline:

1. **Explore the data**: Use `inspect_datasets.py` to examine processed datasets
2. **Build dashboards**: Use the Parquet files in your dashboard application
3. **Analyze data**: Load Parquet files into Jupyter notebooks for analysis
4. **Share insights**: Use the metadata files for documentation and reporting
