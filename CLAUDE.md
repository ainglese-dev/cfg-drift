# cfg-drift - Network Configuration Compliance Testing

A comprehensive tool that validates network device configurations using the Supreme Golden Config approach. Tests both required configurations (must have) and forbidden configurations (must not have).

## What This Tool Does

- **Validates** required configurations from expected golden templates
- **Detects** forbidden configurations from forbidden golden templates
- **Supports** multiple configuration categories (banners, DNS, NTP, features, etc.)
- **Provides** visual structure for easy management and expansion

Think of it as a comprehensive compliance checker for network device configurations - ensuring devices have what they should and don't have what they shouldn't.

## Supreme Golden Config Structure

```
supreme_golden_cfg/
├── expected_Q1/           # MUST HAVE configurations (PASS when found)
│   └── fragments/
│       ├── banners/       # Required security banners
│       ├── dns/           # Required DNS settings
│       ├── domain/        # Required domain configs
│       └── ntp/           # Required NTP servers
└── forbidden_Q1/          # MUST NOT HAVE configurations (FAIL when found)
    └── fragments/
        └── features/      # Forbidden features/commands
```

## Testing Modes

**Strict Mode** (default): All expected configs must match exactly, all forbidden configs forbidden
**Loose Mode**: Expected configs need only be present, forbidden configs still forbidden

Set mode with: `--drift-mode=loose` (CLI flag)

## Quick Start

### 1. Run the Tests
```bash
# Clean output (recommended) - simple pass/fail status
pytest --drift-mode=strict --tb=no -q

# Loose mode - clean output
pytest --drift-mode=loose --tb=no -q

# Verbose output (detailed failures)
pytest --drift-mode=strict -v

# See all available options
pytest --help
```

### 2. Check Results

**Strict Mode:**
- ✅ **PASS**: Device banner exists AND matches approved template
- ❌ **FAIL**: Banner missing OR content doesn't match templates

**Loose Mode:**
- ✅ **PASS**: Device has any banner (content ignored)
- ❌ **FAIL**: No banner found

### 3. Basic Workflow
1. Take device config snapshots → place in `snapshots/<timestamp>/`
2. Define approved banners → place in `fragments/banners/`
3. Run tests to check compliance

## Project Structure

```
cfg-drift/
├── snapshots/                    # Device configuration snapshots
│   └── 2025-09-25T12:00:00Z/    # Timestamp directory (auto-selected)
│       ├── spine01.cfg          # Device config files
│       └── leaf01.cfg
├── fragments/                   # Approved templates
│   └── banners/                # Banner templates
│       └── banner1.cfg         # Example approved banner
├── tests/                      # Test files
│   └── test_banner_presence.py # Main test logic
└── results/                    # Test outputs (if any)
```

## Adding New Tests (Super Simple!)

### Adding Device Snapshots
1. **Create timestamped directory**: `snapshots/2025-10-01T14:30:00Z/`
2. **Add device configs**: Copy `.cfg` files into the timestamp directory
3. **Run tests**: `pytest -q` (automatically uses newest timestamp)

### Adding New Banner Templates
1. **Create fragment file**: `fragments/banners/new-banner.cfg`
2. **Copy full banner block** including:
   - Header line: `banner motd ^C`
   - Banner content: `Welcome to Device...`
   - Terminator: `^C`
3. **Test**: Device banners will be checked against ALL fragments

### Example Banner Fragment
```
banner motd ^C
Welcome to Corporate Network
Authorized Access Only
Violations will be prosecuted
^C
```

## Testing Commands

### Basic Commands

```bash
# Strict mode (default) - exact content matching
pytest -q

# Loose mode - any banner content acceptable
pytest --drift-mode=loose -q

# Verbose output (shows details)
pytest -v

# Test specific timestamp
pytest --snap-timestamp=2025-09-24T12:00:00Z -q

# Test with custom directories
pytest --snap-directory=my-snapshots --fragments-dir=my-fragments -q

# Combine multiple options
pytest --drift-mode=loose --snap-timestamp=2025-09-24T12:00:00Z -v

# See all available options
pytest --help
```

### CLI Options

**Available Flags:**
- `--drift-mode` → testing mode: `strict` | `loose` (default: `strict`)
- `--snap-directory` → snapshots directory (default: `snapshots`)
- `--snap-timestamp` → specific timestamp folder (default: most recent)
- `--expected-dir` → expected configs directory (default: `supreme_golden_cfg/expected_Q1/fragments`)
- `--forbidden-dir` → forbidden configs directory (default: `supreme_golden_cfg/forbidden_Q1/fragments`)
- `--fragments-dir` → legacy banners directory (default: `fragments/banners`)

**Get Help:**
```bash
pytest --help  # Shows all options with detailed descriptions
```

## Common Issues & Solutions

### "No snapshot timestamp directory found"
- **Problem**: No snapshot directories exist
- **Solution**: Create `snapshots/YYYY-MM-DDTHH:MM:SSZ/` with `.cfg` files

### "No .cfg files found"
- **Problem**: Timestamp directory is empty
- **Solution**: Add device config files ending in `.cfg`

### "banner did not match any approved fragment"
- **Problem**: Device banner differs from all templates
- **Solution**: Either fix device banner OR add new approved fragment

### "No fragments to compare against"
- **Problem**: No approved banner templates
- **Solution**: Add at least one `.cfg` file to `fragments/banners/`

## How Banner Matching Works

1. **Extract**: Find `banner motd ^C...^C` block from device config
2. **Normalize**: Remove timestamps and extra whitespace
3. **Compare**: Check if it exactly matches ANY fragment
4. **Report**: Pass if match found, fail otherwise

The tool is smart about:
- Different banner delimiters (`^C`, `^D`, etc.)
- Generated timestamps in configs
- Whitespace differences
- Inline vs multi-line banner formats

## Adding Your First Test

1. **Create snapshot directory**:
   ```bash
   mkdir -p snapshots/$(date -u +%Y-%m-%dT%H:%M:%SZ)
   ```

2. **Add a device config** with banner:
   ```bash
   cat > snapshots/2025-10-01T14:00:00Z/router01.cfg << 'EOF'
   banner motd ^C
   Welcome to Router01
   Authorized users only
   ^C
   hostname router01
   EOF
   ```

3. **Create matching fragment**:
   ```bash
   cat > fragments/banners/standard-banner.cfg << 'EOF'
   banner motd ^C
   Welcome to Router01
   Authorized users only
   ^C
   EOF
   ```

4. **Run test**:
   ```bash
   pytest -v
   ```

You should see: `test_banner_matches_any_fragment_full[router01] PASSED`

That's it! You've successfully created your first banner compliance test.