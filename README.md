# REVCISCO - Cisco 4321 ISR Password Reset Tool

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

## 📋 Features

- **🎯 Single Bootstrap Script** - Complete setup with one command
- **🖥️ Beautiful TUI Interface** - Rich library-based Text User Interface
- **🔄 Automatic Break Sequence** - 5 fallback methods with intelligent retry logic
- **⚙️ ROM Monitor Automation** - Full automation of password recovery workflow
- **🔍 System Detection** - Comprehensive license, hardware, software, and feature detection
- **💻 Interactive Command Mode** - Full interactive shell once config access is gained
- **📊 Extensive Logging** - Multi-level logging with rotation and JSON export
- **🛡️ Multiple Retry Strategies** - Exponential backoff, linear, fixed delay, and adaptive retries
- **📁 State Machine** - Robust state tracking with rollback capabilities
- **💾 Configuration Backup** - Automatic backup and restore of router configurations

## 📁 Project Structure

```
REVCISCO/
├── bootstrap.sh              # Main bootstrap script - RUN THIS FIRST!
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── INSTALL.md                 # Detailed installation guide
├── STRUCTURE.md               # Directory structure documentation
│
├── src/                       # Source code
│   ├── main.py               # Alternative entry point
│   ├── bootstrap.py          # Python bootstrap/TUI launcher
│   ├── cisco_reset.py        # Main application class
│   ├── logging_monitor.py    # Logging and monitoring system
│   ├── serial_connection.py  # Serial port connection handler
│   ├── prompt_detector.py   # Prompt detection with regex
│   ├── retry_strategies.py   # Retry management
│   ├── command_executor.py   # Command execution with retries
│   ├── recovery_state_machine.py # State machine for recovery
│   ├── rommon_handler.py     # ROM monitor automation
│   ├── password_reset.py     # Password reset workflow
│   ├── system_detector.py   # System detection/inventory
│   ├── interactive_config.py # Interactive shell mode
│   ├── config_backup.py     # Configuration backup/restore
│   └── tui_interface.py     # Text User Interface
│
├── scripts/                   # Utility scripts
│   └── test_tool.py          # Component test script
│
├── docs/                      # Documentation
│   ├── QUICK_START.md        # Quick start guide
│   └── UI_IMPROVEMENTS.md    # UI improvements summary
│
├── config/                    # Configuration files (auto-created)
├── logs/                      # Log files (auto-created)
├── monitoring/                # Monitoring data (auto-created)
├── backups/                   # Configuration backups (auto-created)
└── venv/                      # Virtual environment (auto-created)
```

## 🔧 Prerequisites

- **Python 3.7+** - Required for the tool
- **Linux System** - For TTY/serial port access
- **Direct TTY Connection** - Physical connection to Cisco 4321 ISR console port
- **sudo Access** - For adding user to dialout group (one-time setup)

## 📦 Installation

### Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/SWORDIntel/REVCISCO.git
cd REVCISCO

# Run bootstrap script
./bootstrap.sh
```

### Manual Installation

See [INSTALL.md](INSTALL.md) for detailed manual installation instructions.

## 💡 Usage

### TUI Mode (Recommended)

```bash
source venv/bin/activate
python src/bootstrap.py
```

The TUI provides:
- Connection status display
- Port selection menu
- Step-by-step workflow progress
- System detection results
- Interactive command mode
- Error handling with suggestions

### CLI Mode

```bash
source venv/bin/activate
python src/cisco_reset.py --port /dev/ttyS0 --no-tui
```

## 🔄 Password Recovery Workflow

The tool automates the complete Cisco password recovery process:

1. **Connection** - Connect to router via TTY
2. **Break Sequence** - Automatically sends break during boot
3. **ROM Monitor** - Enters ROM monitor mode
4. **Config Register** - Sets register to skip startup config (0x2142)
5. **Reboot** - Reboots router
6. **System Detection** - Detects licenses, hardware, software
7. **Password Reset** - Resets enable secret password
8. **Restore Config** - Restores config register (0x2102)
9. **Save Config** - Saves configuration

## 🧪 Testing

Test all components:

```bash
source venv/bin/activate
python scripts/test_tool.py
```

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md) - Get started quickly
- [Installation Guide](INSTALL.md) - Detailed installation instructions
- [Directory Structure](STRUCTURE.md) - Project organization
- [UI Improvements](docs/UI_IMPROVEMENTS.md) - UI features and improvements

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

## 🔒 Security

**⚠️ IMPORTANT**: This tool is for authorized password recovery only. Use responsibly and only on devices you own or have explicit permission to access.

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

**Made with ❤️ for network engineers(Except that one BT engineer i accidentally may have stolen the ISR off in the 3.2 seconds his back was turned,NEXT TIME BRO DONT KEEP YOUR SHIT ONTOP OF THE TRASH IM A GREMLIN)**
