#!/usr/bin/env python3
"""
DSL System End-to-End Test

Tests the complete DSL workflow:
1. Parse YAML specifications
2. Validate against schema
3. Build intermediate representation
4. Execute with sample inputs
"""

import sys
from pathlib import Path

from dsl.core.adapter import build_ir, execute, parse, validate


def test_minimal_spec():
    """Test minimal valid specification"""
    print("=" * 60)
    print("Testing: Minimal Spec")
    print("=" * 60)

    spec_path = Path("dsl/examples/minimal.yaml")
    with open(spec_path) as f:
        yaml_content = f.read()

    # Parse
    print("✓ Parsing YAML...")
    spec = parse(yaml_content)
    print(f"  Dashboard ID: {spec['dashboard']['id']}")

    # Validate
    print("✓ Validating...")
    violations = validate(spec)
    if violations:
        print("  ✗ Validation failed:")
        for v in violations:
            print(f"    [{v['code']}] {v['message']}")
        return False
    print("  ✓ Valid!")

    # Build IR
    print("✓ Building intermediate representation...")
    ir = build_ir(spec)
    print(f"  Pages: {len(ir['pages'])}")

    # Execute
    print("✓ Executing...")
    inputs = {"filters": {}}
    try:
        results = execute(ir, inputs)
        print(f"  Results: {results['dashboard_id']}")
        print(f"  Pages processed: {len(results['pages'])}")
        return True
    except Exception as e:
        print(f"  ✗ Execution failed: {e}")
        return False


def test_happy_path_spec():
    """Test complete fraud detection dashboard"""
    print("\n" + "=" * 60)
    print("Testing: Happy Path (Fraud Detection)")
    print("=" * 60)

    spec_path = Path("dsl/examples/happy_path.yaml")
    with open(spec_path) as f:
        yaml_content = f.read()

    # Parse
    print("✓ Parsing YAML...")
    spec = parse(yaml_content)
    print(f"  Dashboard: {spec['dashboard']['title']}")

    # Validate
    print("✓ Validating...")
    violations = validate(spec)
    if violations:
        print("  ✗ Validation failed:")
        for v in violations:
            print(f"    [{v['code']}] {v['message']}")
        return False
    print("  ✓ Valid!")

    # Build IR
    print("✓ Building intermediate representation...")
    ir = build_ir(spec)
    print(f"  Pages: {len(ir['pages'])}")
    for page in ir["pages"]:
        print(f"    - {page['id']}: {len(page['metrics'])} metrics, {len(page['filters'])} filters")

    # Execute
    print("✓ Executing...")
    inputs = {"filters": {"amount_filter": [0, 500], "fraud_filter": 1}}
    try:
        results = execute(ir, inputs)
        print(f"  Results: {results['dashboard_id']}")
        print(f"  Pages processed: {len(results['pages'])}")

        # Show metrics from first page
        if results["pages"]:
            page_result = results["pages"][0]
            print(f"\n  Page '{page_result['id']}' metrics:")
            for metric_id, value in page_result["metrics"].items():
                print(f"    - {metric_id}: {value}")

        return True
    except Exception as e:
        print(f"  ✗ Execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_failing_spec():
    """Test specification with intentional errors"""
    print("\n" + "=" * 60)
    print("Testing: Failing Spec (Error Detection)")
    print("=" * 60)

    spec_path = Path("dsl/examples/failing.yaml")
    with open(spec_path) as f:
        yaml_content = f.read()

    # Parse
    print("✓ Parsing YAML...")
    spec = parse(yaml_content)

    # Validate
    print("✓ Validating (expecting errors)...")
    violations = validate(spec)
    if violations:
        print(f"  ✓ Found {len(violations)} violations (as expected):")
        for v in violations:
            print(f"    [{v['code']}] {v['message']}")
            print(f"      Path: {v['path']}")
            print(f"      Repair: {v['repair']}")
        return True
    else:
        print("  ✗ Expected validation errors but got none!")
        return False


def main():
    """Run all tests"""
    print("DSL System End-to-End Testing")
    print("=" * 60)

    results = []

    # Test 1: Minimal spec
    results.append(("Minimal Spec", test_minimal_spec()))

    # Test 2: Happy path
    results.append(("Happy Path", test_happy_path_spec()))

    # Test 3: Failing spec
    results.append(("Error Detection", test_failing_spec()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")

    # Exit code
    all_passed = all(result for _, result in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
