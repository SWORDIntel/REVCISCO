# Directory Structure

## Complete Project Layout

```
CISCORESET/
├── bootstrap.sh              # Main bootstrap script - RUN THIS FIRST!
├── requirements.txt           # Python dependencies
├── activate.sh               # Auto-generated venv activation script
├── README.md                 # Main documentation
│
├── src/                      # Source code directory
│   ├── __init__.py
│   ├── main.py              # Alternative entry point
│   ├── bootstrap.py         # Python bootstrap/TUI launcher
│   ├── cisco_reset.py       # Main application class
│   ├── logging_monitor.py   # Logging and monitoring system
│   ├── serial_connection.py # Serial port connection handler
│   ├── prompt_detector.py   # Prompt detection with regex
│   ├── retry_strategies.py  # Retry management
│   ├── command_executor.py  # Command execution with retries
│   ├── recovery_state_machine.py # State machine for recovery
│   ├── rommon_handler.py    # ROM monitor automation
│   ├── password_reset.py    # Password reset workflow
│   ├── system_detector.py   # System detection/inventory
│   ├── interactive_config.py # Interactive shell mode
│   ├── config_backup.py     # Configuration backup/restore
│   └── tui_interface.py     # Text User Interface
│
├── scripts/                  # Utility scripts
│   └── test_tool.py         # Component test script
│
├── docs/                     # Documentation
│   ├── README.md            # Detailed documentation
│   ├── QUICK_START.md       # Quick start guide
│   └── UI_IMPROVEMENTS.md   # UI improvements summary
│
├── config/                   # Configuration files (auto-created)
├── logs/                     # Log files (auto-created)
│   ├── cisco_reset_YYYY-MM-DD.log
│   ├── commands_YYYY-MM-DD.log
│   └── state_YYYY-MM-DD.log
│
├── monitoring/               # Monitoring data (auto-created)
│   ├── metrics_YYYY-MM-DD.json
│   └── detection_YYYY-MM-DD_HHMMSS.json
│
├── backups/                  # Configuration backups (auto-created)
│   └── running_config_YYYYMMDD_HHMMSS.txt
│
└── venv/                     # Virtual environment (auto-created)
    ├── bin/
    ├── lib/
    └── ...
```

## Bootstrap Process

The `bootstrap.sh` script performs:

1. **Python Check**: Verifies Python 3.7+ is installed
2. **Virtual Environment**: Creates isolated Python environment
3. **Dependencies**: Installs pyserial, rich, textual
4. **Directories**: Creates logs/, monitoring/, backups/, config/
5. **User Setup**: Adds user to dialout group (for serial port access)
6. **Permissions**: Makes scripts executable
7. **Verification**: Tests imports and basic functionality
8. **Activation Script**: Creates activate.sh for easy venv activation

## Entry Points

1. **bootstrap.sh** - Main setup script (run once)
2. **src/bootstrap.py** - Python bootstrap/TUI launcher
3. **src/main.py** - Alternative entry point
4. **src/cisco_reset.py** - Main application (CLI mode)

## Usage Flow

```bash
# 1. Initial setup (one time)
./bootstrap.sh

# 2. Activate virtual environment
source venv/bin/activate
# OR
source activate.sh

# 3. Run tool
python src/bootstrap.py
```
