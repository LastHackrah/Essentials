#!/usr/bin/env python3
"""
Dataset Inspector

Utility script for inspecting processed Parquet files and their metadata
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from etl.config import load_config
from etl.loader import ParquetLoader


def list_datasets(loader: ParquetLoader) -> None:
    """List all processed datasets"""
    parquet_files = list(loader.processed_data_dir.glob("*.parquet"))
    parquet_dirs = [d for d in loader.processed_data_dir.iterdir() if d.is_dir()]

    print(f"\n{'='*60}")
    print("PROCESSED DATASETS")
    print(f"{'='*60}\n")

    if not parquet_files and not parquet_dirs:
        print("No processed datasets found.")
        return

    for parquet_file in sorted(parquet_files):
        dataset_name = parquet_file.stem
        size_mb = parquet_file.stat().st_size / 1024**2

        try:
            df = pd.read_parquet(parquet_file)
            print(f"Dataset: {dataset_name}")
            print(f"  File: {parquet_file.name}")
            print(f"  Size: {size_mb:.2f} MB")
            print(f"  Rows: {len(df):,}")
            print(f"  Columns: {len(df.columns)}")
            print()
        except Exception as e:
            print(f"Dataset: {dataset_name}")
            print(f"  Error: {e}")
            print()

    for parquet_dir in sorted(parquet_dirs):
        dataset_name = parquet_dir.name
        try:
            df = pd.read_parquet(parquet_dir)
            print(f"Dataset: {dataset_name} (partitioned)")
            print(f"  Directory: {parquet_dir.name}")
            print(f"  Rows: {len(df):,}")
            print(f"  Columns: {len(df.columns)}")
            print()
        except Exception as e:
            print(f"Dataset: {dataset_name}")
            print(f"  Error: {e}")
            print()


def show_dataset_info(loader: ParquetLoader, dataset_name: str) -> None:
    """Show detailed information about a dataset"""
    print(f"\n{'='*60}")
    print(f"DATASET: {dataset_name}")
    print(f"{'='*60}\n")

    try:
        # Load data
        df = loader.load_parquet(dataset_name)

        print("BASIC INFORMATION")
        print(f"Rows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")
        print(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        print()

        print("COLUMNS")
        print(df.dtypes.to_string())
        print()

        print("SAMPLE DATA (first 5 rows)")
        print(df.head().to_string())
        print()

        print("MISSING VALUES")
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(missing[missing > 0].to_string())
        else:
            print("No missing values")
        print()

        # Load metadata if available
        try:
            metadata = loader.load_metadata(dataset_name)
            print("METADATA")
            print(json.dumps(metadata, indent=2, default=str))
            print()
        except FileNotFoundError:
            print("No metadata file found")
            print()

    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)


def show_column_info(loader: ParquetLoader, dataset_name: str, column_name: str) -> None:
    """Show detailed information about a specific column"""
    print(f"\n{'='*60}")
    print(f"COLUMN: {dataset_name}.{column_name}")
    print(f"{'='*60}\n")

    try:
        df = loader.load_parquet(dataset_name)

        if column_name not in df.columns:
            print(f"Column '{column_name}' not found in dataset")
            print(f"Available columns: {', '.join(df.columns)}")
            sys.exit(1)

        col = df[column_name]

        print(f"Data Type: {col.dtype}")
        print(f"Non-Null Count: {col.count():,}")
        print(f"Null Count: {col.isnull().sum():,}")
        print(f"Unique Values: {col.nunique():,}")
        print()

        if pd.api.types.is_numeric_dtype(col):
            print("STATISTICS")
            print(col.describe().to_string())
            print()

        print("VALUE COUNTS (top 10)")
        print(col.value_counts().head(10).to_string())
        print()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Inspect processed Kaggle datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all processed datasets
  python inspect_datasets.py --list

  # Show information about a specific dataset
  python inspect_datasets.py --dataset credit_card_fraud

  # Show information about a specific column
  python inspect_datasets.py --dataset credit_card_fraud --column amount
        """,
    )

    parser.add_argument("--list", action="store_true", help="List all processed datasets")

    parser.add_argument("--dataset", help="Dataset name to inspect")

    parser.add_argument("--column", help="Column name to inspect (requires --dataset)")

    parser.add_argument(
        "--config", default="config/datasets.yaml", help="Path to configuration file"
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config)

        # Create loader
        loader = ParquetLoader(config.processed_data_dir, config.metadata_dir, config.compression)

        if args.list:
            list_datasets(loader)
        elif args.dataset and args.column:
            show_column_info(loader, args.dataset, args.column)
        elif args.dataset:
            show_dataset_info(loader, args.dataset)
        else:
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
