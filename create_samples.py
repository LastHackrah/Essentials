#!/usr/bin/env python3
"""
Create representative samples of large datasets for Streamlit Cloud deployment.

Target: Keep total data size under 100MB for fast deployment and reasonable UX.
Strategy: Stratified sampling to preserve statistical distributions.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/processed")

# Sample configurations: (filename, target_rows, sampling_strategy)
SAMPLE_CONFIGS = [
    # Large files that need significant reduction
    ("us_accidents.parquet", 50000, "stratified"),  # 974MB → ~15MB
    ("amazon_food_reviews.parquet", 30000, "random"),  # 162MB → ~5MB
    ("credit_card_fraud.parquet", 50000, "stratified"),  # 48MB → ~5MB
    ("us_pollution.parquet", 100000, "stratified"),  # 24MB → ~5MB
    ("power_consumption.parquet", 100000, "time_series"),  # 24MB → ~5MB

    # Medium files - modest reduction
    ("spotify_tracks.parquet", 50000, "random"),  # 8.7MB → ~4MB

    # Small files - keep as is (< 3MB)
    # tmdb_movies, network_intrusion, ibm_hr_attrition, food_price - no change needed
]


def create_stratified_sample(df: pd.DataFrame, n_samples: int, strat_column: str = None) -> pd.DataFrame:
    """Create stratified sample preserving class distributions."""
    if strat_column and strat_column in df.columns:
        # Stratified by specified column
        return df.groupby(strat_column, group_keys=False).apply(
            lambda x: x.sample(min(len(x), max(1, int(n_samples * len(x) / len(df)))))
        ).sample(n=min(n_samples, len(df)))
    else:
        # Random sample
        return df.sample(n=min(n_samples, len(df)))


def create_time_series_sample(df: pd.DataFrame, n_samples: int, time_column: str = None) -> pd.DataFrame:
    """Create time series sample preserving temporal patterns."""
    if time_column and time_column in df.columns:
        df = df.sort_values(time_column)
        # Take every Nth row to maintain temporal coverage
        step = max(1, len(df) // n_samples)
        return df.iloc[::step].head(n_samples)
    else:
        # Fallback to random
        return df.sample(n=min(n_samples, len(df)))


def sample_dataset(filename: str, target_rows: int, strategy: str):
    """Sample a single dataset."""
    file_path = DATA_DIR / filename

    if not file_path.exists():
        print(f"⏭️  Skipping {filename} (file not found)")
        return

    print(f"\n📊 Processing: {filename}")

    # Read original
    df = pd.read_parquet(file_path)
    original_rows = len(df)
    original_size = file_path.stat().st_size / (1024 * 1024)  # MB

    print(f"   Original: {original_rows:,} rows, {original_size:.1f} MB")

    if original_rows <= target_rows:
        print(f"   ✅ Already small enough, keeping as is")
        return

    # Apply sampling strategy
    if strategy == "stratified":
        # Try to find a good stratification column
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        strat_col = categorical_cols[0] if len(categorical_cols) > 0 else None
        sampled_df = create_stratified_sample(df, target_rows, strat_col)
    elif strategy == "time_series":
        # Try to find a time column
        time_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
        time_col = time_cols[0] if time_cols else None
        sampled_df = create_time_series_sample(df, target_rows, time_col)
    else:  # random
        sampled_df = df.sample(n=target_rows)

    # Save sample
    sampled_df.to_parquet(file_path, compression='snappy', index=False)

    new_size = file_path.stat().st_size / (1024 * 1024)
    reduction = (1 - new_size / original_size) * 100

    print(f"   ✅ Sampled: {len(sampled_df):,} rows, {new_size:.1f} MB ({reduction:.0f}% reduction)")


def main():
    print("🎲 Creating representative samples for Streamlit Cloud deployment")
    print("=" * 70)

    for filename, target_rows, strategy in SAMPLE_CONFIGS:
        sample_dataset(filename, target_rows, strategy)

    print("\n" + "=" * 70)
    print("📦 Summary of data directory:")

    total_size = 0
    for file in sorted(DATA_DIR.glob("*.parquet")):
        size_mb = file.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"   {file.name:45s} {size_mb:8.2f} MB")

    print(f"\n   {'Total:':<45s} {total_size:8.2f} MB")

    if total_size > 100:
        print(f"\n   ⚠️  Warning: Total size {total_size:.1f} MB exceeds 100MB target")
    else:
        print(f"\n   ✅ Total size is within target (< 100MB)")


if __name__ == "__main__":
    main()
