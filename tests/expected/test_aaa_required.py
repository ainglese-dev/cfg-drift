"""
Test that devices have required aaa configurations.

Validates device snapshots contain proper aaa blocks matching approved templates.
"""
import pytest
from tests.common.config_utils import (
    test_config, snapshot_directory, device_configs,
    load_golden_config_fragments, check_patterns_in_config, read_file,
    write_csv_report, log_compliance_result
)


def test_aaa_required(device_configs, test_config):
    """Verify devices have required aaa configurations."""
    # Load approved aaa templates
    aaa_templates = load_golden_config_fragments(test_config['expected_dir'], 'aaa')

    if not aaa_templates:
        pytest.skip(f"No aaa templates found in '{test_config['expected_dir']}/aaa/'")

    csv_results = []

    for device, config_path in device_configs:
        # Read device config file (e.g., snapshots/2025-09-25T12:00:00Z/spine01.cfg)
        lines = read_file(config_path)
        config_text = '\n'.join(lines)

        # Check if device has any aaa configuration matching templates
        found_match = False
        matched_template = None

        for template_name, template_content in aaa_templates.items():
            # Check if this template's pattern appears in device config
            if template_content.lower().strip() in config_text.lower():
                found_match = True
                matched_template = template_name

                if test_config['mode'] == 'strict':
                    # In strict mode, check exact content match
                    csv_results.append(log_compliance_result(
                        device, 'aaa', template_name, 'PASS', test_config['mode'],
                        'Exact match'
                    ))
                else:
                    # In loose mode, presence is enough
                    csv_results.append(log_compliance_result(
                        device, 'aaa', template_name, 'PASS', test_config['mode'],
                        'Configuration present (loose mode)'
                    ))
                break

        if not found_match:
            # No aaa configuration found
            csv_results.append(log_compliance_result(
                device, 'aaa', 'any template', 'MISSING', test_config['mode'],
                'No aaa configuration found'
            ))

            if test_config['mode'] == 'strict':
                # Write CSV before failing
                write_csv_report(test_config, csv_results)
                assert False, (
                    f"{device}: No aaa configuration found matching templates in "
                    f"expected_dir/aaa/ ({len(aaa_templates)} templates checked)"
                )

    # Write CSV report
    write_csv_report(test_config, csv_results)
