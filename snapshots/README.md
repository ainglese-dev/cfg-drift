# Snapshots Directory

This directory contains network device configuration snapshots for testing.

## Structure

```
snapshots/
├── README.md                    # This file
├── examples/                    # Sanitized example snapshots (committed to git)
│   └── 2025-01-01T12:00:00Z/   # Example timestamp directory
└── YYYY-MM-DDTHH:MM:SSZ/       # Real snapshots (gitignored for security)
```

## Security Note

**Real device snapshots are automatically excluded from git** via `.gitignore` to protect:
- IP addresses and network topology
- Device hostnames and infrastructure details
- Configuration details that could reveal security posture

## Usage

1. **Real snapshots**: Place actual device configs in timestamped directories
2. **Testing**: The framework automatically discovers the most recent snapshot directory
3. **Examples**: Use the `examples/` directory for documentation and demos

## Example Commands

```bash
# Test against most recent snapshot
pytest --csv-output --drift-mode=strict --tb=no -q

# Test against specific snapshot
pytest --snap-timestamp=2025-01-01T12:00:00Z --csv-output --drift-mode=loose -v
```