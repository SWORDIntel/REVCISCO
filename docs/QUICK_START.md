# Quick Start Guide

## Installation

1. Install dependencies:
```bash
cd REVCISCO
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
python src/bootstrap.py
```

Or make it executable:
```bash
chmod +x src/bootstrap.py
./src/bootstrap.py
```

### Basic Workflow

1. **UART Pin Discovery**: Select option 1 for receive-only Pin 1/Pin 2 boot-output discovery.
2. **Guided Reset**: Select option 2 for the full Cisco 4321 ISR guided workflow.
3. **Connect to Router**: Select option 3, confirm the 4321 ISR console settings, then choose your TTY port.
4. **Password Reset**: Select option 4 if you are already connected.
5. **System Detection**: Select option 5 to view licenses, hardware, software info.
6. **Interactive Mode**: Select option 6 to execute Cisco IOS commands directly.
7. **UART Firmware Dump**: Select option 14 to capture a raw UART byte stream to `firmware_dumps/`.
8. **Decompress Dump**: Select option 15 to decompress or extract an existing dump. Choose `binwalk` format for broader firmware carving when binwalk is installed.

The tool now shows a Cisco 4321 ISR preflight before connecting, checks router identity after manual connection when possible, and warns on startup if a previous recovery stopped before cleanup.

### UART Pin Discovery Wiring

Use option 1 before reset work when you are identifying the Cisco `UART_DEBUG` header.

Correct first-test wiring:

```text
Adapter GND  -> Cisco Pin 1
Adapter RX   -> Cisco Pin 2
```

Everything else stays disconnected:

```text
Adapter TX/VCC/CTS/DTR -> disconnected
Cisco Pin 3            -> empty
Cisco Pin 4            -> empty
```

With the current wire colors, use brown/tan from adapter GND on Cisco Pin 1. Use the adapter RX wire on Cisco Pin 2. If yellow is plugged into adapter RX, yellow goes to Cisco Pin 2. Remove red, orange, and any wire on Cisco Pin 3 or Pin 4.

The pass condition is exactly: Pin 1 = brown/tan GND, Pin 2 = adapter RX wire, Pin 3 = empty, Pin 4 = empty.

## Testing

Run the test script to verify components:
```bash
python scripts/test_tool.py
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
