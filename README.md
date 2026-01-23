# CISCORESET - Cisco 4321 ISR Password Reset Tool

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A robust, production-ready Python tool for automated password recovery on Cisco 4321 ISR routers via direct TTY console connection. Features a beautiful Text User Interface (TUI), comprehensive logging, multiple retry strategies, and full automation of the ROM monitor recovery process.

## 🚀 Quick Start

### Single Command Installation

```bash
./bootstrap.sh
```

The bootstrap script automatically:
- ✅ Checks Python version (3.7+)
- ✅ Creates isolated virtual environment
- ✅ Installs all dependencies
- ✅ Sets up user permissions (dialout group)
- ✅ Creates directory structure
- ✅ Verifies installation

### Run the Tool

```bash
source venv/bin/activate
python src/bootstrap.py
```

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    CISCORESET Tool Architecture                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Bootstrap  │  ← Initial setup, dependency check, venv creation
│   Script     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   TUI Main   │  ← Text User Interface (Rich library)
│   Interface  │
└──────┬───────┘
       │
       ├─────────────────────────────────────────────────┐
       │                                                 │
       ▼                                                 ▼
┌──────────────┐                              ┌──────────────┐
│   Serial     │  ← TTY/Serial connection     │   Settings   │
│  Connection  │                              │   Manager    │
└──────┬───────┘                              └──────────────┘
       │
       ├─────────────────────────────────────────────────┐
       │                                                 │
       ▼                                                 ▼
┌──────────────┐                              ┌──────────────┐
│   Command    │  ← Execute IOS commands      │   Prompt     │
│  Executor    │                              │  Detector    │
└──────┬───────┘                              └──────┬───────┘
       │                                               │
       ├───────────────────────────────────────────────┤
       │                                               │
       ▼                                               ▼
┌──────────────┐                              ┌──────────────┐
│    ROM       │  ← Break sequence, ROMmon    │   Recovery   │
│   Handler    │                              │   State      │
└──────┬───────┘                              │   Machine    │
       │                                       └──────────────┘
       │
       ▼
┌──────────────┐
│  Password    │  ← Reset enable secret, console, VTY
│   Reset      │
└──────┬───────┘
       │
       ├─────────────────────────────────────────────────┐
       │                                                 │
       ▼                                                 ▼
┌──────────────┐                              ┌──────────────┐
│   System     │  ← Detect licenses, hardware │   Config     │
│  Detector    │                              │   Backup     │
└──────────────┘                              └──────────────┘

┌──────────────┐
│   Logging    │  ← Multi-level logging, metrics, monitoring
│   Monitor    │
└──────────────┘
```

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│              Password Reset Workflow (Guided Mode)               │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ├─► [1] Physical Preparation
  │     ├─► Check serial cable connections
  │     ├─► Verify router is powered ON
  │     └─► Confirm physical access
  │
  ├─► [2] Power Cycle Router
  │     ├─► User: Turn OFF router
  │     ├─► Wait 10 seconds (countdown)
  │     └─► User: Turn ON router
  │
  ├─► [3] Connect to Router
  │     ├─► Auto-detect or select TTY port
  │     ├─► Open serial connection
  │     └─► Initialize command executor
  │
  ├─► [4] Wait for Boot Sequence
  │     └─► Monitor boot output
  │
  ├─► [5] Send Break Sequence
  │     ├─► Method 1: Ctrl+Break
  │     ├─► Method 2: Ctrl+C (fallback)
  │     ├─► Method 3: Multiple breaks (fallback)
  │     └─► Retry with exponential backoff
  │
  ├─► [6] Enter ROM Monitor
  │     └─► Detect ROMmon prompt
  │
  ├─► [7] Set Config Register
  │     └─► confreg 0x2142 (skip startup config)
  │
  ├─► [8] Reboot Router
  │     └─► reset command
  │
  ├─► [9] Wait for IOS Boot
  │     └─► Monitor for IOS prompt
  │
  ├─► [10] System Detection
  │      ├─► Detect licenses
  │      ├─► Detect hardware
  │      ├─► Detect software
  │      └─► Export results
  │
  ├─► [11] Reset Password
  │      ├─► Enter config mode
  │      ├─► Set enable secret
  │      └─► Exit config mode
  │
  ├─► [12] Restore Config Register
  │      └─► confreg 0x2102 (normal boot)
  │
  ├─► [13] Save Configuration
  │      └─► write memory
  │
  └─► [14] SUCCESS
         └─► Password reset complete!
```

