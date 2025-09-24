#!/usr/bin/env python3
"""
Auto-generate individual test files for each configuration category.

Scans supreme_golden_cfg structure and creates dedicated test files.
"""
import os
import sys
from pathlib import Path

# Templates for test files
EXPECTED_TEST_TEMPLATE = '''"""
Test that devices have required {category} configurations.

Validates device snapshots contain proper {category} blocks matching approved templates.
"""
import pytest
from tests.common.config_utils import (
    test_config, snapshot_directory, device_configs,
    load_golden_config_fragments, check_patterns_in_config, read_file,
    write_csv_report, log_compliance_result
)


def test_{category}_required(device_configs, test_config):
    """Verify devices have required {category} configurations."""
    # Load approved {category} templates
    {category}_templates = load_golden_config_fragments(test_config['expected_dir'], '{category}')

    if not {category}_templates:
        pytest.skip(f"No {category} templates found in '{{test_config['expected_dir']}}/{category}/'")

    csv_results = []

    for device, config_path in device_configs:
        # Read device config file (e.g., snapshots/2025-09-25T12:00:00Z/spine01.cfg)
        lines = read_file(config_path)
        config_text = '\\n'.join(lines)

        # Check if device has any {category} configuration matching templates
        found_match = False
        matched_template = None

        for template_name, template_content in {category}_templates.items():
            # Check if this template's pattern appears in device config
            if template_content.lower().strip() in config_text.lower():
                found_match = True
                matched_template = template_name

                if test_config['mode'] == 'strict':
                    # In strict mode, check exact content match
                    csv_results.append(log_compliance_result(
                        device, '{category}', template_name, 'PASS', test_config['mode'],
                        'Exact match'
                    ))
                else:
                    # In loose mode, presence is enough
                    csv_results.append(log_compliance_result(
                        device, '{category}', template_name, 'PASS', test_config['mode'],
                        'Configuration present (loose mode)'
                    ))
                break

        if not found_match:
            # No {category} configuration found
            csv_results.append(log_compliance_result(
                device, '{category}', 'any template', 'MISSING', test_config['mode'],
                'No {category} configuration found'
            ))

            if test_config['mode'] == 'strict':
                # Write CSV before failing
                write_csv_report(test_config, csv_results)
                assert False, (
                    f"{{device}}: No {category} configuration found matching templates in "
                    f"expected_dir/{category}/ ({{len({category}_templates)}} templates checked)"
                )

    # Write CSV report
    write_csv_report(test_config, csv_results)
'''

FORBIDDEN_TEST_TEMPLATE = '''"""
Test that devices do NOT contain forbidden {category} configurations.

Validates device snapshots don't contain forbidden {category} like debug commands.
"""
import pytest
from tests.common.config_utils import (
    test_config, snapshot_directory, device_configs,
    load_golden_config_fragments, check_patterns_in_config, read_file,
    write_csv_report, log_compliance_result
)


def test_{category}_forbidden(device_configs, test_config):
    """Verify devices do NOT contain forbidden {category} configurations."""
    # Load forbidden {category} patterns
    forbidden_patterns = load_golden_config_fragments(test_config['forbidden_dir'], '{category}')

    if not forbidden_patterns:
        pytest.skip(f"No forbidden {category} patterns found in '{{test_config['forbidden_dir']}}/{category}/'")

    csv_results = []

    for device, config_path in device_configs:
        # Read device config file (e.g., snapshots/2025-09-25T12:00:00Z/spine01.cfg)
        lines = read_file(config_path)

        # Check if any forbidden patterns appear in the device config
        found_patterns = check_patterns_in_config(lines, forbidden_patterns)

        # Log results for each forbidden template
        for template_name in forbidden_patterns.keys():
            template_found = any(pattern_file == template_name for pattern_file, _ in found_patterns)

            if template_found:
                # Found forbidden pattern - FAIL
                matching_pattern = next(content for file, content in found_patterns if file == template_name)
                csv_results.append(log_compliance_result(
                    device, '{category}', template_name, 'FORBIDDEN', test_config['mode'],
                    f"Found: {{matching_pattern}}"
                ))
            else:
                # Forbidden pattern not found - PASS
                csv_results.append(log_compliance_result(
                    device, '{category}', template_name, 'PASS', test_config['mode'],
                    'Not found (compliant)'
                ))

        # FAIL if any forbidden patterns are found
        if found_patterns:
            pattern_details = []
            for pattern_file, pattern_content in found_patterns:
                pattern_details.append(f"'{{pattern_content}}' (from {{pattern_file}})")

            # Write CSV before failing
            write_csv_report(test_config, csv_results)

            assert False, (
                f"{{device}}: Found forbidden {category} configuration in {{config_path}}:\\n"
                f"  Forbidden patterns detected: {{', '.join(pattern_details)}}\\n"
                f"  These patterns are forbidden per forbidden_dir/{category}/"
            )

    # Write CSV report
    write_csv_report(test_config, csv_results)
'''

def discover_categories(base_path):
    """Discover all configuration categories in a golden config directory."""
    categories = []
    fragments_path = os.path.join(base_path, 'fragments')

    if not os.path.isdir(fragments_path):
        return categories

    for category_name in sorted(os.listdir(fragments_path)):
        category_path = os.path.join(fragments_path, category_name)
        if os.path.isdir(category_path):
            # Check if category has .cfg files
            cfg_files = [f for f in os.listdir(category_path) if f.endswith('.cfg')]
            if cfg_files:
                categories.append(category_name)

    return categories

def generate_test_file(category, template, output_path):
    """Generate a test file for a specific category."""
    content = template.format(category=category)

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"Generated: {output_path}")

def main():
    """Main generation function."""
    # Discover expected categories
    expected_categories = discover_categories('supreme_golden_cfg/expected_Q1')
    print(f"Found expected categories: {expected_categories}")

    # Discover forbidden categories
    forbidden_categories = discover_categories('supreme_golden_cfg/forbidden_Q1')
    print(f"Found forbidden categories: {forbidden_categories}")

    # Generate expected test files
    for category in expected_categories:
        if category == 'banners':
            print(f"Skipping {category} - already exists with custom logic")
            continue

        output_file = f"tests/expected/test_{category}_required.py"
        generate_test_file(category, EXPECTED_TEST_TEMPLATE, output_file)

    # Generate forbidden test files
    for category in forbidden_categories:
        if category == 'features':
            print(f"Skipping {category} - already exists")
            continue

        output_file = f"tests/forbidden/test_{category}_forbidden.py"
        generate_test_file(category, FORBIDDEN_TEST_TEMPLATE, output_file)

    print("\\nTest file generation complete!")
    print("Run: pytest --csv-output --print-csv --drift-mode=strict --tb=no -q")

if __name__ == "__main__":
    main()