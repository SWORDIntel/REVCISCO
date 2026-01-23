#!/usr/bin/env python3
"""
Single auto-bootstrapping entry point for Cisco 4321 ISR Password Reset Tool
"""

import sys
import os
import time
from pathlib import Path

# Add src directory to path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)

def check_dependencies():
    """Check and install dependencies"""
    missing = []
    
    try:
        import serial
    except ImportError:
        missing.append("pyserial")
    
    try:
        import rich
    except ImportError:
        missing.append("rich")
    
    if missing:
        print(f"\n[!] Missing dependencies: {', '.join(missing)}")
        print("\nInstalling dependencies...")
        
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install"] + missing,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✓ Dependencies installed successfully!")
                print("\nPlease run the tool again.")
            else:
                print(f"✗ Failed to install dependencies:")
                print(result.stderr)
                print("\nPlease install manually:")
                print(f"  {sys.executable} -m pip install {' '.join(missing)}")
        except Exception as e:
            print(f"✗ Error installing dependencies: {e}")
            print("\nPlease install manually:")
            print(f"  {sys.executable} -m pip install {' '.join(missing)}")
        
        sys.exit(0)
    
    print("✓ All dependencies available")

def initialize_directories():
    """Initialize required directories"""
    # Get project root (parent of src directory)
    base_dir = Path(__file__).parent.parent
    dirs = ['logs', 'monitoring', 'backups', 'config']
    for dir_name in dirs:
        (base_dir / dir_name).mkdir(exist_ok=True)

def main():
    """Main bootstrap function"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        console = Console()
        console.print(Panel.fit(
            "[bold cyan]Cisco 4321 ISR Password Reset Tool[/bold cyan]\n"
            "[dim]Bootstrap Initialization[/dim]",
            border_style="cyan"
        ))
        use_rich = True
    except ImportError:
        print("Cisco 4321 ISR Password Reset Tool - Bootstrap")
        print("=" * 80)
        use_rich = False
        console = None
    
    # Check Python version
    if console:
        with console.status("[bold green]Checking Python version...") as status:
            check_python_version()
            status.update("[bold green]✓ Python version OK")
    else:
        print("Checking Python version...")
        check_python_version()
        print("✓ Python version OK")
    
    # Check dependencies
    if console:
        with console.status("[bold green]Checking dependencies...") as status:
            check_dependencies()
            status.update("[bold green]✓ Dependencies OK")
    else:
        print("Checking dependencies...")
        check_dependencies()
        print("✓ Dependencies OK")
    
    # Initialize directories
    if console:
        with console.status("[bold green]Initializing directories...") as status:
            initialize_directories()
            status.update("[bold green]✓ Directories initialized")
    else:
        print("Initializing directories...")
        initialize_directories()
        print("✓ Directories initialized")
    
    # Initialize logging
    try:
        from logging_monitor import LoggingMonitor
    except ImportError:
        # Try relative import
        from .logging_monitor import LoggingMonitor
    
    # Get project root for log directories
    project_root = Path(__file__).parent.parent
    log_monitor = LoggingMonitor(
        log_dir=str(project_root / "logs"),
        monitoring_dir=str(project_root / "monitoring"),
        log_level="INFO",
        enable_console=True
    )
    
    log_monitor.logger.info("Bootstrap complete, launching TUI...")
    
    if console:
        console.print("\n[bold green]Bootstrap complete![/bold green]")
        console.print("[dim]Launching TUI interface...[/dim]\n")
        time.sleep(1)
    
    # Launch TUI
    try:
        from tui_interface import TUIInterface
        from cisco_reset import CiscoReset
        
        tui = TUIInterface(logger=log_monitor.logger)
        # Check if this is first run (no settings file exists)
        project_root = Path(__file__).parent.parent
        settings_file = project_root / "config" / "settings.json"
        show_onboarding = not settings_file.exists()
        tui.show_welcome(show_onboarding=show_onboarding)
        
        # Create main application
        app = CiscoReset(log_monitor=log_monitor, tui=tui)
        
        # Run TUI main loop
        app.run_tui()
        
    except KeyboardInterrupt:
        log_monitor.logger.info("Interrupted by user")
        print("\nExiting...")
    except Exception as e:
        log_monitor.logger.log_exception(e, "bootstrap")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
