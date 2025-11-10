# Utility Scripts

One-time and development utility scripts for the DashSpec project.

## Scripts

### `inspect_datasets.py`
Inspect processed Parquet datasets and view metadata.

```bash
python scripts/inspect_datasets.py --list
python scripts/inspect_datasets.py --inspect fraud_detection
python scripts/inspect_datasets.py --schema us_pollution
```

### `test_dsl.py`
End-to-end DSL system testing with minimal, happy path, and error detection tests.

```bash
python scripts/test_dsl.py
```

Tests the complete workflow:
- Parse YAML specifications
- Validate against schema
- Build intermediate representation
- Execute with sample inputs

### `upgrade_dashboards_to_v12.py`
**One-time utility** - Upgrade v1.1 dashboards to v1.2 format with formatting rules, DQ specs, and enhanced metadata.

```bash
python scripts/upgrade_dashboards_to_v12.py
```

**Note**: This script was used for the v1.1 → v1.2 migration and is kept for reference. All production dashboards are now on v1.2.

## Usage Notes

- Run scripts from the project root directory
- Scripts assume the standard project structure
- For automated testing, use `pytest tests/` instead of `test_dsl.py`
