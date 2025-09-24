#!/usr/bin/env python3
"""
Simple configuration drift comparison between snapshots.

Uses standard diff command to show what changed between two snapshots.
"""
import os
import sys
import subprocess
import argparse


def find_snapshot_directories(snapshots_base):
    """Find all valid snapshot directories."""
    if not os.path.isdir(snapshots_base):
        return []

    timestamp_dirs = []
    for d in os.listdir(snapshots_base):
        dir_path = os.path.join(snapshots_base, d)
        if os.path.isdir(dir_path) and d not in ['examples', 'README.md']:
            if 'T' in d and ('Z' in d or ':' in d):
                timestamp_dirs.append(d)

    return sorted(timestamp_dirs)


def get_device_configs(snapshot_dir):
    """Get all .cfg files from a snapshot directory."""
    if not os.path.isdir(snapshot_dir):
        return {}

    configs = {}
    for file in os.listdir(snapshot_dir):
        if file.endswith('.cfg'):
            device_name = file[:-4]  # Remove .cfg extension
            configs[device_name] = os.path.join(snapshot_dir, file)

    return configs


def main():
    """Main drift comparison function."""
    parser = argparse.ArgumentParser(description='Compare configuration drift between snapshots')
    parser.add_argument('--snapshots-dir', default='snapshots',
                       help='Base snapshots directory (default: snapshots)')
    parser.add_argument('--snapshot-a', required=True,
                       help='First (older) snapshot timestamp')
    parser.add_argument('--snapshot-b',
                       help='Second (newer) snapshot timestamp (default: latest)')
    parser.add_argument('--device-filter',
                       help='Only compare specific device (optional)')
    parser.add_argument('--color', action='store_true',
                       help='Use colordiff for colored output (falls back to diff if not installed)')

    args = parser.parse_args()

    # Find available snapshots
    available_snapshots = find_snapshot_directories(args.snapshots_dir)
    if not available_snapshots:
        print(f"No snapshots found in {args.snapshots_dir}")
        sys.exit(1)

    # Validate snapshot-a
    if args.snapshot_a not in available_snapshots:
        print(f"Snapshot '{args.snapshot_a}' not found.")
        print(f"Available: {', '.join(available_snapshots)}")
        sys.exit(1)

    # Default snapshot-b to latest if not specified
    if not args.snapshot_b:
        args.snapshot_b = available_snapshots[-1]

    if args.snapshot_b not in available_snapshots:
        print(f"Snapshot '{args.snapshot_b}' not found.")
        print(f"Available: {', '.join(available_snapshots)}")
        sys.exit(1)

    # Get device configurations from both snapshots
    snapshot_a_dir = os.path.join(args.snapshots_dir, args.snapshot_a)
    snapshot_b_dir = os.path.join(args.snapshots_dir, args.snapshot_b)

    old_devices = get_device_configs(snapshot_a_dir)
    new_devices = get_device_configs(snapshot_b_dir)

    print(f"# Comparing {args.snapshot_a} -> {args.snapshot_b}")

    # New devices
    new_device_names = set(new_devices.keys()) - set(old_devices.keys())
    if new_device_names:
        print(f"# NEW: {', '.join(sorted(new_device_names))}")

    # Removed devices
    removed_device_names = set(old_devices.keys()) - set(new_devices.keys())
    if removed_device_names:
        print(f"# REMOVED: {', '.join(sorted(removed_device_names))}")

    # Compare common devices
    common_devices = set(old_devices.keys()) & set(new_devices.keys())
    for device in sorted(common_devices):
        if args.device_filter and device != args.device_filter:
            continue

        old_config = old_devices[device]
        new_config = new_devices[device]

        # Choose diff command based on color option
        if args.color:
            # Try colordiff first, fall back to diff
            diff_cmd = 'colordiff'
            try:
                subprocess.run([diff_cmd, '--version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                diff_cmd = 'diff'
        else:
            diff_cmd = 'diff'

        # Just run diff and show output
        try:
            result = subprocess.run([diff_cmd, '-u', old_config, new_config],
                                  capture_output=True, text=True)
            if result.returncode == 1:  # Files differ
                print(f"\n## {device}")
                print(result.stdout)
            elif result.returncode > 1:  # Error
                print(f"Error comparing {device}: {result.stderr}")
        except Exception as e:
            print(f"Error running diff for {device}: {e}")


if __name__ == "__main__":
    main()