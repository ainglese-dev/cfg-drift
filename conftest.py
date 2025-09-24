"""
Pytest configuration and CLI options for cfg-drift banner testing.

Provides clean CLI flags for configuring banner compliance tests.
"""
import pytest

def pytest_addoption(parser):
    """Add custom CLI options for cfg-drift configuration."""

    group = parser.getgroup("cfg-drift", "Configuration drift testing options")

    group.addoption(
        "--drift-mode",
        action="store",
        default="strict",
        choices=["strict", "loose"],
        help="Banner validation mode: 'strict' (exact content match) or 'loose' (presence only). "
             "Default: strict"
    )

    group.addoption(
        "--snap-directory",
        action="store",
        default="snapshots",
        help="Base snapshots directory path. Default: 'snapshots'"
    )

    group.addoption(
        "--snap-timestamp",
        action="store",
        default=None,
        help="Specific snapshot timestamp directory name (e.g., '2025-09-24T12:00:00Z'). "
             "Default: most recent timestamp directory"
    )

    group.addoption(
        "--fragments-dir",
        action="store",
        default="fragments/banners",
        help="Directory containing approved banner fragments. "
             "Default: 'fragments/banners'"
    )

    group.addoption(
        "--expected-dir",
        action="store",
        default="supreme_golden_cfg/expected_Q1/fragments",
        help="Directory containing expected/required configuration templates. "
             "Default: 'supreme_golden_cfg/expected_Q1/fragments'"
    )

    group.addoption(
        "--forbidden-dir",
        action="store",
        default="supreme_golden_cfg/forbidden_Q1/fragments",
        help="Directory containing forbidden configuration patterns. "
             "Default: 'supreme_golden_cfg/forbidden_Q1/fragments'"
    )

    group.addoption(
        "--csv-output",
        action="store_true",
        default=False,
        help="Generate CSV compliance report in results directory. Default: disabled"
    )

    group.addoption(
        "--results-dir",
        action="store",
        default="results",
        help="Directory to save CSV compliance reports. Default: 'results'"
    )

    group.addoption(
        "--print-csv",
        action="store_true",
        default=False,
        help="Print CSV report to terminal (requires --csv-output). Default: disabled"
    )

def pytest_configure(config):
    """Validate CLI options after pytest configuration."""
    mode = config.getoption("--drift-mode")
    if mode and mode not in ["strict", "loose"]:
        raise pytest.UsageError(f"--drift-mode must be 'strict' or 'loose', got: '{mode}'")