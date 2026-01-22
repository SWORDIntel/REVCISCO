"""
Text User Interface (TUI) for interactive terminal-based interface
"""

import time
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
    
    def show_welcome(self):
        """Show welcome screen"""
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
        else:
            print("=" * 80)
            print("Cisco 4321 ISR Password Reset Tool")
            print("Version 1.0.0")
            print("=" * 80)
    
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
                ("7", "Exit")
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
                choices=["1", "2", "3", "4", "5", "6", "7"],
                default="1"
            )
        else:
            print(f"\nConnection Status: {connection_status}")
            print("\nMain Menu:")
            print("1. Connect to Router")
            print("2. Password Reset Workflow")
            print("3. System Detection/Inventory")
            print("4. Interactive Command Mode")
            print("5. View Logs")
            print("6. Settings")
            print("7. Exit")
            choice = input("\nSelect option [1-7]: ").strip() or "1"
        
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
