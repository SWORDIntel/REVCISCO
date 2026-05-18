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

1. **Guided Reset**: Select option 1 for the full Cisco 4321 ISR guided workflow
2. **Connect to Router**: Select option 2, confirm the 4321 ISR console settings, then choose your TTY port
3. **Password Reset**: Select option 3 if you are already connected
4. **System Detection**: Select option 4 to view licenses, hardware, software info
5. **Interactive Mode**: Select option 5 to execute Cisco IOS commands directly
6. **UART Firmware Dump**: Select option 13 to capture a raw UART byte stream to `firmware_dumps/`
7. **Decompress Dump**: Select option 14 to decompress or extract an existing dump. Choose `binwalk` format for broader firmware carving when binwalk is installed.

The tool now shows a Cisco 4321 ISR preflight before connecting, checks router identity after manual connection when possible, and warns on startup if a previous recovery stopped before cleanup.

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
