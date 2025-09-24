# cfg-drift - Network Configuration Compliance Testing

A comprehensive tool that validates network device configurations using the Supreme Golden Config approach. Tests both required configurations (must have) and forbidden configurations (must not have).

## Features

- **✅ Expected Configuration Testing**: Validates required configs from golden templates
- **🚫 Forbidden Configuration Detection**: Detects forbidden configs from prohibited patterns
- **📊 CSV Compliance Reports**: Generates timestamped compliance reports
- **🔧 Auto-Generated Tests**: Dynamically creates tests based on golden config structure
- **📈 Multiple Test Modes**: Strict (exact match) and Loose (presence only) validation

## Quick Start

### 1. Setup
```bash
# Clone the repository
git clone https://github.com/ainglese-dev/cfg-drift.git
cd cfg-drift

# Install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install pytest
```

### 2. Add Your Configurations

#### Golden Config Templates
- **Expected**: `supreme_golden_cfg/expected_Q1/fragments/[category]/`
- **Forbidden**: `supreme_golden_cfg/forbidden_Q1/fragments/[category]/`

#### Device Snapshots
- **Current snapshots**: `snapshots/YYYY-MM-DDTHH:MM:SSZ/device.cfg`
- **Examples**: `snapshots/examples/` (for reference)

### 3. Generate Tests
```bash
# Auto-generate test files for all categories
python generate_tests.py
```

### 4. Run Compliance Tests
```bash
# Clean output with CSV report
pytest --csv-output --drift-mode=strict --tb=no -q

# Verbose output with printed CSV
pytest --csv-output --print-csv --drift-mode=loose -v

# Test specific category
pytest tests/expected/test_banners_required.py --csv-output -v
```

## Project Structure

```
cfg-drift/
├── supreme_golden_cfg/           # Golden configuration templates
│   ├── expected_Q1/fragments/    # Required configurations
│   │   ├── banners/             # Security banners
│   │   ├── aaa/                 # Authentication configs
│   │   ├── ntp/                 # Time synchronization
│   │   └── ...                  # Additional categories
│   └── forbidden_Q1/fragments/   # Forbidden configurations
│       ├── features/            # Forbidden features
│       ├── debug/               # Debug commands
│       └── protocols/           # Insecure protocols
├── snapshots/                   # Device configuration snapshots
│   ├── examples/                # Sanitized examples (committed)
│   └── YYYY-MM-DDTHH:MM:SSZ/   # Real snapshots (gitignored)
├── tests/                       # Auto-generated test files
│   ├── expected/                # Required config tests
│   ├── forbidden/               # Forbidden config tests
│   └── common/                  # Shared utilities
├── results/                     # CSV compliance reports (gitignored)
└── generate_tests.py            # Test file generator
```

## Extending the Framework

### Add New Configuration Category

1. **Add Golden Config Template**:
   ```bash
   mkdir supreme_golden_cfg/expected_Q1/fragments/ospf
   echo "router ospf 1" > supreme_golden_cfg/expected_Q1/fragments/ospf/ospf-corporate.cfg
   ```

2. **Generate Test**:
   ```bash
   python generate_tests.py  # Creates tests/expected/test_ospf_required.py
   ```

3. **Test Immediately**:
   ```bash
   pytest --csv-output --drift-mode=strict --tb=no -q
   ```

## Test Modes

- **Strict Mode**: Exact content matching for expected configs, all forbidden configs prohibited
- **Loose Mode**: Presence-only checking for expected configs, all forbidden configs still prohibited

## CSV Output Format

```csv
Timestamp,Device,Category,Template_Used,Status,Mode,Details
2025-01-01T12:00:00,spine01,banners,banner-01.cfg,PASS,strict,Exact match
2025-01-01T12:00:00,leaf01,features,features-01.cfg,FAILED,strict,FORBIDDEN: Found: feature bash
```

## Security

- **Real device snapshots** are automatically excluded from git
- **IP addresses and network topology** are not committed
- **CSV compliance reports** stay local for security
- **Only framework code and sanitized examples** are version controlled

## Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.