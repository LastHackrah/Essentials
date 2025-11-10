#!/usr/bin/env python3
"""
Audit all example YAML files for DSL feature coverage
"""

import yaml
from pathlib import Path
from collections import defaultdict

def audit_dashboard(spec_path: Path) -> dict:
    """Audit a single dashboard for features used"""
    with open(spec_path) as f:
        spec = yaml.safe_load(f)

    features = {
        'version': spec.get('dsl_version'),
        'has_metadata': 'metadata' in spec.get('dashboard', {}),
        'has_narrative': spec.get('dashboard', {}).get('metadata', {}).get('narrative') is not None,
        'has_formatting': 'formatting' in spec.get('dashboard', {}).get('data_source', {}),
        'has_column_labels': 'column_labels' in spec.get('dashboard', {}).get('data_source', {}),
        'has_dq_rules': 'data_quality' in spec.get('dashboard', {}).get('data_source', {}),
        'has_validation_policy': 'validation_policy' in spec,
        'num_pages': len(spec.get('dashboard', {}).get('pages', [])),
        'chart_types': set(),
        'has_filters': False,
        'has_metrics': False,
        'layout_types': set(),
    }

    # Analyze pages
    for page in spec.get('dashboard', {}).get('pages', []):
        if page.get('filters'):
            features['has_filters'] = True
        if page.get('metrics'):
            features['has_metrics'] = True

        # Check layout
        layout = page.get('layout', {})
        features['layout_types'].add(layout.get('type', 'single'))

        # Check chart types
        for comp in layout.get('components', []):
            if comp.get('type') == 'visualization':
                viz = comp.get('visualization', {})
                chart_type = viz.get('chart_type')
                if chart_type:
                    features['chart_types'].add(chart_type)

    return features

def main():
    """Audit all dashboards"""
    spec_dir = Path('dsl/examples')
    dashboards = list(spec_dir.glob('*.yaml'))

    # Exclude test files
    exclude = {'failing.yaml', 'happy_path.yaml', 'minimal.yaml', 'enhanced_fraud_analysis.yaml'}
    dashboards = [d for d in dashboards if d.name not in exclude]

    print("=" * 80)
    print("DSL FEATURE COVERAGE AUDIT")
    print("=" * 80)

    # Aggregate statistics
    all_chart_types = set()
    all_layout_types = set()
    feature_counts = defaultdict(int)

    for dash_path in sorted(dashboards):
        features = audit_dashboard(dash_path)

        print(f"\n📊 {dash_path.name}")
        print(f"  Version: {features['version']}")
        print(f"  Pages: {features['num_pages']}")
        print(f"  Chart Types: {', '.join(sorted(features['chart_types'])) if features['chart_types'] else 'None'}")
        print(f"  Layouts: {', '.join(sorted(features['layout_types']))}")

        # Feature flags
        flags = []
        if features['has_metadata']: flags.append('✓ metadata')
        if features['has_narrative']: flags.append('✓ narrative')
        if features['has_formatting']: flags.append('✓ formatting')
        if features['has_column_labels']: flags.append('✓ labels')
        if features['has_dq_rules']: flags.append('✓ DQ')
        if features['has_validation_policy']: flags.append('✓ policy')
        if features['has_filters']: flags.append('✓ filters')
        if features['has_metrics']: flags.append('✓ metrics')

        print(f"  Features: {', '.join(flags) if flags else 'Basic'}")

        # Aggregate
        all_chart_types.update(features['chart_types'])
        all_layout_types.update(features['layout_types'])
        for key in ['has_metadata', 'has_narrative', 'has_formatting', 'has_column_labels',
                    'has_dq_rules', 'has_validation_policy', 'has_filters', 'has_metrics']:
            if features[key]:
                feature_counts[key] += 1

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Dashboards: {len(dashboards)}")
    print(f"\nChart Types Used: {', '.join(sorted(all_chart_types))}")
    print(f"Layout Types Used: {', '.join(sorted(all_layout_types))}")
    print(f"\nFeature Adoption:")
    for feature, count in sorted(feature_counts.items()):
        pct = (count / len(dashboards)) * 100
        print(f"  {feature}: {count}/{len(dashboards)} ({pct:.0f}%)")

    # Available chart types (from schema)
    available_charts = {
        'histogram', 'ecdf', 'boxplot', 'violin', 'kde', 'scatter', 'hexbin', 'kde2d',
        'line', 'bar', 'heatmap', 'pie', 'table'
    }
    unused_charts = available_charts - all_chart_types
    if unused_charts:
        print(f"\n⚠️  Unused Chart Types: {', '.join(sorted(unused_charts))}")

    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
