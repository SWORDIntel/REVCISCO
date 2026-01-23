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
                ("1", "Connect to Router"),
                ("2", "Password Reset Workflow"),
                ("3", "System Detection/Inventory"),
                ("4", "Interactive Command Mode"),
                ("5", "View Logs"),
                ("6", "Settings"),
                ("7", "Exit"),
                ("8", "View Metrics"),
                ("9", "Configuration Backup/Restore"),
                ("10", "Individual Detection Options"),
                ("11", "Advanced Password Reset")
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
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                default="1"
            )
        else:
            print(f"\nConnection Status: {connection_status}")
            print("\nMain Menu:")
            print("1. Guided Workflow (Step-by-Step)")
            print("2. Connect to Router")
            print("3. Password Reset Workflow")
            print("4. System Detection/Inventory")
            print("5. Interactive Command Mode")
            print("6. View Logs")
            print("7. Settings")
            print("8. Exit")
            print("9. View Metrics")
            print("10. Configuration Backup/Restore")
            print("11. Individual Detection Options")
            print("12. Advanced Password Reset")
            choice = input("\nSelect option [1-12]: ").strip() or "1"
        
        return choice
    
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