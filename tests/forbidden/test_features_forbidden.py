"""
Test that devices do NOT contain forbidden feature configurations.

Validates device snapshots don't contain forbidden features like 'feature bash'.
"""
import pytest
from tests.common.config_utils import (
    test_config, snapshot_directory, device_configs,
    load_golden_config_fragments, check_patterns_in_config, read_file,
    write_csv_report, log_compliance_result
)


def test_features_forbidden(device_configs, test_config):
    """Verify devices do NOT contain forbidden feature configurations."""
    # Load forbidden feature patterns
    forbidden_patterns = load_golden_config_fragments(test_config['forbidden_dir'], 'features')

    if not forbidden_patterns:
        pytest.skip(f"No forbidden feature patterns found in '{test_config['forbidden_dir']}/features/'")

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
                    device, 'features', template_name, 'FORBIDDEN', test_config['mode'],
                    f"Found: {matching_pattern}"
                ))
            else:
                # Forbidden pattern not found - PASS
                csv_results.append(log_compliance_result(
                    device, 'features', template_name, 'PASS', test_config['mode'],
                    'Not found (compliant)'
                ))

        # FAIL if any forbidden patterns are found
        if found_patterns:
            pattern_details = []
            for pattern_file, pattern_content in found_patterns:
                pattern_details.append(f"'{pattern_content}' (from {pattern_file})")

            # Write CSV before failing
            write_csv_report(test_config, csv_results)

            assert False, (
                f"{device}: Found forbidden features configuration in {config_path}:\n"
                f"  Forbidden patterns detected: {', '.join(pattern_details)}\n"
                f"  These patterns are forbidden per forbidden_dir/features/"
            )

    # Write CSV report
    write_csv_report(test_config, csv_results)