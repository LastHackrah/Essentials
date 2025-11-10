#!/usr/bin/env python3
"""
Utility script to add severity field to all Violation() calls in adapter.py

This script analyzes violation codes and assigns appropriate severity levels.
"""

import re
from pathlib import Path

# Severity mapping by code pattern
SEVERITY_MAP = {
    "UNSUPPORTED_VERSION": "ERROR",
    "SCHEMA_NOT_FOUND": "ERROR",
    "SCHEMA_VIOLATION": "ERROR",
    "INVALID_SCHEMA": "ERROR",
    "DUPLICATE_ID": "ERROR",
    "INVALID_REFERENCE": "CRITICAL",
    "MISSING_REQUIRED_ROLE": "ERROR",
    "DQ_FIELD_NOT_IN_SCHEMA": "ERROR",
    "DQ_INAPPROPRIATE_METHOD": "WARNING",
    "DQ_QUESTIONABLE_METHOD": "WARNING",
}

def add_severity_to_violations(file_path: Path):
    """Add severity field to all Violation() calls"""

    with open(file_path) as f:
        content = f.read()

    # Pattern to match Violation() calls
    pattern = r'Violation\(\s*code="([A-Z_]+)",'

    def replacement(match):
        code = match.group(1)
        severity = SEVERITY_MAP.get(code, "ERROR")  # Default to ERROR
        return f'Violation(\n                code="{code}",\n                severity=ViolationSeverity.{severity},'

    # Replace all occurrences
    updated_content = re.sub(pattern, replacement, content)

    # Write back
    with open(file_path, 'w') as f:
        f.write(updated_content)

    print(f"✓ Updated {file_path}")
    print(f"  Applied severity levels to violations")

if __name__ == "__main__":
    adapter_path = Path("dsl/adapter.py")
    add_severity_to_violations(adapter_path)
