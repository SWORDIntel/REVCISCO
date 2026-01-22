# Quick Start Guide

## Installation

1. Install dependencies:
```bash
cd tools/CISCORESET
pip install -r requirements.txt
```

2. Add user to dialout group (for serial port access):
```bash
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

## Usage

### Start the Tool

```bash
python bootstrap.py
```

Or make it executable:
```bash
chmod +x bootstrap.py
./bootstrap.py
```

### Basic Workflow

1. **Connect to Router**: Select option 1, choose your TTY port
2. **Password Reset**: Select option 2, follow the guided workflow
3. **System Detection**: Select option 3 to view licenses, hardware, software info
4. **Interactive Mode**: Select option 4 to execute Cisco IOS commands directly

## Testing

Run the test script to verify components:
```bash
python test_tool.py
```

## Troubleshooting

### "No module named 'serial'"
Install dependencies: `pip install -r requirements.txt`

### "Permission denied" on port
Add user to dialout group: `sudo usermod -a -G dialout $USER`

### "No TTY ports found"
- Check cable connection
- Verify port exists: `ls -l /dev/ttyS* /dev/ttyUSB*`
- Check permissions

## Features

- ✅ Single entry point (`bootstrap.py`)
- ✅ Beautiful TUI interface
- ✅ Automatic break sequence with 5 fallback methods
- ✅ ROM monitor automation
- ✅ System detection (licenses, hardware, software)
- ✅ Interactive command mode
- ✅ Extensive logging and monitoring
- ✅ Multiple retry strategies
