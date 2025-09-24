"""
Shared utilities for configuration drift testing.

Common functions used across all test modules for device configuration validation.
"""
import os
import re
import glob
import csv
import pytest
from datetime import datetime


def get_config(request):
    """Get configuration from CLI flags."""
    return {
        'snapshots_base': request.config.getoption("--snap-directory"),
        'snap_ts': request.config.getoption("--snap-timestamp"),
        'fragments_dir': request.config.getoption("--fragments-dir"),
        'expected_dir': request.config.getoption("--expected-dir"),
        'forbidden_dir': request.config.getoption("--forbidden-dir"),
        'mode': request.config.getoption("--drift-mode").lower(),
        'csv_output': request.config.getoption("--csv-output"),
        'results_dir': request.config.getoption("--results-dir"),
        'print_csv': request.config.getoption("--print-csv")
    }


def read_file(path):
    """Read file content, ignoring encoding errors."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read().splitlines()


def normalize_text(lines):
    """Clean lines for comparison: remove timestamps, normalize whitespace."""
    cleaned = []
    for line in lines:
        # Skip auto-generated timestamp comments
        if re.match(r'^\s*!.*(Generated|build|\d{4}-\d{2}-\d{2}|UTC|local)', line, re.IGNORECASE):
            continue
        cleaned.append(' '.join(line.strip().split()))

    # Remove empty lines from start/end
    while cleaned and not cleaned[0]:
        cleaned.pop(0)
    while cleaned and not cleaned[-1]:
        cleaned.pop()

    return '\n'.join(cleaned).strip()


def extract_banner(lines):
    """Extract full banner block: header + content + terminator."""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith('banner '):
            continue

        parts = stripped.split(None, 3)
        if len(parts) < 3:
            continue

        delimiter = parts[2]
        banner_lines = [line]

        # Handle inline banners: "banner motd ^Ccontent^C"
        if len(parts) >= 4:
            content = parts[3]
            if content.endswith(delimiter):
                return [line, content[:-len(delimiter)], delimiter]
            banner_lines.append(content)

        # Collect lines until delimiter
        for j in range(i + 1, len(lines)):
            if lines[j].strip() == delimiter:
                banner_lines.append(lines[j].strip())
                return banner_lines
            banner_lines.append(lines[j])

        return banner_lines  # EOF reached

    return None


def find_latest_snapshot_dir(snapshots_base, snap_ts=None):
    """Find the most recent snapshot directory."""
    if snap_ts:
        candidate = os.path.join(snapshots_base, snap_ts)
        return candidate if os.path.isdir(candidate) else None

    if not os.path.isdir(snapshots_base):
        return None

    subdirs = [d for d in sorted(os.listdir(snapshots_base))
               if os.path.isdir(os.path.join(snapshots_base, d))]

    return os.path.join(snapshots_base, subdirs[-1]) if subdirs else None


def collect_device_configs(snapshot_dir):
    """Get all .cfg files from snapshot directory."""
    cfg_files = glob.glob(os.path.join(snapshot_dir, '*.cfg'))
    return [(os.path.splitext(os.path.basename(f))[0], f) for f in sorted(cfg_files)]


def load_golden_config_fragments(base_dir, category_name):
    """Load all .cfg fragments for a specific category."""
    category_path = os.path.join(base_dir, category_name)
    fragments = {}

    if not os.path.isdir(category_path):
        return fragments

    for filename in sorted(os.listdir(category_path)):
        file_path = os.path.join(category_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.cfg'):
            fragments[filename] = normalize_text(read_file(file_path))

    return fragments


def check_patterns_in_config(config_lines, patterns):
    """Check if any patterns appear in configuration lines."""
    config_text = '\n'.join(config_lines).lower()
    found_patterns = []

    for pattern_name, pattern_content in patterns.items():
        # Check if the pattern content appears in the config
        if pattern_content.lower().strip() in config_text:
            found_patterns.append((pattern_name, pattern_content.strip()))

    return found_patterns


# Common fixtures
@pytest.fixture(scope="session")
def test_config(request):
    """Get test configuration from CLI flags."""
    return get_config(request)


@pytest.fixture(scope="session")
def snapshot_directory(test_config):
    """Find and validate snapshot directory."""
    snapshot_dir = find_latest_snapshot_dir(test_config['snapshots_base'], test_config['snap_ts'])
    if not snapshot_dir:
        pytest.skip(f"No snapshot directory found in '{test_config['snapshots_base']}'")
    return snapshot_dir


@pytest.fixture(scope="session")
def device_configs(snapshot_directory):
    """Collect device configuration files."""
    configs = collect_device_configs(snapshot_directory)
    if not configs:
        pytest.skip(f"No .cfg files in '{snapshot_directory}'")
    return configs


# CSV Reporting Functions
def write_csv_report(test_config, results):
    """Write compliance results to CSV file."""
    if not test_config['csv_output']:
        return

    # Create results directory
    results_dir = test_config['results_dir']
    os.makedirs(results_dir, exist_ok=True)

    # Generate timestamp filename (shared across session)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")  # Minute precision for session sharing
    csv_file = os.path.join(results_dir, f"compliance_{timestamp}.csv")

    # Check if file exists to determine if we need header
    file_exists = os.path.isfile(csv_file)

    # Append to CSV file
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Device', 'Category', 'Template_Used', 'Status', 'Mode', 'Details'])
        for result in results:
            writer.writerow(result)

    # Print CSV to terminal if requested (only for this batch)
    if test_config['print_csv']:
        for result in results:
            print(','.join(str(x) for x in result))

    return csv_file


def log_compliance_result(device, category, template, status, mode, details=""):
    """Log a single compliance result for CSV reporting."""
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Map specific failure types to FAILED status, preserve original in details
    if status in ['MISSING', 'FORBIDDEN']:
        original_status = status
        status = 'FAILED'
        # Prepend original status to details if not already there
        if not details.startswith(original_status):
            details = f"{original_status}: {details}" if details else original_status

    return [timestamp, device, category, template, status, mode, details]