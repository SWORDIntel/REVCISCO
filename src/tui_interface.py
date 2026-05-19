"""
Text User Interface (TUI) for interactive terminal-based interface
"""

import time
import json
from typing import Optional, Any, List, Dict
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.align import Align
    from rich.columns import Columns
    from rich.markdown import Markdown
    from rich.rule import Rule
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class TUIInterface:
    """Text User Interface for Cisco Reset Tool"""
    
    def __init__(self, logger: Optional[Any] = None):
        self.logger = logger
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
            if logger:
                logger.warning("Rich library not available, using basic interface")
    
    def show_welcome(self, show_onboarding: bool = True):
        """Show welcome screen with optional onboarding"""
        if self.console:
            self.console.clear()
            welcome_text = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]  [bold white]Cisco 4321 ISR Password Reset Tool[/bold white]                    [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [dim]Version 1.0.0 - Direct TTY Console Connection[/dim]        [bold cyan]║[/bold cyan]
[bold cyan]╚══════════════════════════════════════════════════════════════╝[/bold cyan]

[bold]Features:[/bold]
  • Automatic break sequence with multiple retry methods
  • ROM monitor automation
  • System detection (licenses, hardware, software)
  • Interactive command mode
  • Extensive logging and monitoring
  • Guided step-by-step workflow

[dim]Press Ctrl+C to exit at any time[/dim]
"""
            welcome = Panel(
                welcome_text,
                title="[bold cyan]Welcome[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            )
            self.console.print(Align.center(welcome))
            self.console.print()
            
            # Show onboarding option on first run
            if show_onboarding:
                if self.confirm("[bold cyan]Would you like a guided walkthrough?[/bold cyan]", default=True):
                    self.show_onboarding_guide()
        else:
            print("=" * 80)
            print("Cisco 4321 ISR Password Reset Tool")
            print("Version 1.0.0")
            print("=" * 80)
    
    def show_onboarding_guide(self):
        """Show onboarding/quick start guide"""
        if self.console:
            self.console.clear()
            guide_text = """
[bold cyan]Quick Start Guide[/bold cyan]

This tool will help you reset the password on your Cisco 4321 ISR router.

[bold]Prerequisites:[/bold]
  ✓ Router powered off or ready to power cycle
  ✓ Serial/TTY cable connected to router console port
  ✓ Serial/TTY cable connected to your computer
  ✓ User has permissions to access serial ports (dialout group)

[bold]What This Tool Does:[/bold]
  1. Connects to router via serial console
  2. Sends break sequence during boot
  3. Enters ROM monitor mode
  4. Modifies configuration register
  5. Reboots router
  6. Resets enable secret password
  7. Restores configuration register
  8. Saves configuration

[bold]Recommended Workflow:[/bold]
  • Use "Guided Workflow" option for step-by-step instructions
  • Follow on-screen prompts for physical actions (power cycle, etc.)
  • Tool will handle all technical steps automatically

[bold]Ready to begin?[/bold]
  Select "Guided Workflow" from the main menu for step-by-step instructions.
"""
            guide = Panel(
                guide_text,
                title="[bold cyan]Onboarding Guide[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            )
            self.console.print(guide)
            self.console.print()
            Prompt.ask("[bold cyan]Press Enter to continue to main menu[/bold cyan]", default="")
        else:
            print("\n" + "=" * 80)
            print("Quick Start Guide")
            print("=" * 80)
            print("\nThis tool will help you reset the password on your Cisco 4321 ISR router.")
            print("\nPrerequisites:")
            print("  - Router powered off or ready to power cycle")
            print("  - Serial/TTY cable connected")
            print("  - User in dialout group")
            print("\nUse 'Guided Workflow' option for step-by-step instructions.")
            input("\nPress Enter to continue...")
    
    def show_main_menu(self, connection_status: str = "Not Connected") -> str:
        """Show main menu and get selection"""
        if self.console:
            self.console.clear()
            
            # Status indicator
            status_color = "green" if "Connected" in connection_status else "red"
            status_panel = Panel(
                f"[{status_color}]{connection_status}[/{status_color}]",
                title="[bold]Connection Status[/bold]",
                border_style=status_color
            )
            self.console.print(status_panel)
            self.console.print()
            
            # Menu options
            menu_table = Table.grid(padding=(0, 2))
            menu_table.add_column(style="cyan", justify="right")
            menu_table.add_column(style="white")
            
            menu_items = [
                ("1", "UART Pin Discovery"),
                ("2", "Guided Cisco 4321 ISR Reset"),
                ("3", "Connect to Cisco 4321 ISR"),
                ("4", "Password Reset Workflow"),
                ("5", "System Detection/Inventory"),
                ("6", "Interactive Command Mode"),
                ("7", "View Logs"),
                ("8", "Settings"),
                ("9", "Exit"),
                ("10", "View Metrics"),
                ("11", "Configuration Backup/Restore"),
                ("12", "Individual Detection Options"),
                ("13", "Advanced Password Reset"),
                ("14", "UART Firmware Dump"),
                ("15", "Decompress Firmware Dump")
            ]
            
            for num, desc in menu_items:
                menu_table.add_row(f"[bold]{num}[/bold]", desc)
            
            menu_panel = Panel(
                menu_table,
                title="[bold blue]Main Menu[/bold blue]",
                border_style="blue",
                padding=(1, 2)
            )
            self.console.print(menu_panel)
            self.console.print()
            
            choice = Prompt.ask(
                "[bold cyan]Select option[/bold cyan]",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"],
                default="1"
            )
        else:
            print(f"\nConnection Status: {connection_status}")
            print("\nMain Menu:")
            print("1. UART Pin Discovery")
            print("2. Guided Cisco 4321 ISR Reset")
            print("3. Connect to Cisco 4321 ISR")
            print("4. Password Reset Workflow")
            print("5. System Detection/Inventory")
            print("6. Interactive Command Mode")
            print("7. View Logs")
            print("8. Settings")
            print("9. Exit")
            print("10. View Metrics")
            print("11. Configuration Backup/Restore")
            print("12. Individual Detection Options")
            print("13. Advanced Password Reset")
            print("14. UART Firmware Dump")
            print("15. Decompress Firmware Dump")
            choice = input("\nSelect option [1-15]: ").strip() or "1"
        
        return choice

    def show_uart_pin_discovery_intro(self, ports: list, baudrate: int = 9600,
                                      in_dialout_group: bool = False) -> bool:
        """Show receive-only UART pin discovery safety checklist."""
        port_text = "\n".join(f"  - {port}" for port in ports) if ports else "  - No serial ports detected"
        permission = "OK" if in_dialout_group else "Needs attention"
        content = (
            "Use this before any reset workflow to identify Cisco UART_DEBUG pins safely.\n\n"
            "Supported cable styles:\n"
            "  - 6-pin USB-TTL board: GND, RXD/RX, TXD/TX, VCC, CTS, DTR\n"
            "  - 4/5-pin USB-TTL lead: GND, RX, TX, VCC, optional 3V3/5V\n"
            "  - 3-wire UART lead: GND, RX, TX\n"
            "  - Keyed JST/Dupont harness: verify labels; wire colors are not authoritative\n"
            "  - RJ45/rollover Cisco console cable: use the normal console port, not UART_DEBUG probing\n"
            "  - DB9/RS-232 adapter: do not connect directly to TTL UART_DEBUG pins\n\n"
            "Receive-only discovery rule:\n"
            "  Adapter GND -> one Cisco ground candidate\n"
            "  Adapter RX  -> one Cisco transmit/TX-output candidate\n\n"
            "Everything else must be disconnected/floating:\n"
            "  Adapter TX, VCC/3V3/5V, CTS, DTR, RTS\n"
            "  Every Cisco pin not in the current two-wire test\n\n"
            "Cable-specific cautions:\n"
            "  - RX/TX labels are from the adapter's perspective; adapter RX listens to Cisco TX.\n"
            "  - Never use the adapter power pin while probing router UART headers.\n"
            "  - If the cable exposes 3V3 and 5V, leave both disconnected.\n"
            "  - If your cable is DB9/RS-232 level, use a TTL-level adapter instead.\n\n"
            "General candidate workflow:\n"
            "  1. Identify or choose one likely Cisco GND pin.\n"
            "  2. Keep adapter GND on that ground candidate.\n"
            "  3. Move adapter RX across one Cisco pin at a time.\n"
            "  4. Power cycle and listen after each candidate pair.\n"
            "  5. A pass is readable boot text, such as System Bootstrap, Cisco IOS, ROMMON, or IOS XE.\n\n"
            "If you are testing the earlier suspected mapping:\n"
            "  Brown/tan adapter GND -> Cisco Pin 1\n"
            "  Adapter RX wire       -> Cisco Pin 2\n"
            "  Cisco Pin 3/Pin 4     -> empty\n\n"
            "Do not connect adapter VCC to the Cisco header. Only add adapter TX after RX output is confirmed.\n\n"
            f"Listen baud rate: {baudrate}\n"
            f"Serial permission: {permission}\n"
            f"Detected ports:\n{port_text}"
        )

        if self.console:
            self.console.clear()
            self.show_info_panel("UART Pin Discovery", content)
            self.console.print()
            if not ports:
                self.show_error_dialog(
                    "No Serial Port Detected",
                    "Connect the USB UART adapter and check /dev/ttyUSB*, /dev/ttyACM*, or /dev/ttyS*.",
                    ["Do not connect adapter TX or power pins", "Confirm dialout group access"]
                )
                return False
            return self.confirm("Confirm this is a two-wire receive-only test: adapter GND plus adapter RX only?", default=False)

        print("\nUART Pin Discovery")
        print("-" * 80)
        print(content)
        if not ports:
            return False
        return self.confirm("Confirm this is a two-wire receive-only test: adapter GND plus adapter RX only?", default=False)

    def show_uart_discovery_settings(self, default_log_file: str) -> Optional[Dict[str, Any]]:
        """Collect UART discovery listener settings."""
        cable_types = {
            "1": "6-pin USB-TTL board (GND/RX/TX/VCC/CTS/DTR)",
            "2": "4/5-pin USB-TTL lead (GND/RX/TX/VCC[/3V3/5V])",
            "3": "3-wire UART lead (GND/RX/TX)",
            "4": "Keyed JST/Dupont harness",
            "5": "RJ45/rollover Cisco console cable",
            "6": "DB9/RS-232 adapter",
            "7": "Other/unknown cable"
        }

        if self.console:
            cable_menu = "\n".join(f"{key}. {label}" for key, label in cable_types.items())
            self.show_info_panel("Connected Cable Type", cable_menu)
            cable_choice = Prompt.ask(
                "Connected cable type",
                choices=list(cable_types.keys()),
                default="1",
                show_choices=False
            )
            cable_note = cable_types[cable_choice]
            if cable_choice == "5":
                cable_note += "\nUse this with the normal Cisco console port. Do not use RJ45 rollover wiring for board-level UART_DEBUG pin probing."
            elif cable_choice == "6":
                cable_note += "\nDB9/RS-232 voltage levels are not TTL-safe. Use a TTL-level USB adapter for UART_DEBUG headers."
            self.show_info_panel("Selected Cable", cable_note)
            ground_label = Prompt.ask("Cisco ground candidate label", default="unknown/selected GND candidate")
            rx_label = Prompt.ask("Cisco RX-test candidate label", default="next candidate pin")
            duration = IntPrompt.ask("Listen duration in seconds", default=60)
            output_file = Prompt.ask("Save boot log to", default=default_log_file)
        else:
            print("\nConnected cable type:")
            for key, label in cable_types.items():
                print(f"{key}. {label}")
            cable_choice = input("Cable type [1]: ").strip() or "1"
            if cable_choice not in cable_types:
                cable_choice = "7"
            ground_label = input("Cisco ground candidate label [unknown/selected GND candidate]: ").strip() or "unknown/selected GND candidate"
            rx_label = input("Cisco RX-test candidate label [next candidate pin]: ").strip() or "next candidate pin"
            duration = int(input("Listen duration in seconds [60]: ").strip() or "60")
            output_file = input(f"Save boot log to [{default_log_file}]: ").strip() or default_log_file

        return {
            "cable_type": cable_types[cable_choice],
            "ground_label": ground_label,
            "rx_label": rx_label,
            "duration": float(duration),
            "output_file": output_file
        }

    def show_uart_discovery_result(self, result: Dict[str, Any]) -> None:
        """Show UART discovery listener result."""
        sample = result.get("sample", "")
        if len(sample) > 1200:
            sample = sample[-1200:]
        detected = result.get("detected_boot_text", False)
        content = (
            f"Cable type: {result.get('cable_type', 'unknown')}\n"
            f"Tested GND candidate: {result.get('ground_label', 'unknown')}\n"
            f"Tested RX candidate: {result.get('rx_label', 'unknown')}\n"
            f"Captured: {result.get('bytes_captured', 0):,} bytes\n"
            f"Saved: {result.get('output_file', 'unknown')}\n"
            f"Likely Cisco boot text: {'yes' if detected else 'no'}\n\n"
            "Recent output:\n"
            f"{sample or '<no readable output captured>'}"
        )

        suggestions = []
        if detected:
            suggestions = [
                "Record this GND/RX candidate pair as the likely console output path",
                "Keep adapter power pins disconnected",
                "Only add adapter TX later if you need interactive input"
            ]
        else:
            suggestions = [
                "Power cycle the router while listening",
                "Move adapter RX to the next candidate Cisco pin",
                "Keep adapter TX and all power/control pins disconnected",
                "If every RX candidate is silent, re-check or change the ground candidate"
            ]

        if self.console:
            self.console.print(Panel(
                content,
                title="[bold cyan]UART Discovery Result[/bold cyan]",
                border_style="green" if detected else "yellow",
                padding=(1, 2)
            ))
            if suggestions:
                self.show_info_panel("Next Steps", "\n".join(f"- {s}" for s in suggestions))
            Prompt.ask("[bold cyan]Press Enter to continue[/bold cyan]", default="")
        else:
            print("\nUART Discovery Result")
            print("-" * 80)
            print(content)
            print("\nNext Steps:")
            for suggestion in suggestions:
                print(f"- {suggestion}")
            input("\nPress Enter to continue...")

    def show_cisco_4321_preflight(self, ports: list, baudrate: int = 9600,
                                  in_dialout_group: bool = False) -> bool:
        """Show Cisco 4321 ISR-specific preflight checks."""
        port_text = "\n".join(f"  - {port}" for port in ports) if ports else "  - No serial ports detected"
        permission = "OK" if in_dialout_group else "Needs attention"
        permission_detail = (
            "Current user is in the dialout group."
            if in_dialout_group
            else "Current user may need dialout group access for /dev/tty* ports."
        )

        content = (
            "Target router: Cisco 4321 ISR / ISR4321\n\n"
            "Expected console settings:\n"
            f"  - Baud rate: {baudrate}\n"
            "  - Data bits: 8\n"
            "  - Parity: none\n"
            "  - Stop bits: 1\n"
            "  - Flow control: none\n\n"
            f"Detected serial ports:\n{port_text}\n\n"
            f"Linux serial permission: {permission}\n"
            f"  - {permission_detail}"
        )

        if self.console:
            self.console.clear()
            self.show_info_panel("Cisco 4321 ISR Preflight", content)
            self.console.print()
            if not ports:
                self.show_error_dialog(
                    "No Serial Port Detected",
                    "No console port was found before starting the Cisco 4321 ISR workflow.",
                    [
                        "Check the console cable",
                        "Try a different USB port",
                        "Verify /dev/ttyUSB*, /dev/ttyACM*, or /dev/ttyS* exists",
                        "Confirm dialout group access"
                    ]
                )
                return False
            return self.confirm("Continue with these Cisco 4321 ISR console settings?", default=True)

        print("\nCisco 4321 ISR Preflight")
        print("-" * 80)
        print(content)
        if not ports:
            return False
        return self.confirm("Continue with these Cisco 4321 ISR console settings?", default=True)

    def show_uart_dump_menu(self, default_output_file: str) -> Optional[Dict[str, Any]]:
        """Collect raw UART firmware/image dump settings."""
        if self.console:
            self.console.clear()
            self.show_info_panel(
                "UART Firmware Dump",
                "Capture raw bytes from the connected Cisco 4321 ISR console/UART directly to a file.\n\n"
                "Use this only when the router or bootloader is already transmitting an image/firmware stream. "
                "The capture stops at the expected byte count, after idle timeout, or at the maximum timeout."
            )
            self.console.print()
            if not self.confirm("Start a raw UART capture session?", default=False):
                return None

            output_file = Prompt.ask("Output file", default=default_output_file)
            size_text = Prompt.ask("Expected bytes (blank for unknown)", default="").strip()
            timeout = IntPrompt.ask("Maximum capture time in seconds", default=3600)
            idle_timeout = IntPrompt.ask("Stop after idle seconds", default=10)
        else:
            print("\nUART Firmware Dump")
            print("-" * 80)
            print("Capture raw bytes from the connected UART to a file.")
            if not self.confirm("Start a raw UART capture session?", default=False):
                return None
            output_file = input(f"Output file [{default_output_file}]: ").strip() or default_output_file
            size_text = input("Expected bytes (blank for unknown): ").strip()
            timeout = int(input("Maximum capture time in seconds [3600]: ").strip() or "3600")
            idle_timeout = int(input("Stop after idle seconds [10]: ").strip() or "10")

        expected_size = None
        if size_text:
            try:
                expected_size = int(size_text.replace("_", "").replace(",", ""))
            except ValueError:
                self.show_error_dialog("Invalid Size", "Expected bytes must be a whole number")
                return None

        return {
            "output_file": output_file,
            "expected_size": expected_size,
            "timeout": float(timeout),
            "idle_timeout": float(idle_timeout)
        }

    def show_uart_dump_result(self, result: Dict[str, Any]) -> None:
        """Show raw UART dump result."""
        bytes_written = result.get("bytes_written", 0)
        duration = result.get("duration", 0)
        reason = result.get("reason", "unknown")
        output_file = result.get("output_file", "unknown")
        expected_size = result.get("expected_size")
        expected_text = f"\nExpected: {expected_size:,} bytes" if expected_size is not None else ""
        content = (
            f"File: {output_file}\n"
            f"Captured: {bytes_written:,} bytes{expected_text}\n"
            f"Duration: {duration:.1f}s\n"
            f"Stopped by: {reason}"
        )
        if self.console:
            self.console.print(Panel(
                content,
                title="[bold green]UART Dump Complete[/bold green]",
                border_style="green",
                padding=(1, 2)
            ))
            Prompt.ask("[bold cyan]Press Enter to continue[/bold cyan]", default="")
        else:
            print("\nUART Dump Complete")
            print("-" * 80)
            print(content)
            input("\nPress Enter to continue...")

    def show_decompression_menu(self, default_dir: str) -> Optional[Dict[str, Any]]:
        """Collect decompression settings for an existing firmware dump."""
        formats = ["auto", "gzip", "bzip2", "xz", "zip", "tar", "zlib", "binwalk"]

        if self.console:
            self.console.clear()
            self.show_info_panel(
                "Decompress Firmware Dump",
                "Decompress or extract a captured UART dump. Auto-detect handles gzip, bzip2, xz, zip, tar, "
                "and common zlib/deflate streams. Choose binwalk for broader firmware carving/extraction."
            )
            self.console.print()
            default_input = str(Path(default_dir) / "uart_dump.bin")
            input_file = Prompt.ask("Input dump file", default=default_input)
            output_path = Prompt.ask("Output path (blank for automatic)", default="").strip() or None
            format_hint = Prompt.ask("Format", choices=formats, default="auto")
        else:
            print("\nDecompress Firmware Dump")
            print("-" * 80)
            input_file = input(f"Input dump file [{Path(default_dir) / 'uart_dump.bin'}]: ").strip()
            if not input_file:
                input_file = str(Path(default_dir) / "uart_dump.bin")
            output_path = input("Output path (blank for automatic): ").strip() or None
            format_hint = input("Format [auto/gzip/bzip2/xz/zip/tar/zlib/binwalk] [auto]: ").strip() or "auto"
            if format_hint not in formats:
                self.show_error_dialog("Invalid Format", f"Unsupported format: {format_hint}")
                return None

        return {
            "input_file": input_file,
            "output_path": output_path,
            "format_hint": format_hint
        }

    def show_decompression_result(self, result: Dict[str, Any]) -> None:
        """Show decompression result."""
        content = (
            f"Input: {result.get('input_file', 'unknown')}\n"
            f"Output: {result.get('output_path', 'unknown')}\n"
            f"Format: {result.get('format', 'unknown')}"
        )

        if self.console:
            self.console.print(Panel(
                content,
                title="[bold green]Decompression Complete[/bold green]",
                border_style="green",
                padding=(1, 2)
            ))
            Prompt.ask("[bold cyan]Press Enter to continue[/bold cyan]", default="")
        else:
            print("\nDecompression Complete")
            print("-" * 80)
            print(content)
            input("\nPress Enter to continue...")

    def show_recovery_resume_notice(self, state: Dict[str, Any]) -> None:
        """Warn about an incomplete previous recovery workflow."""
        phase = state.get("phase", "unknown")
        next_step = state.get("next_step", "Review router state before continuing.")
        timestamp = state.get("timestamp", "unknown")
        details = state.get("details", {})
        detail_text = ""
        if details:
            detail_text = "\n\nDetails:\n" + "\n".join(f"  - {key}: {value}" for key, value in details.items())

        content = (
            f"Previous recovery phase: {phase}\n"
            f"Recorded at: {timestamp}\n\n"
            f"Recommended next step:\n  {next_step}"
            f"{detail_text}"
        )

        if self.console:
            self.console.clear()
            self.show_error_dialog(
                "Incomplete Recovery Detected",
                content,
                [
                    "Connect to the Cisco 4321 ISR before continuing",
                    "If config-register was set to 0x2142, restore 0x2102 before finishing",
                    "Use Advanced Password Reset > Restore Config Register if IOS is available"
                ]
            )
            Prompt.ask("[bold cyan]Press Enter to continue[/bold cyan]", default="")
        else:
            print("\nIncomplete Recovery Detected")
            print("-" * 80)
            print(content)
            input("\nPress Enter to continue...")

    def show_router_identity(self, identity: Dict[str, Any]) -> None:
        """Show best-effort Cisco 4321 ISR identity check results."""
        status = identity.get("status", "Unknown")
        model = identity.get("model", "Unknown")
        serial = identity.get("serial", "Unknown")
        ios_version = identity.get("ios_version", "Unknown")
        is_4321 = identity.get("is_4321", False)
        border = "green" if is_4321 else "yellow"
        content = (
            f"Status: {status}\n\n"
            f"Model/PID: {model}\n"
            f"Serial: {serial}\n"
            f"IOS XE/IOS: {ios_version}"
        )

        if self.console:
            self.console.print()
            self.console.print(Panel(
                content,
                title="[bold cyan]Cisco 4321 ISR Identity Check[/bold cyan]",
                border_style=border,
                padding=(1, 2)
            ))
            self.console.print()
        else:
            print("\nCisco 4321 ISR Identity Check")
            print("-" * 80)
            print(content)

    def show_break_failure_menu(self) -> str:
        """Offer recovery choices when automated break sequence fails."""
        if self.console:
            self.show_error_dialog(
                "ROMmon Break Not Detected",
                "The tool did not detect a Cisco 4321 ISR rommon prompt after automated break attempts.",
                [
                    "Break must land early in boot",
                    "Power cycle and retry if IOS has already started",
                    "Manual ROMmon commands can still be used"
                ]
            )
            self.console.print()
            choice = Prompt.ask(
                "[bold cyan]Next action[/bold cyan]",
                choices=["retry", "manual", "abort"],
                default="retry"
            )
            return choice

        print("\nROMmon Break Not Detected")
        print("1. Retry break sequence")
        print("2. Show manual ROMmon assistant")
        print("3. Abort workflow")
        choice = input("Select option [1-3]: ").strip() or "1"
        return {"1": "retry", "2": "manual", "3": "abort"}.get(choice, "abort")

    def show_rommon_manual_assistant(self) -> None:
        """Show manual Cisco 4321 ISR ROMmon recovery commands."""
        content = (
            "Use this when automated break timing fails.\n\n"
            "1. Power cycle the Cisco 4321 ISR.\n"
            "2. Send your terminal's break signal during early boot.\n"
            "3. At the rommon prompt, run:\n\n"
            "   rommon 1 > confreg 0x2142\n"
            "   rommon 2 > reset\n\n"
            "After IOS boots without startup config, return here and continue the workflow.\n"
            "Before finishing, restore normal boot with:\n\n"
            "   Router(config)# config-register 0x2102\n"
            "   Router# write memory"
        )

        if self.console:
            self.console.print(Panel(
                content,
                title="[bold yellow]Manual Cisco 4321 ISR ROMmon Assistant[/bold yellow]",
                border_style="yellow",
                padding=(1, 2)
            ))
            Prompt.ask("[bold cyan]Press Enter after trying manual ROMmon entry[/bold cyan]", default="")
        else:
            print("\nManual Cisco 4321 ISR ROMmon Assistant")
            print("-" * 80)
            print(content)
            input("\nPress Enter after trying manual ROMmon entry...")
    
    def show_port_selection(self, ports: list) -> Optional[str]:
        """Show port selection menu"""
        if not ports:
            if self.console:
                error_panel = Panel(
                    "[red]No TTY ports found[/red]\n\n"
                    "[dim]Please check:[/dim]\n"
                    "  • Cable connection\n"
                    "  • Port permissions (user in dialout group)\n"
                    "  • Port name: /dev/ttyS*, /dev/ttyUSB*, /dev/ttyACM*",
                    title="[bold red]Error[/bold red]",
                    border_style="red"
                )
                self.console.print(error_panel)
            else:
                print("No TTY ports found")
            return None
        
        if self.console:
            self.console.print()
            table = Table(
                title="[bold cyan]Available TTY Ports[/bold cyan]",
                show_header=True,
                header_style="bold magenta",
                border_style="cyan"
            )
            table.add_column("#", style="cyan", justify="right", width=4)
            table.add_column("Port Path", style="green", width=30)
            table.add_column("Status", style="yellow", width=15)
            
            for i, port in enumerate(ports, 1):
                # Check if port exists
                exists = "✓ Available" if Path(port).exists() else "✗ Not Found"
                table.add_row(str(i), port, exists)
            
            self.console.print(table)
            self.console.print()
            choice = Prompt.ask(
                "[bold cyan]Select port number[/bold cyan]",
                choices=[str(i) for i in range(1, len(ports) + 1)],
                default="1"
            )
            selected = ports[int(choice) - 1]
            self.console.print(f"[green]Selected: {selected}[/green]")
            return selected
        else:
            print("\nAvailable Ports:")
            for i, port in enumerate(ports, 1):
                print(f"{i}. {port}")
            choice = input(f"\nSelect port [1-{len(ports)}]: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(ports):
                return ports[int(choice) - 1]
            return None
    
    def show_progress(self, message: str, spinner: bool = True):
        """Show progress indicator (context manager)"""
        if self.console and spinner:
            return self.console.status(f"[bold green]{message}...", spinner="dots")
        else:
            class SimpleProgress:
                def __enter__(self):
                    print(f"{message}...", end="", flush=True)
                    return self
                def __exit__(self, *args):
                    print(" Done")
            return SimpleProgress()
    
    def show_progress_bar(self, total: int, description: str = "Processing"):
        """Show progress bar"""
        if self.console:
            return Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=self.console
            )
        return None
    
    def show_status(self, status: str, level: str = "info"):
        """Show status message"""
        if self.console:
            if level == "error":
                self.console.print(f"[red]{status}[/red]")
            elif level == "warning":
                self.console.print(f"[yellow]{status}[/yellow]")
            elif level == "success":
                self.console.print(f"[green]{status}[/green]")
            else:
                self.console.print(status)
        else:
            print(status)
    
    def show_detection_results(self, results: dict):
        """Show system detection results in organized panels"""
        if self.console:
            self.console.clear()
            self.console.print(Rule("[bold cyan]System Detection Results[/bold cyan]"))
            self.console.print()
            
            # Create columns layout
            panels = []
            
            # Licenses
            licenses = results.get('licenses', {})
            if licenses.get('parsed', {}).get('udi'):
                udi = licenses['parsed']['udi']
                license_text = f"[bold]UDI:[/bold]\n"
                license_text += f"  PID: [cyan]{udi.get('pid', 'N/A')}[/cyan]\n"
                license_text += f"  SN:  [cyan]{udi.get('sn', 'N/A')}[/cyan]\n"
                if licenses.get('parsed', {}).get('active_licenses'):
                    license_text += f"\n[bold]Active Licenses:[/bold] {len(licenses['parsed']['active_licenses'])}"
                panels.append(Panel(license_text, title="[bold cyan]Licenses[/bold cyan]", border_style="cyan"))
            
            # Hardware
            hardware = results.get('hardware', {})
            if hardware.get('parsed', {}).get('chassis'):
                chassis = hardware['parsed']['chassis']
                hw_text = f"[bold]Chassis:[/bold] [green]{chassis.get('name', 'N/A')}[/green]\n"
                hw_text += f"  PID: [cyan]{chassis.get('pid', 'N/A')}[/cyan]\n"
                hw_text += f"  SN:  [cyan]{chassis.get('sn', 'N/A')}[/cyan]"
                if hardware.get('parsed', {}).get('modules'):
                    hw_text += f"\n\n[bold]Modules:[/bold] {len(hardware['parsed']['modules'])}"
                panels.append(Panel(hw_text, title="[bold green]Hardware[/bold green]", border_style="green"))
            
            # Software
            software = results.get('software', {})
            if software.get('parsed', {}).get('ios_version'):
                sw_text = f"[bold]IOS Version:[/bold] [blue]{software['parsed']['ios_version']}[/blue]"
                if software.get('parsed', {}).get('image_file'):
                    sw_text += f"\n[bold]Image:[/bold] [dim]{software['parsed']['image_file']}[/dim]"
                if software.get('parsed', {}).get('packages'):
                    sw_text += f"\n\n[bold]Packages:[/bold] {len(software['parsed']['packages'])}"
                panels.append(Panel(sw_text, title="[bold blue]Software[/bold blue]", border_style="blue"))
            
            # Interfaces
            interfaces = results.get('interfaces', {})
            if interfaces.get('parsed', {}).get('summary'):
                summary = interfaces['parsed']['summary']
                int_text = f"[bold]Physical:[/bold] {summary.get('total_physical', 0)}\n"
                int_text += f"[bold]Logical:[/bold] {summary.get('total_logical', 0)}"
                panels.append(Panel(int_text, title="[bold yellow]Interfaces[/bold yellow]", border_style="yellow"))
            
            if panels:
                self.console.print(Columns(panels, equal=True, expand=True))
                self.console.print()
            
            # Export option
            if self.confirm("Export results to file?", default=False):
                export_format = Prompt.ask(
                    "Export format",
                    choices=["json", "yaml", "txt"],
                    default="json"
                )
                return export_format
            
        else:
            print("\n" + "=" * 80)
            print("System Detection Results")
            print("=" * 80)
            licenses = results.get('licenses', {})
            if licenses.get('parsed', {}).get('udi'):
                udi = licenses['parsed']['udi']
                print(f"UDI: PID={udi.get('pid', 'N/A')}, SN={udi.get('sn', 'N/A')}")
            print("=" * 80)
        
        return None
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """Show confirmation prompt"""
        if self.console:
            return Confirm.ask(message, default=default)
        else:
            response = input(f"{message} [y/N]: ").strip().lower()
            return response in ['y', 'yes']
    
    def get_password(self, prompt: str = "Enter password: ") -> str:
        """Get password input"""
        import getpass
        if self.console:
            self.console.print(f"[dim]{prompt}[/dim]", end="")
        return getpass.getpass("")
    
    def show_workflow_progress(self, step: str, current: int, total: int, status: str = ""):
        """Show workflow progress"""
        if self.console:
            progress_text = f"[bold cyan]Step {current}/{total}:[/bold cyan] {step}"
            if status:
                progress_text += f"\n[dim]{status}[/dim]"
            
            # Progress bar
            progress_bar = ""
            filled = int((current / total) * 20)
            progress_bar = "█" * filled + "░" * (20 - filled)
            progress_text += f"\n[{progress_bar}] {int((current/total)*100)}%"
            
            panel = Panel(
                progress_text,
                title="[bold]Workflow Progress[/bold]",
                border_style="cyan"
            )
            self.console.print(panel)
        else:
            print(f"\nStep {current}/{total}: {step}")
            if status:
                print(f"  {status}")
    
    def show_error_dialog(self, title: str, message: str, suggestions: List[str] = None):
        """Show error dialog with suggestions"""
        if self.console:
            error_text = f"[red]{message}[/red]"
            if suggestions:
                error_text += "\n\n[bold]Suggestions:[/bold]"
                for i, suggestion in enumerate(suggestions, 1):
                    error_text += f"\n  {i}. {suggestion}"
            
            panel = Panel(
                error_text,
                title=f"[bold red]{title}[/bold red]",
                border_style="red",
                padding=(1, 2)
            )
            self.console.print(panel)
        else:
            print(f"\nERROR: {title}")
            print(message)
            if suggestions:
                print("\nSuggestions:")
                for suggestion in suggestions:
                    print(f"  - {suggestion}")
    
    def show_success_message(self, message: str):
        """Show success message"""
        if self.console:
            panel = Panel(
                f"[green]{message}[/green]",
                title="[bold green]Success[/bold green]",
                border_style="green"
            )
            self.console.print(panel)
        else:
            print(f"\nSUCCESS: {message}")
    
    def show_info_panel(self, title: str, content: str):
        """Show information panel"""
        if self.console:
            panel = Panel(
                content,
                title=f"[bold cyan]{title}[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            )
            self.console.print(panel)
        else:
            print(f"\n{title}")
            print("-" * len(title))
            print(content)
    
    def show_log_viewer(self, log_dir: str, log_files: List[str] = None) -> Optional[str]:
        """Show log viewer with file selection"""
        from pathlib import Path
        log_path = Path(log_dir)
        
        if not log_path.exists():
            self.show_error_dialog("Log Directory Not Found", f"Log directory does not exist: {log_dir}")
            return None
        
        # Find log files
        if log_files is None:
            log_files = sorted(log_path.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
            log_files = [str(f) for f in log_files[:20]]  # Last 20 files
        
        if not log_files:
            self.show_error_dialog("No Log Files", "No log files found in log directory")
            return None
        
        if self.console:
            self.console.clear()
            table = Table(
                title="[bold cyan]Available Log Files[/bold cyan]",
                show_header=True,
                header_style="bold magenta",
                border_style="cyan"
            )
            table.add_column("#", style="cyan", justify="right", width=4)
            table.add_column("File Name", style="green", width=40)
            table.add_column("Size", style="yellow", width=12)
            
            for i, log_file in enumerate(log_files, 1):
                file_path = Path(log_file)
                size = file_path.stat().st_size if file_path.exists() else 0
                size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024*1024):.1f} MB"
                table.add_row(str(i), file_path.name, size_str)
            
            self.console.print(table)
            self.console.print()
            
            choice = Prompt.ask(
                "[bold cyan]Select log file to view[/bold cyan]",
                choices=[str(i) for i in range(1, len(log_files) + 1)],
                default="1"
            )
            selected = log_files[int(choice) - 1]
            
            # Show log content
            return self._view_log_file(selected)
        else:
            print("\nAvailable Log Files:")
            for i, log_file in enumerate(log_files, 1):
                print(f"{i}. {Path(log_file).name}")
            choice = input(f"\nSelect file [1-{len(log_files)}]: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(log_files):
                return self._view_log_file(log_files[int(choice) - 1])
        
        return None
    
    def _view_log_file(self, log_file: str, lines: int = 100) -> str:
        """View log file content"""
        from pathlib import Path
        file_path = Path(log_file)
        
        if not file_path.exists():
            self.show_error_dialog("File Not Found", f"Log file does not exist: {log_file}")
            return log_file
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                # Show last N lines
                display_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            if self.console:
                self.console.clear()
                content = ''.join(display_lines)
                panel = Panel(
                    f"[dim]{content}[/dim]",
                    title=f"[bold cyan]Log File: {file_path.name}[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 1)
                )
                self.console.print(panel)
                self.console.print()
                
                if len(all_lines) > lines:
                    self.console.print(f"[dim]Showing last {lines} of {len(all_lines)} lines[/dim]")
                
                Prompt.ask("[bold cyan]Press Enter to continue[/bold cyan]", default="")
            else:
                print(f"\n{'='*80}")
                print(f"Log File: {file_path.name}")
                print(f"{'='*80}\n")
                print(''.join(display_lines))
                if len(all_lines) > lines:
                    print(f"\n[Showing last {lines} of {len(all_lines)} lines]")
                input("\nPress Enter to continue...")
            
            return log_file
        except Exception as e:
            self.show_error_dialog("Error Reading Log", f"Failed to read log file: {e}")
            return log_file
    
    def show_settings_menu(self, settings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Show settings menu and return updated settings"""
        if self.console:
            self.console.clear()
            self.console.print(Rule("[bold cyan]Settings[/bold cyan]"))
            self.console.print()
            
            # Display current settings
            table = Table(
                title="[bold cyan]Current Settings[/bold cyan]",
                show_header=True,
                header_style="bold magenta",
                border_style="cyan"
            )
            table.add_column("Setting", style="cyan", width=25)
            table.add_column("Value", style="green", width=30)
            table.add_column("Description", style="dim", width=40)
            
            setting_descriptions = {
                "last_port": "Last used serial port",
                "default_baudrate": "Default baud rate",
                "log_level": "Logging level (DEBUG/INFO/WARNING/ERROR)",
                "auto_reconnect": "Automatically reconnect on disconnect",
                "command_timeout": "Command execution timeout (seconds)",
                "break_retry_count": "Number of break sequence retries",
                "enable_metrics": "Enable metrics collection",
                "auto_backup": "Automatically backup configurations",
                "show_welcome": "Show welcome screen on startup",
                "theme": "UI theme (default/dark/light)"
            }
            
            for key, value in settings.items():
                desc = setting_descriptions.get(key, "")
                display_value = str(value)
                if isinstance(value, bool):
                    display_value = "Yes" if value else "No"
                table.add_row(key, display_value, desc)
            
            self.console.print(table)
            self.console.print()
            
            # Options
            options_table = Table.grid(padding=(0, 2))
            options_table.add_column(style="cyan", justify="right")
            options_table.add_column(style="white")
            
            options_table.add_row("1", "Change setting")
            options_table.add_row("2", "Reset to defaults")
            options_table.add_row("3", "Export settings")
            options_table.add_row("4", "Back to main menu")
            
            self.console.print(options_table)
            self.console.print()
            
            choice = Prompt.ask(
                "[bold cyan]Select option[/bold cyan]",
                choices=["1", "2", "3", "4"],
                default="4"
            )
            
            if choice == "1":
                return self._edit_setting(settings)
            elif choice == "2":
                if self.confirm("Reset all settings to defaults?", default=False):
                    return {}
            elif choice == "3":
                self._export_settings(settings)
            
            return None
        else:
            print("\nSettings:")
            for key, value in settings.items():
                print(f"  {key}: {value}")
            return None
    
    def _edit_setting(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Edit a setting"""
        setting_names = list(settings.keys())
        
        if self.console:
            table = Table(
                title="[bold cyan]Select Setting to Edit[/bold cyan]",
                show_header=True,
                header_style="bold magenta",
                border_style="cyan"
            )
            table.add_column("#", style="cyan", justify="right", width=4)
            table.add_column("Setting", style="green", width=30)
            
            for i, key in enumerate(setting_names, 1):
                table.add_row(str(i), key)
            
            self.console.print(table)
            self.console.print()
            
            choice = Prompt.ask(
                "[bold cyan]Select setting[/bold cyan]",
                choices=[str(i) for i in range(1, len(setting_names) + 1)],
                default="1"
            )
            selected_key = setting_names[int(choice) - 1]
            current_value = settings[selected_key]
            
            # Get new value based on type
            if isinstance(current_value, bool):
                new_value = self.confirm(f"Enable {selected_key}?", default=current_value)
            elif isinstance(current_value, int):
                new_value = IntPrompt.ask(f"Enter new value for {selected_key}", default=current_value)
            elif isinstance(current_value, float):
                new_value = float(Prompt.ask(f"Enter new value for {selected_key}", default=str(current_value)))
            else:
                new_value = Prompt.ask(f"Enter new value for {selected_key}", default=str(current_value))
            
            return {selected_key: new_value}
        
        return {}
    
    def _export_settings(self, settings: Dict[str, Any]):
        """Export settings to file"""
        from pathlib import Path
        from datetime import datetime
        
        export_file = f"settings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            import json
            with open(export_file, 'w') as f:
                json.dump(settings, f, indent=2)
            self.show_success_message(f"Settings exported to {export_file}")
        except Exception as e:
            self.show_error_dialog("Export Failed", f"Failed to export settings: {e}")
    
    def show_metrics(self, metrics: Dict[str, Any]):
        """Show metrics in a formatted panel"""
        if self.console:
            self.console.clear()
            self.console.print(Rule("[bold cyan]System Metrics[/bold cyan]"))
            self.console.print()
            
            panels = []
            
            # Connection metrics
            if 'connection' in metrics:
                conn = metrics['connection']
                conn_text = f"[bold]Uptime:[/bold] {conn.get('uptime', 0):.1f}s"
                if conn.get('start_time'):
                    from datetime import datetime
                    start = datetime.fromtimestamp(conn['start_time'])
                    conn_text += f"\n[bold]Started:[/bold] {start.strftime('%Y-%m-%d %H:%M:%S')}"
                panels.append(Panel(conn_text, title="[bold cyan]Connection[/bold cyan]", border_style="cyan"))
            
            # Bytes metrics
            if 'bytes' in metrics:
                bytes_data = metrics['bytes']
                bytes_text = f"[bold]Sent:[/bold] {bytes_data.get('sent', 0):,} bytes\n"
                bytes_text += f"[bold]Received:[/bold] {bytes_data.get('received', 0):,} bytes\n"
                bytes_text += f"[bold]Total:[/bold] {bytes_data.get('total', 0):,} bytes"
                panels.append(Panel(bytes_text, title="[bold green]Data Transfer[/bold green]", border_style="green"))
            
            # Error metrics
            if 'errors' in metrics:
                errors = metrics['errors']
                error_text = f"[bold]Total Errors:[/bold] {sum(errors.values())}\n"
                for err_type, count in errors.items():
                    error_text += f"  {err_type}: {count}\n"
                panels.append(Panel(error_text, title="[bold red]Errors[/bold red]", border_style="red"))
            
            # Command execution
            if 'command_execution' in metrics:
                cmd = metrics['command_execution']
                cmd_text = f"[bold]Commands:[/bold] {cmd.get('count', 0)}\n"
                cmd_text += f"[bold]Avg Time:[/bold] {cmd.get('average', 0):.3f}s"
                panels.append(Panel(cmd_text, title="[bold yellow]Commands[/bold yellow]", border_style="yellow"))
            
            if panels:
                self.console.print(Columns(panels, equal=True, expand=True))
                self.console.print()
            
            Prompt.ask("[bold cyan]Press Enter to continue[/bold cyan]", default="")
        else:
            print("\nMetrics:")
            print(json.dumps(metrics, indent=2))
            input("\nPress Enter to continue...")
    
    def show_backup_menu(self, backup_dir: str, command_executor: Optional[Any] = None) -> Optional[str]:
        """Show backup/restore menu"""
        from pathlib import Path
        backup_path = Path(backup_dir)
        
        if self.console:
            self.console.clear()
            self.console.print(Rule("[bold cyan]Configuration Backup & Restore[/bold cyan]"))
            self.console.print()
            
            # Menu options
            options_table = Table.grid(padding=(0, 2))
            options_table.add_column(style="cyan", justify="right")
            options_table.add_column(style="white")
            
            options_table.add_row("1", "Backup Running Configuration")
            options_table.add_row("2", "Backup Startup Configuration")
            options_table.add_row("3", "List Available Backups")
            options_table.add_row("4", "Restore Configuration")
            options_table.add_row("5", "Back to Main Menu")
            
            self.console.print(options_table)
            self.console.print()
            
            choice = Prompt.ask(
                "[bold cyan]Select option[/bold cyan]",
                choices=["1", "2", "3", "4", "5"],
                default="5"
            )
            
            if choice == "1":
                # Backup running config
                if not command_executor:
                    self.show_error_dialog("Not Connected", "Please connect to router first")
                    return None
                
                with self.show_progress("Backing up running configuration"):
                    success, output = command_executor.execute("show running-config", timeout=30.0)
                    if success:
                        from config_backup import ConfigBackup
                        backup = ConfigBackup(backup_dir=backup_dir, logger=self.logger)
                        backup_file = backup.backup_running_config(output)
                        if backup_file:
                            self.show_success_message(f"Configuration backed up to {backup_file}")
                            return backup_file
                        else:
                            self.show_error_dialog("Backup Failed", "Failed to create backup file")
                    else:
                        self.show_error_dialog("Backup Failed", f"Failed to get running config: {output[-200:]}")
                return None
                
            elif choice == "2":
                # Backup startup config
                if not command_executor:
                    self.show_error_dialog("Not Connected", "Please connect to router first")
                    return None
                
                with self.show_progress("Backing up startup configuration"):
                    success, output = command_executor.execute("show startup-config", timeout=30.0)
                    if success:
                        from config_backup import ConfigBackup
                        backup = ConfigBackup(backup_dir=backup_dir, logger=self.logger)
                        backup_file = backup.backup_startup_config(output)
                        if backup_file:
                            self.show_success_message(f"Startup configuration backed up to {backup_file}")
                            return backup_file
                        else:
                            self.show_error_dialog("Backup Failed", "Failed to create backup file")
                    else:
                        self.show_error_dialog("Backup Failed", f"Failed to get startup config: {output[-200:]}")
                return None
                
            elif choice == "3":
                # List backups
                return self._list_backups(backup_dir)
                
            elif choice == "4":
                # Restore config
                return self._restore_config_menu(backup_dir, command_executor)
            
            return None
        else:
            print("\nConfiguration Backup & Restore")
            print("1. Backup Running Configuration")
            print("2. Backup Startup Configuration")
            print("3. List Available Backups")
            print("4. Restore Configuration")
            print("5. Back to Main Menu")
            choice = input("\nSelect option [1-5]: ").strip() or "5"
            # Similar logic for non-rich mode
            return None
    
    def _list_backups(self, backup_dir: str) -> Optional[str]:
        """List available backup files"""
        from pathlib import Path
        backup_path = Path(backup_dir)
        
        if not backup_path.exists():
            self.show_error_dialog("Backup Directory Not Found", f"Backup directory does not exist: {backup_dir}")
            return None
        
        # Find backup files
        backup_files = sorted(backup_path.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not backup_files:
            self.show_error_dialog("No Backups Found", "No backup files found in backup directory")
            return None
        
        if self.console:
            self.console.clear()
            table = Table(
                title="[bold cyan]Available Backups[/bold cyan]",
                show_header=True,
                header_style="bold magenta",
                border_style="cyan"
            )
            table.add_column("#", style="cyan", justify="right", width=4)
            table.add_column("File Name", style="green", width=40)
            table.add_column("Size", style="yellow", width=12)
            table.add_column("Modified", style="dim", width=20)
            
            for i, backup_file in enumerate(backup_files[:20], 1):  # Last 20 backups
                size = backup_file.stat().st_size
                size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024*1024):.1f} MB"
                from datetime import datetime
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
                table.add_row(str(i), backup_file.name, size_str, mtime_str)
            
            self.console.print(table)
            self.console.print()
            Prompt.ask("[bold cyan]Press Enter to continue[/bold cyan]", default="")
        
        return None
    
    def _restore_config_menu(self, backup_dir: str, command_executor: Optional[Any] = None) -> Optional[str]:
        """Show restore configuration menu"""
        from pathlib import Path
        backup_path = Path(backup_dir)
        
        if not command_executor:
            self.show_error_dialog("Not Connected", "Please connect to router first")
            return None
        
        # Find backup files
        backup_files = sorted(backup_path.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not backup_files:
            self.show_error_dialog("No Backups Found", "No backup files found")
            return None
        
        if self.console:
            self.console.clear()
            table = Table(
                title="[bold cyan]Select Backup to Restore[/bold cyan]",
                show_header=True,
                header_style="bold magenta",
                border_style="cyan"
            )
            table.add_column("#", style="cyan", justify="right", width=4)
            table.add_column("File Name", style="green", width=40)
            table.add_column("Modified", style="dim", width=20)
            
            for i, backup_file in enumerate(backup_files[:20], 1):
                from datetime import datetime
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S")
                table.add_row(str(i), backup_file.name, mtime_str)
            
            self.console.print(table)
            self.console.print()
            
            if not self.confirm("WARNING: Restoring configuration will overwrite current config. Continue?", default=False):
                return None
            
            choice = Prompt.ask(
                "[bold cyan]Select backup file[/bold cyan]",
                choices=[str(i) for i in range(1, min(len(backup_files), 20) + 1)],
                default="1"
            )
            selected_file = backup_files[int(choice) - 1]
            
            # Restore configuration
            from config_backup import ConfigBackup
            backup = ConfigBackup(backup_dir=backup_dir, logger=self.logger)
            config_content = backup.restore_config(str(selected_file))
            
            if config_content:
                if self.confirm("Apply this configuration to the router?", default=False):
                    with self.show_progress("Restoring configuration"):
                        # Enter config mode and apply
                        if command_executor.enter_config_mode():
                            # Split config into lines and apply
                            lines = config_content.split('\n')
                            for line in lines:
                                line = line.strip()
                                if line and not line.startswith('!'):
                                    command_executor.execute(line, timeout=5.0)
                            command_executor.exit_config_mode()
                            command_executor.save_config()
                            self.show_success_message(f"Configuration restored from {selected_file.name}")
                            return str(selected_file)
                        else:
                            self.show_error_dialog("Restore Failed", "Failed to enter configuration mode")
            else:
                self.show_error_dialog("Restore Failed", "Failed to read backup file")
        
        return None
    
    def show_individual_detection_menu(self, system_detector: Any) -> Optional[str]:
        """Show menu for individual detection functions"""
        if self.console:
            self.console.clear()
            self.console.print(Rule("[bold cyan]Individual System Detection[/bold cyan]"))
            self.console.print()
            
            # Menu options
            options_table = Table.grid(padding=(0, 2))
            options_table.add_column(style="cyan", justify="right")
            options_table.add_column(style="white")
            
            options_table.add_row("1", "Detect Licenses Only")
            options_table.add_row("2", "Detect Hardware Only")
            options_table.add_row("3", "Detect Software Only")
            options_table.add_row("4", "Detect Features Only")
            options_table.add_row("5", "Detect Interfaces Only")
            options_table.add_row("6", "Detect Modules Only")
            options_table.add_row("7", "Detect Configuration Only")
            options_table.add_row("8", "Detect System Info Only")
            options_table.add_row("9", "Run All Detections")
            options_table.add_row("0", "Back to Main Menu")
            
            self.console.print(options_table)
            self.console.print()
            
            choice = Prompt.ask(
                "[bold cyan]Select detection option[/bold cyan]",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
                default="0"
            )
            
            if choice == "1":
                with self.show_progress("Detecting licenses..."):
                    results = system_detector.detect_licenses()
                    self.show_detection_results({"licenses": results})
                    return "licenses"
            elif choice == "2":
                with self.show_progress("Detecting hardware..."):
                    results = system_detector.detect_hardware()
                    self.show_detection_results({"hardware": results})
                    return "hardware"
            elif choice == "3":
                with self.show_progress("Detecting software..."):
                    results = system_detector.detect_software()
                    self.show_detection_results({"software": results})
                    return "software"
            elif choice == "4":
                with self.show_progress("Detecting features..."):
                    results = system_detector.detect_features()
                    self.show_detection_results({"features": results})
                    return "features"
            elif choice == "5":
                with self.show_progress("Detecting interfaces..."):
                    results = system_detector.detect_interfaces()
                    self.show_detection_results({"interfaces": results})
                    return "interfaces"
            elif choice == "6":
                with self.show_progress("Detecting modules..."):
                    results = system_detector.detect_modules()
                    self.show_detection_results({"modules": results})
                    return "modules"
            elif choice == "7":
                with self.show_progress("Detecting configuration..."):
                    results = system_detector.detect_configuration()
                    self.show_detection_results({"configuration": results})
                    return "configuration"
            elif choice == "8":
                with self.show_progress("Detecting system info..."):
                    results = system_detector.detect_system_info()
                    self.show_detection_results({"system_info": results})
                    return "system_info"
            elif choice == "9":
                with self.show_progress("Running all detections..."):
                    results = system_detector.detect_all()
                    self.show_detection_results(results)
                    return "all"
            
            return None
        else:
            print("\nIndividual System Detection")
            print("1. Detect Licenses Only")
            print("2. Detect Hardware Only")
            print("3. Detect Software Only")
            print("4. Detect Features Only")
            print("5. Detect Interfaces Only")
            print("6. Detect Modules Only")
            print("7. Detect Configuration Only")
            print("8. Detect System Info Only")
            print("9. Run All Detections")
            print("0. Back to Main Menu")
            return None
    
    def show_advanced_password_reset_menu(self, password_reset: Any) -> Optional[str]:
        """Show advanced password reset options"""
        if self.console:
            self.console.clear()
            self.console.print(Rule("[bold cyan]Advanced Password Reset Options[/bold cyan]"))
            self.console.print()
            
            self.show_info_panel(
                "Advanced Password Reset",
                "These options allow you to reset specific passwords individually.\n"
                "Useful when you only need to reset one type of password.\n\n"
                "Note: Router must be in privileged mode (no password required)."
            )
            self.console.print()
            
            # Menu options
            options_table = Table.grid(padding=(0, 2))
            options_table.add_column(style="cyan", justify="right")
            options_table.add_column(style="white")
            
            options_table.add_row("1", "Reset Enable Secret Password")
            options_table.add_row("2", "Reset Console Password")
            options_table.add_row("3", "Reset VTY Password")
            options_table.add_row("4", "Verify Password Reset")
            options_table.add_row("5", "Restore Config Register")
            options_table.add_row("6", "Save Configuration")
            options_table.add_row("0", "Back to Main Menu")
            
            self.console.print(options_table)
            self.console.print()
            
            choice = Prompt.ask(
                "[bold cyan]Select password reset option[/bold cyan]",
                choices=["1", "2", "3", "4", "5", "6", "0"],
                default="0"
            )
            
            if choice == "1":
                # Reset enable secret
                password = self.get_password("Enter new enable secret password: ")
                if password:
                    password_confirm = self.get_password("Confirm password: ")
                    if password == password_confirm:
                        with self.show_progress("Resetting enable secret password..."):
                            if password_reset.reset_enable_secret(password):
                                self.show_success_message("Enable secret password reset successfully")
                                return "enable_secret"
                            else:
                                self.show_error_dialog("Reset Failed", "Failed to reset enable secret password")
                    else:
                        self.show_error_dialog("Password Mismatch", "Passwords do not match")
                return None
                
            elif choice == "2":
                # Reset console password
                password = self.get_password("Enter new console password: ")
                if password:
                    password_confirm = self.get_password("Confirm password: ")
                    if password == password_confirm:
                        with self.show_progress("Resetting console password..."):
                            if password_reset.reset_console_password(password):
                                self.show_success_message("Console password reset successfully")
                                return "console"
                            else:
                                self.show_error_dialog("Reset Failed", "Failed to reset console password")
                    else:
                        self.show_error_dialog("Password Mismatch", "Passwords do not match")
                return None
                
            elif choice == "3":
                # Reset VTY password
                password = self.get_password("Enter new VTY password: ")
                if password:
                    password_confirm = self.get_password("Confirm password: ")
                    if password == password_confirm:
                        with self.show_progress("Resetting VTY password..."):
                            if password_reset.reset_vty_password(password):
                                self.show_success_message("VTY password reset successfully")
                                return "vty"
                            else:
                                self.show_error_dialog("Reset Failed", "Failed to reset VTY password")
                    else:
                        self.show_error_dialog("Password Mismatch", "Passwords do not match")
                return None
                
            elif choice == "4":
                # Verify password reset
                with self.show_progress("Verifying password reset..."):
                    if password_reset.verify_password_reset():
                        self.show_success_message("Password reset verified successfully")
                        return "verified"
                    else:
                        self.show_error_dialog("Verification Failed", "Password reset verification failed")
                return None
                
            elif choice == "5":
                # Restore config register
                if self.confirm("Restore configuration register to original value?", default=False):
                    with self.show_progress("Restoring configuration register..."):
                        if password_reset.restore_config_register():
                            self.show_success_message("Configuration register restored successfully")
                            return "config_register"
                        else:
                            self.show_error_dialog("Restore Failed", "Failed to restore configuration register")
                return None
                
            elif choice == "6":
                # Save configuration
                if self.confirm("Save current configuration?", default=False):
                    with self.show_progress("Saving configuration..."):
                        if password_reset.save_configuration():
                            self.show_success_message("Configuration saved successfully")
                            return "saved"
                        else:
                            self.show_error_dialog("Save Failed", "Failed to save configuration")
                return None
            
            return None
        else:
            print("\nAdvanced Password Reset Options")
            print("1. Reset Enable Secret Password")
            print("2. Reset Console Password")
            print("3. Reset VTY Password")
            print("4. Verify Password Reset")
            print("5. Restore Config Register")
            print("6. Save Configuration")
            print("0. Back to Main Menu")
            return None
    
    def show_guided_workflow(self) -> bool:
        """Show guided step-by-step workflow with physical action prompts"""
        if self.console:
            self.console.clear()
            self.console.print(Rule("[bold cyan]Guided Password Reset Workflow[/bold cyan]"))
            self.console.print()
            
            self.show_info_panel(
                "Guided Workflow",
                "This guided workflow will walk you through the entire password reset process.\n"
                "Follow the on-screen instructions and perform the physical actions when prompted.\n\n"
                "The tool will handle all technical steps automatically."
            )
            self.console.print()
            
            if not self.confirm("[bold cyan]Ready to begin?[/bold cyan]", default=True):
                return False
            
            # Step 1: Physical preparation
            self.console.clear()
            step1 = Panel(
                "[bold]Step 1: Physical Preparation[/bold]\n\n"
                "Before we begin, ensure:\n"
                "  ✓ Serial/TTY cable is connected to router console port\n"
                "  ✓ Serial/TTY cable is connected to your computer\n"
                "  ✓ Router is currently powered ON\n"
                "  ✓ You have physical access to power cycle the router\n\n"
                "[dim]We'll power cycle the router in the next step.[/dim]",
                title="[bold cyan]Preparation[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            )
            self.console.print(step1)
            self.console.print()
            
            if not self.confirm("[bold cyan]Are all connections ready?[/bold cyan]", default=True):
                self.show_error_dialog("Setup Incomplete", "Please complete the physical setup and try again")
                return False
            
            # Step 2: Power cycle instruction
            self.console.clear()
            step2 = Panel(
                "[bold]Step 2: Power Cycle Router[/bold]\n\n"
                "We need to power cycle the router to catch the boot sequence.\n\n"
                "[yellow]ACTION REQUIRED:[/yellow]\n"
                "  1. Turn OFF the router (unplug power or use power switch)\n"
                "  2. Wait for the router to fully power down\n"
                "  3. We'll wait 10 seconds, then you'll turn it back ON",
                title="[bold yellow]Physical Action Required[/bold yellow]",
                border_style="yellow",
                padding=(1, 2)
            )
            self.console.print(step2)
            self.console.print()
            
            if not self.confirm("[bold cyan]Have you turned OFF the router?[/bold cyan]", default=False):
                self.show_error_dialog("Action Required", "Please turn off the router first")
                return False
            
            # Countdown timer
            self.console.print()
            self.console.print("[bold yellow]Waiting 10 seconds before power on...[/bold yellow]")
            for i in range(10, 0, -1):
                self.console.print(f"[dim]  {i}...[/dim]", end="\r")
                time.sleep(1)
            self.console.print("[green]  Ready![/green]")
            self.console.print()
            
            # Step 3: Power on instruction
            step3 = Panel(
                "[bold]Step 3: Power On Router[/bold]\n\n"
                "[yellow]ACTION REQUIRED:[/yellow]\n"
                "  Turn ON the router now (plug in power or use power switch)\n\n"
                "[dim]The tool will automatically detect the boot sequence and send the break signal.[/dim]",
                title="[bold yellow]Power On Now[/bold yellow]",
                border_style="yellow",
                padding=(1, 2)
            )
            self.console.print(step3)
            self.console.print()
            
            if not self.confirm("[bold cyan]Have you turned ON the router?[/bold cyan]", default=False):
                self.show_error_dialog("Action Required", "Please turn on the router")
                return False
            
            # Return True to indicate ready for automated workflow
            self.console.print()
            self.show_success_message("Physical setup complete! Ready for automated workflow.")
            time.sleep(2)
            return True
        else:
            print("\n" + "=" * 80)
            print("Guided Password Reset Workflow")
            print("=" * 80)
            print("\nStep 1: Physical Preparation")
            print("Ensure serial cable is connected and router is powered ON")
            input("\nPress Enter when ready...")
            
            print("\nStep 2: Power Cycle")
            print("Turn OFF the router now")
            input("Press Enter when router is OFF...")
            
            print("\nWaiting 10 seconds...")
            for i in range(10, 0, -1):
                print(f"  {i}...", end="\r")
                time.sleep(1)
            print("  Ready!")
            
            print("\nStep 3: Power On")
            print("Turn ON the router now")
            input("Press Enter when router is ON...")
            
            return True
