"""
Upgrade all v1.1 dashboards to v1.2 with formatting, DQ rules, and enhancements
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List


class DashboardUpgrader:
    """Upgrade dashboards from v1.1 to v1.2"""

    # Currency mappings by dataset context
    CURRENCY_MAP = {
        'fraud': 'USD',
        'amazon': 'USD',
        'tmdb': 'USD',
        'ibm': 'USD',
        'default': 'USD'
    }

    def __init__(self, input_file: Path):
        self.input_file = input_file
        self.output_file = input_file.parent / input_file.name.replace('_v1.1.yaml', '_v1.2.yaml')

    def upgrade(self):
        """Perform the upgrade"""
        with open(self.input_file) as f:
            spec = yaml.safe_load(f)

        # Update version
        spec['dsl_version'] = '1.2.0'

        # Enhance metadata
        self._enhance_metadata(spec)

        # Add formatting rules
        self._add_formatting(spec)

        # Add column labels
        self._add_column_labels(spec)

        # Add data quality rules
        self._add_data_quality(spec)

        # Save upgraded spec
        with open(self.output_file, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False, indent=2)

        print(f"✅ Upgraded: {self.input_file.name} → {self.output_file.name}")

    def _enhance_metadata(self, spec: Dict):
        """Add narrative and currency to metadata"""
        metadata = spec.get('dashboard', {}).get('metadata', {})

        # Add currency if not present
        if 'currency' not in metadata:
            dataset_name = metadata.get('dataset_name', '').lower()
            for key, currency in self.CURRENCY_MAP.items():
                if key in dataset_name or key in str(self.input_file):
                    metadata['currency'] = currency
                    break
            else:
                metadata['currency'] = 'USD'

        # Generate narrative if not present
        if 'narrative' not in metadata:
            narrative = self._generate_narrative(metadata)
            metadata['narrative'] = narrative

        spec['dashboard']['metadata'] = metadata

    def _generate_narrative(self, metadata: Dict) -> str:
        """Generate a basic narrative from metadata"""
        name = metadata.get('dataset_name', 'Dataset')
        rows = metadata.get('rows', 0)
        description = metadata.get('description', '')
        source = metadata.get('source', '')

        narrative = f"""
The {name} contains {rows:,} records {f'from {source}' if source else ''}.
{description}

This dataset enables comprehensive analysis of key patterns and trends.
The dashboard provides interactive visualizations and metrics for data exploration,
allowing users to filter, aggregate, and discover insights across multiple dimensions.
        """.strip()

        return narrative

    def _add_formatting(self, spec: Dict):
        """Add formatting rules based on schema"""
        data_source = spec.get('dashboard', {}).get('data_source', {})
        schema = data_source.get('schema', {})

        if 'formatting' not in data_source:
            formatting = {}

            for field, dtype in schema.items():
                field_lower = field.lower()

                # Currency fields
                if any(term in field_lower for term in ['price', 'amount', 'revenue', 'cost', 'salary', 'fee']):
                    formatting[field] = {
                        'type': 'currency',
                        'precision': 2,
                        'use_thousands_separator': True
                    }

                # Percentage fields
                elif any(term in field_lower for term in ['rate', 'percent', 'ratio', 'pct']):
                    formatting[field] = {
                        'type': 'percent',
                        'precision': 1
                    }

                # Integer fields
                elif dtype == 'integer':
                    formatting[field] = {
                        'type': 'integer',
                        'use_thousands_separator': True
                    }

                # Float fields (general numbers)
                elif dtype == 'float' and 'id' not in field_lower:
                    formatting[field] = {
                        'type': 'number',
                        'precision': 2,
                        'use_thousands_separator': True
                    }

            if formatting:
                data_source['formatting'] = formatting

    def _add_column_labels(self, spec: Dict):
        """Generate human-readable column labels"""
        data_source = spec.get('dashboard', {}).get('data_source', {})
        schema = data_source.get('schema', {})

        if 'column_labels' not in data_source:
            column_labels = {}

            for field in schema.keys():
                # Convert snake_case to Title Case
                label = field.replace('_', ' ').title()
                # Handle common abbreviations
                label = label.replace('Id', 'ID')
                label = label.replace('Aqi', 'AQI')
                label = label.replace('Iso', 'ISO')
                label = label.replace('Url', 'URL')
                label = label.replace('Pct', '%')

                column_labels[field] = label

            data_source['column_labels'] = column_labels

    def _add_data_quality(self, spec: Dict):
        """Add basic data quality rules"""
        data_source = spec.get('dashboard', {}).get('data_source', {})
        schema = data_source.get('schema', {})

        if 'data_quality' not in data_source:
            dq_rules = {
                'missing_values': {
                    'strategy': 'auto',
                    'rules': []
                },
                'duplicates': {
                    'enabled': False  # Enable per dataset as needed
                },
                'outliers': {
                    'enabled': True,
                    'rules': []
                },
                'validation': {
                    'rules': []
                },
                'reporting': {
                    'log_level': 'info',
                    'show_summary': True,
                    'show_details': False
                }
            }

            # Add outlier detection for numeric fields
            for field, dtype in schema.items():
                if dtype in ['float', 'integer'] and 'id' not in field.lower():
                    dq_rules['outliers']['rules'].append({
                        'fields': [field],
                        'method': 'percentile',
                        'lower': 0.1,
                        'upper': 99.9,
                        'action': 'cap'
                    })

            # Add validation for datetime fields
            for field, dtype in schema.items():
                if dtype == 'datetime':
                    dq_rules['validation']['rules'].append({
                        'field': field,
                        'constraint': 'not_null',
                        'action': 'drop'
                    })

            data_source['data_quality'] = dq_rules


def main():
    """Upgrade all v1.1 dashboards"""
    examples_dir = Path('dsl/examples')
    v11_files = list(examples_dir.glob('*_v1.1.yaml'))

    print(f"Found {len(v11_files)} v1.1 dashboards to upgrade\n")

    for yaml_file in v11_files:
        try:
            upgrader = DashboardUpgrader(yaml_file)
            upgrader.upgrade()
        except Exception as e:
            print(f"❌ Failed to upgrade {yaml_file.name}: {e}")

    print(f"\n✅ Upgrade complete! {len(v11_files)} dashboards upgraded to v1.2")


if __name__ == '__main__':
    main()
