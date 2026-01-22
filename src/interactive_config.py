"""
Interactive configuration mode once config access is available
"""

import sys
from typing import List, Optional, Callable, Any

from command_executor import CommandExecutor
from prompt_detector import RouterState


class InteractiveConfig:
    """Interactive configuration shell"""
    
    def __init__(self, command_executor: CommandExecutor, logger: Optional[Any] = None):
        self.command_executor = command_executor
        self.logger = logger
        self.command_history: List[str] = []
        self.active = False
        
    def start(self):
        """Start interactive mode"""
        self.active = True
        if self.logger:
            self.logger.info("Entering interactive configuration mode")
        
        try:
            from rich.console import Console
            from rich.panel import Panel
            console = Console()
            console.print()
            console.print(Panel.fit(
                "[bold cyan]Interactive Configuration Mode[/bold cyan]\n"
                "[dim]Type 'help' for available commands, 'exit' to quit[/dim]",
                border_style="cyan"
            ))
            console.print()
        except ImportError:
            print("\n" + "=" * 80)
            print("Interactive Configuration Mode")
            print("=" * 80)
            print("Type 'help' for available commands, 'exit' to quit")
            print("=" * 80 + "\n")
        
        try:
            from rich.prompt import Prompt
            use_rich = True
        except ImportError:
            use_rich = False
        
        while self.active:
            try:
                if use_rich:
                    command = Prompt.ask("[bold cyan]cisco[/bold cyan]>", default="").strip()
                else:
                    command = input("cisco> ").strip()
                
                if not command:
                    continue
                
                # Handle special commands
                if command.lower() in ['exit', 'quit']:
                    self.stop()
                    break
                elif command.lower() == 'help':
                    self._show_help()
                    continue
                elif command.lower() == 'history':
                    self._show_history()
                    continue
                elif command.lower() == 'clear':
                    print("\n" * 50)
                    continue
                elif command.lower().startswith('show-detection'):
                    # This would show system detection results if available
                    print("System detection results not available in this mode")
                    continue
                
                # Execute command
                self.command_history.append(command)
                success, output = self.command_executor.execute(command, timeout=30.0)
                
                if success:
                    print(output)
                else:
                    print(f"Error: {output[-500:]}")  # Show last 500 chars
                    
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit interactive mode")
            except EOFError:
                self.stop()
                break
            except Exception as e:
                if self.logger:
                    self.logger.log_exception(e, "interactive mode")
                print(f"Error: {e}")
    
    def stop(self):
        """Stop interactive mode"""
        self.active = False
        if self.logger:
            self.logger.info("Exiting interactive configuration mode")
        print("\nExiting interactive mode...")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
Available Commands:
  help              - Show this help message
  exit / quit       - Exit interactive mode
  history           - Show command history
  clear             - Clear screen
  show <command>    - Execute show command
  configure         - Enter configuration mode
  <any IOS command> - Execute any Cisco IOS command

Examples:
  show version
  show running-config
  configure terminal
  enable secret <password>
"""
        print(help_text)
    
    def _show_history(self):
        """Show command history"""
        if not self.command_history:
            print("No command history")
            return
        
        print("\nCommand History:")
        print("-" * 80)
        for i, cmd in enumerate(self.command_history[-20:], 1):  # Last 20 commands
            print(f"{i:3d}: {cmd}")
        print("-" * 80)
