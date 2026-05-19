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

1. **UART Pin Discovery**: Select option 1 for receive-only candidate-pair boot-output discovery.
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

Discovery mode supports common cable styles including the FT232RL 6-pin header (`DTR RXI TXO VCC CTS GND`), generic 6-pin USB-TTL boards, 4/5-pin USB-TTL leads, 3-wire UART leads, keyed JST/Dupont harnesses, RJ45/rollover console cables, and DB9/RS-232 adapters.

For this setup, use the FT232RL layout:

```text
DTR  RXI  TXO  VCC  CTS  GND
```

Start with Cisco Pin 1 as the ground candidate and Cisco Pin 2, Pin 3, Pin 4 as signal candidates unless your photo/markings show otherwise.

Correct receive-only test wiring:

```text
FT232RL GND  -> one Cisco ground candidate
FT232RL RXI  -> one Cisco TX-output candidate
```

Everything else stays disconnected:

```text
Adapter TX/VCC/3V3/5V/CTS/DTR/RTS -> disconnected
All other Cisco pins              -> empty
```

Test combinations one at a time: select the cable type in option 1, keep adapter GND on a likely ground, select the connected FT232RL signal, enter one or more Cisco candidate labels, select a baud or enable auto-baud sweep, power cycle during each RXI listen window, and record the first pair that produces readable Cisco boot text. Try 9600 first, then 115200 if 9600 is silent. `RXI` listens to Cisco TX output. `TXO` is adapter transmit output and is only useful later as a suspected Cisco RX/input test.

The discovery result classifies each attempt as `boot_text`, `readable_unknown`, `unreadable_output`, `no_output`, `connection_failed`, `txo_candidate_recorded`, or `skipped`. It also reports readability quality, shows next-step recommendations, and writes a combined log plus `.session.json` and `.attempts.csv` files containing the tested cable type, notes, attempts, and generated pin map.

The session summary also prints a final wiring plan. The target end state is `FT232RL GND -> Cisco GND`, `FT232RL RXI -> Cisco TX/output`, `FT232RL TXO -> Cisco RX/input`, with `VCC`, `DTR`, and `CTS` disconnected.

For the earlier suspected mapping, use brown/tan from adapter GND on Cisco Pin 1 and the adapter RXI wire on Cisco Pin 2. If yellow is plugged into adapter RXI, yellow is the RXI test wire. Keep red, orange, adapter power pins, and every non-test Cisco pin disconnected.

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
