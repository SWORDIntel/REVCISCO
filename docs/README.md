# Cisco 4321 ISR Password Reset Tool

A robust Python-based tool that automates the password recovery process for Cisco 4321 ISR routers via direct TTY connection to the board's console port.

## Quick Start

### Single Command Setup

```bash
./bootstrap.sh
```

This will:
- Check Python version (3.7+)
- Create virtual environment
- Install all dependencies
- Set up user permissions (dialout group)
- Create directory structure
- Verify installation

### After Bootstrap

```bash
# Activate virtual environment
source venv/bin/activate

# Or use the activation script
source activate.sh

# Run the tool
python src/bootstrap.py
```

## Directory Structure

```
CISCORESET/
├── bootstrap.sh          # Main bootstrap script (run this first!)
├── requirements.txt      # Python dependencies
├── activate.sh           # Virtual environment activation script (auto-generated)
├── src/                  # Source code
│   ├── __init__.py
│   ├── main.py          # Alternative entry point
│   ├── bootstrap.py     # Python bootstrap/TUI launcher
│   ├── cisco_reset.py   # Main application
│   ├── logging_monitor.py
│   ├── serial_connection.py
│   ├── prompt_detector.py
│   ├── retry_strategies.py
│   ├── command_executor.py
│   ├── recovery_state_machine.py
│   ├── rommon_handler.py
│   ├── password_reset.py
│   ├── system_detector.py
│   ├── interactive_config.py
│   ├── config_backup.py
│   └── tui_interface.py
├── scripts/              # Utility scripts
│   └── test_tool.py     # Component test script
├── docs/                 # Documentation
│   ├── README.md
│   ├── QUICK_START.md
│   └── UI_IMPROVEMENTS.md
├── config/               # Configuration files
├── logs/                 # Log files (auto-created)
├── monitoring/           # Monitoring data (auto-created)
├── backups/             # Configuration backups (auto-created)
└── venv/                # Virtual environment (auto-created)
```

## Features

- **Single Bootstrap Script**: `./bootstrap.sh` sets up everything
- **Virtual Environment**: Isolated Python environment
- **User Setup**: Automatically adds user to dialout group
- **Text User Interface**: Beautiful TUI with rich library
- **Automatic Break Sequence**: Multiple methods with retry logic
- **ROM Monitor Automation**: Full automation of recovery process
- **System Detection**: Comprehensive license, hardware, software detection
- **Interactive Mode**: Full interactive shell once config access is gained
- **Extensive Logging**: Multi-level logging with rotation
- **Multiple Retry Methods**: Adaptive retry strategies

## Prerequisites

- Python 3.7 or higher
- Linux system (for TTY access)
- Direct TTY connection to Cisco 4321 ISR console port
- sudo access (for adding user to dialout group)

## Installation

1. **Run bootstrap script**:
   ```bash
   ./bootstrap.sh
   ```

2. **If prompted, log out and back in** (for dialout group to take effect)

3. **Activate virtual environment and run**:
   ```bash
   source venv/bin/activate
   python src/bootstrap.py
   ```

## Usage

### TUI Mode (Recommended)

```bash
source venv/bin/activate
python src/bootstrap.py
```

### CLI Mode

```bash
source venv/bin/activate
python src/cisco_reset.py --port /dev/ttyS0 --no-tui
```

## Testing

Test components:
```bash
source venv/bin/activate
python scripts/test_tool.py
```

## Troubleshooting

### "Permission denied" on serial port
- Run: `sudo usermod -a -G dialout $USER`
- Log out and back in

### "No module named 'serial'"
- Activate venv: `source venv/bin/activate`
- Or re-run: `./bootstrap.sh`

### "No TTY ports found"
- Check: `ls -l /dev/ttyS* /dev/ttyUSB*`
- Verify cable connection
- Check permissions

## Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [UI Improvements](docs/UI_IMPROVEMENTS.md)

## License

See LICENSE file for details.

## Disclaimer

This tool is for authorized password recovery only. Use responsibly.
