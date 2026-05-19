# CISCORESET Function Accessibility Report

## Status

All major workflows are reachable from the TUI. The current main menu has 15 options and includes the Cisco 4321 ISR preflight, receive-only UART pin discovery, configuration backup/restore, firmware dumping, and dump decompression.

## Main Menu Options

1. **UART Pin Discovery**
   - Receive-only candidate-pair wiring checklist
   - Handles FT232RL 6-pin headers, 6-pin USB-TTL boards, 4/5-pin leads, 3-wire UART leads, keyed harnesses, RJ45 console cables, DB9/RS-232 adapters, and unknown cable types
   - Keeps TX, power, CTS, DTR, and RTS disconnected during receive-only probing
   - Distinguishes FT232RL RXI passive capture from TXO candidate recording, then supports multiple candidates, auto-baud sweep, output classification, readability metrics, session JSON/CSV export, pin map summaries, recommendations, notes, and a TX introduction checklist
   - Saves discovery logs under `logs/uart_pin_discovery_*.log`

2. **Guided Cisco 4321 ISR Reset**
   - Runs the full guided password reset flow
   - Includes Cisco 4321 ISR console preflight and physical prompts
   - Connects, breaks into ROMmon, resets passwords, restores config register, and saves

3. **Connect to Cisco 4321 ISR**
   - Exposes `connect()`
   - Shows serial port detection and Cisco console settings
   - Persists the last selected port

4. **Password Reset Workflow**
   - Exposes `run_password_reset_workflow()`
   - Shows workflow steps, progress, and error handling

5. **System Detection/Inventory**
   - Exposes `run_system_detection_only()`
   - Runs `detect_all()`
   - Exports detection results

6. **Interactive Command Mode**
   - Exposes `InteractiveConfig.start()`
   - Supports direct IOS command execution, history, and help

7. **View Logs**
   - Exposes `show_log_viewer()`
   - Supports log selection and viewing recent lines

8. **Settings**
   - Exposes `show_settings_menu()`
   - Supports viewing, editing, resetting, and exporting settings

9. **Exit**
   - Performs clean application exit and connection cleanup

10. **View Metrics**
   - Exposes `show_metrics()`
   - Shows connection, transfer, error, and command metrics

11. **Configuration Backup/Restore**
   - Exposes backup/restore actions
   - Supports running-config backup, startup-config backup, backup listing, and restore

12. **Individual Detection Options**
   - Exposes individual system detector functions
   - Supports targeted checks for licenses, hardware, software, features, interfaces, modules, configuration, and system info

13. **Advanced Password Reset**
   - Exposes individual password reset actions
   - Supports enable secret, console, VTY, verification, config register restore, and save

14. **UART Firmware Dump**
   - Captures raw UART byte streams to `firmware_dumps/*.bin`
   - Supports optional expected size, timeout, and idle timeout

15. **Decompress Firmware Dump**
   - Decompresses or extracts captured dumps
   - Supports gzip, bzip2, xz, zip, tar, zlib, and optional binwalk extraction

## Function Coverage

### Directly Accessible via TUI

- UART pin discovery - Option 1
- `connect()` - Options 2 and 3
- `run_password_reset_workflow()` - Options 2 and 4
- `run_system_detection_only()` - Option 5
- `InteractiveConfig.start()` - Option 6
- `show_log_viewer()` - Option 7
- `show_settings_menu()` - Option 8
- `show_metrics()` - Option 10
- Configuration backup and restore actions - Option 11
- Individual detection functions - Option 12
- Advanced password reset functions - Option 13
- Raw UART firmware dump - Option 14
- Firmware dump decompression - Option 15

### Indirectly Accessible via Workflows

- `SystemDetector.detect_all()` covers all detector methods
- `PasswordReset.complete_password_reset()` covers the reset sequence
- `RommonHandler` methods are used by the password reset workflow
- `CommandExecutor` helpers are used by workflows and interactive mode

## Summary

- **Total Menu Options**: 15
- **Directly Accessible Function Groups**: 13
- **Core Workflow Coverage**: Complete
- **Assessment**: All critical and recommended functions are accessible from the menu system.