## 📋 Features

### Core Features
- **🎯 Guided Workflow** - Step-by-step instructions with physical action prompts
- **🖥️ Beautiful TUI Interface** - Rich library-based Text User Interface with 12 menu options
- **🔄 Automatic Break Sequence** - 5 fallback methods with intelligent retry logic
- **⚙️ ROM Monitor Automation** - Full automation of password recovery workflow
- **🔍 System Detection** - Comprehensive license, hardware, software, and feature detection
- **💻 Interactive Command Mode** - Full interactive shell once config access is gained
- **📊 Extensive Logging** - Multi-level logging with rotation and JSON export
- **🛡️ Multiple Retry Strategies** - Exponential backoff, linear, fixed delay, and adaptive retries
- **📁 State Machine** - Robust state tracking with rollback capabilities
- **💾 Configuration Backup** - Automatic backup and restore of router configurations

### Advanced Features
- **⚙️ Settings Management** - Persistent settings with JSON storage
- **📈 Metrics Display** - Real-time connection and operation metrics
- **🔧 Individual Detection** - Run specific detection functions independently
- **🔐 Advanced Password Reset** - Reset console, VTY, and enable passwords separately
- **📝 Log Viewer** - Browse and view log files in TUI
- **🔄 Auto-Reconnect** - Automatic reconnection on connection loss
- **💾 Connection Persistence** - Remembers last used port

## 📁 Project Structure

```
CISCORESET/
├── bootstrap.sh              # Main bootstrap script - RUN THIS FIRST!
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── src/                       # Source code
│   ├── bootstrap.py          # Python bootstrap/TUI launcher
│   ├── cisco_reset.py        # Main application class
│   ├── tui_interface.py      # Text User Interface
│   ├── serial_connection.py  # Serial port connection handler
│   ├── command_executor.py   # Command execution with retries
│   ├── prompt_detector.py    # Prompt detection with regex
│   ├── rommon_handler.py     # ROM monitor automation
│   ├── password_reset.py     # Password reset workflow
│   ├── system_detector.py    # System detection/inventory
│   ├── recovery_state_machine.py # State machine for recovery
│   ├── retry_strategies.py   # Retry management
│   ├── interactive_config.py # Interactive shell mode
│   ├── config_backup.py      # Configuration backup/restore
│   ├── logging_monitor.py    # Logging and monitoring system
│   └── settings_manager.py   # Settings management
│
├── docs/                      # Documentation
│   ├── QUICK_START.md        # Quick start guide
│   ├── README.md             # Detailed documentation
│   ├── UI_IMPROVEMENTS.md    # UI improvements summary
│   ├── INSTALL.md            # Installation guide
│   ├── STRUCTURE.md           # Directory structure
│   ├── EASY_WINS_IMPLEMENTED.md # Feature implementation summary
│   ├── FUNCTION_ACCESSIBILITY_REPORT.md # Function access report
│   └── TUI_FUNCTION_VERIFICATION.md # TUI verification
│
├── scripts/                   # Utility scripts
│   └── test_tool.py          # Component test script
│
├── config/                    # Configuration files (auto-created)
├── logs/                      # Log files (auto-created)
├── monitoring/                # Monitoring data (auto-created)
├── backups/                   # Configuration backups (auto-created)
└── venv/                      # Virtual environment (auto-created)
```

## 🎯 Usage Guide

### Guided Workflow (Recommended for First-Time Users)

1. **Start the Tool**
   ```bash
   source venv/bin/activate
   python src/bootstrap.py
   ```

2. **Select Option 1: Guided Workflow**
   - Follow on-screen instructions
   - Perform physical actions when prompted:
     - Turn OFF router
     - Wait 10 seconds
     - Turn ON router
   - Tool handles all technical steps automatically

### Manual Workflow

1. **Connect to Router** (Option 2)
   - Select TTY port from list
   - Connection is established automatically

