"""
Test that devices have required banner configurations.

Validates device snapshots contain proper banner blocks matching approved templates.
"""
import pytest
from tests.common.config_utils import (
    test_config, snapshot_directory, device_configs,
    load_golden_config_fragments, extract_banner, normalize_text, read_file,
    write_csv_report, log_compliance_result
)


def test_banners_required(device_configs, test_config):
    """Verify devices have required banner configurations."""
    # Load approved banner templates
    banner_templates = load_golden_config_fragments(test_config['expected_dir'], 'banners')

    if not banner_templates:
        pytest.skip(f"No banner templates found in '{test_config['expected_dir']}/banners/'")

    csv_results = []

    for device, config_path in device_configs:
        # Read device config file (e.g., snapshots/2025-09-25T12:00:00Z/spine01.cfg)
        lines = read_file(config_path)

        # Extract banner block: "banner motd ^C" + content + "^C"
        banner = extract_banner(lines)

        if not banner or len(banner) < 3:
            # Log missing banner
            csv_results.append(log_compliance_result(
                device, 'banners', 'N/A', 'MISSING', test_config['mode'],
                'No complete banner found'
            ))
            assert False, (
                f"{device}: No complete banner found in {config_path}. "
                f"Expected: header + content + terminator"
            )

        # In strict mode, check banner content matches templates
        if test_config['mode'] == 'strict':
            # Normalize device banner (remove timestamps, whitespace)
            device_banner = normalize_text(banner)

            # Check if normalized device banner matches ANY approved template
            matching_template = None
            for template_name, template_content in banner_templates.items():
                if device_banner == template_content:
                    matching_template = template_name
                    break

            if matching_template:
                csv_results.append(log_compliance_result(
                    device, 'banners', matching_template, 'PASS', test_config['mode'],
                    'Exact match'
                ))
            else:
                csv_results.append(log_compliance_result(
                    device, 'banners', 'any template', 'FAIL', test_config['mode'],
                    'Banner content mismatch'
                ))
                assert False, (
                    f"{device}: Banner doesn't match any expected template in 'banners/' "
                    f"({len(banner_templates)} templates checked)"
                )
        else:
            # Loose mode - banner exists, that's enough
            csv_results.append(log_compliance_result(
                device, 'banners', 'any template', 'PASS', test_config['mode'],
                'Banner present (loose mode)'
            ))

    # Write CSV report
    write_csv_report(test_config, csv_results)