2. **Run Password Reset** (Option 3)
   - Confirm workflow start
   - Monitor progress through 7 steps
   - Enter new password when prompted

3. **View Results** (Option 4)
   - System detection results
   - Export to JSON/YAML/TXT

### Menu Options

| Option | Function | Description |
|--------|----------|-------------|
| 1 | Guided Workflow | Step-by-step instructions with physical prompts |
| 2 | Connect to Router | Manual connection to router |
| 3 | Password Reset Workflow | Automated password reset process |
| 4 | System Detection | Detect licenses, hardware, software |
| 5 | Interactive Command Mode | Execute Cisco IOS commands directly |
| 6 | View Logs | Browse and view log files |
| 7 | Settings | Configure application settings |
| 8 | Exit | Exit application |
| 9 | View Metrics | View real-time metrics and statistics |
| 10 | Configuration Backup/Restore | Backup and restore router configs |
| 11 | Individual Detection Options | Run specific detection functions |
| 12 | Advanced Password Reset | Reset individual password types |

## 🔧 Prerequisites

- **Python 3.7+** - Required for the tool
- **Linux System** - For TTY/serial port access
- **Direct TTY Connection** - Physical connection to Cisco 4321 ISR console port
- **Serial/TTY Cable** - Console cable connected to router and computer
- **sudo Access** - For adding user to dialout group (one-time setup)

## 📦 Installation

### Automated Installation (Recommended)

```bash
# Navigate to tool directory
cd tools/CISCORESET

# Run bootstrap script
./bootstrap.sh

# Activate virtual environment
source venv/bin/activate

# Run tool
python src/bootstrap.py
```

### Manual Installation

See [docs/INSTALL.md](docs/INSTALL.md) for detailed manual installation instructions.

## 💡 Common Workflows

### First-Time Password Reset

```
1. Run: python src/bootstrap.py
2. Select: Option 1 (Guided Workflow)
3. Follow prompts:
   - Verify connections
   - Turn OFF router
   - Wait 10 seconds
   - Turn ON router
4. Tool automatically:
   - Connects to router
   - Sends break sequence
   - Enters ROM monitor
   - Resets password
   - Saves configuration
```

### Quick System Inventory

```
1. Connect to router (Option 2)
2. Select: Option 4 (System Detection)
3. View results
4. Export if needed (JSON/YAML/TXT)
```

### Configuration Backup

```
1. Connect to router (Option 2)
2. Select: Option 10 (Configuration Backup/Restore)
3. Choose: Backup Running Configuration
4. File saved to backups/ directory
```

## 🧪 Testing

Test all components:

```bash
source venv/bin/activate
python scripts/test_tool.py
```

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get started quickly
- **[Installation Guide](docs/INSTALL.md)** - Detailed installation instructions
- **[Directory Structure](docs/STRUCTURE.md)** - Project organization
- **[UI Improvements](docs/UI_IMPROVEMENTS.md)** - UI features and improvements
- **[Function Accessibility](docs/FUNCTION_ACCESSIBILITY_REPORT.md)** - Complete function inventory
- **[TUI Verification](docs/TUI_FUNCTION_VERIFICATION.md)** - TUI feature verification
- **[Easy Wins Implementation](docs/EASY_WINS_IMPLEMENTED.md)** - Feature implementation summary

## 🛠️ Troubleshooting

### Permission Denied on Serial Port

```bash
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

### No Module Named 'serial'

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Or re-run bootstrap
./bootstrap.sh
```

### No TTY Ports Found

- Check cable connection
- Verify port exists: `ls -l /dev/ttyS* /dev/ttyUSB*`
- Check permissions: `groups | grep dialout`

### Break Sequence Fails

- Try power cycling router again
- Check serial connection quality
- Verify baud rate (default: 9600)
- Try manual break sequence

## 🔒 Security

**⚠️ IMPORTANT**: This tool is for authorized password recovery only. Use responsibly and only on routers you own or have explicit permission to access.

## 📝 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

## 🙏 Acknowledgments

- Built for Cisco 4321 ISR routers
- Uses [pyserial](https://github.com/pyserial/pyserial) for serial communication
- Uses [rich](https://github.com/Textualize/rich) for beautiful terminal UI

---

**Made with ❤️ for network engineers**
