"""
Main tool script for Cisco 4321 ISR Password Reset
"""

import argparse
import sys
import time
import logging
from pathlib import Path
from typing import Optional

# Import all modules
from logging_monitor import LoggingMonitor
from serial_connection import SerialConnection
from prompt_detector import PromptDetector
from retry_strategies import RetryManager
from command_executor import CommandExecutor
from recovery_state_machine import RecoveryStateMachine, RecoveryState
from rommon_handler import RommonHandler
from password_reset import PasswordReset
from system_detector import SystemDetector
from interactive_config import InteractiveConfig
from config_backup import ConfigBackup
from tui_interface import TUIInterface
from settings_manager import SettingsManager


class CiscoReset:
    """Main Cisco Reset application"""
    
    def __init__(self, log_monitor: Optional[LoggingMonitor] = None, 
                 tui: Optional[TUIInterface] = None):
        # Initialize logging
        if log_monitor is None:
            # Get project root for log directories
            project_root = Path(__file__).parent.parent
            self.log_monitor = LoggingMonitor(
                log_dir=str(project_root / "logs"),
                monitoring_dir=str(project_root / "monitoring"),
                log_level="INFO",
                enable_console=True
            )
        else:
            self.log_monitor = log_monitor
        
        self.tui = tui or TUIInterface(logger=self.log_monitor.logger)
        
        # Initialize components
        self.serial_conn: Optional[SerialConnection] = None
        self.prompt_detector = PromptDetector()
        self.retry_manager = RetryManager(
            logger=self.log_monitor.logger,
            metrics=self.log_monitor.metrics
        )
        self.state_machine = RecoveryStateMachine(logger=self.log_monitor.logger)
        self.command_executor: Optional[CommandExecutor] = None
        self.rommon_handler: Optional[RommonHandler] = None
        self.password_reset: Optional[PasswordReset] = None
        self.system_detector: Optional[SystemDetector] = None
        # Get project root for backup directory
        project_root = Path(__file__).parent.parent
        self.config_backup = ConfigBackup(backup_dir=str(project_root / "backups"), logger=self.log_monitor.logger)
        
        # Initialize settings manager
        self.settings_manager = SettingsManager(
            config_dir=str(project_root / "config"),
            logger=self.log_monitor.logger
        )
        
        # Auto-reconnect flag
        self.auto_reconnect_enabled = self.settings_manager.get("auto_reconnect", True)
        
    def connect(self, port: Optional[str] = None, baudrate: int = 9600) -> bool:
        """Connect to router"""
        self.log_monitor.logger.info("Connecting to router...")
        self.state_machine.transition(RecoveryState.CONNECTED, "Connecting to router")
        
        # Create serial connection
        self.serial_conn = SerialConnection(
            port=port,
            baudrate=baudrate,
            logger=self.log_monitor.logger,
            metrics=self.log_monitor.metrics
        )
        
        # Auto-detect port if not provided
        if not port:
            # Try to use last port from settings
            last_port = self.settings_manager.get("last_port")
            if last_port and Path(last_port).exists():
                if self.tui.confirm(f"Use last port {last_port}?", default=True):
                    port = last_port
            
            if not port:
                detected_ports = self.serial_conn.detect_ports()
                if not detected_ports:
                    self.log_monitor.logger.error("No TTY ports found")
                    return False
                
                if len(detected_ports) == 1:
                    port = detected_ports[0]
                else:
                    # Use TUI to select port
                    port = self.tui.show_port_selection(detected_ports)
                    if not port:
                        return False
        
        # Save last used port
        self.settings_manager.set("last_port", port)
        
        # Open connection
        if not self.serial_conn.open(port, baudrate):
            return False
        
        # Record connection start time
        self.log_monitor.metrics.start_connection()
        
        # Initialize command executor
        self.command_executor = CommandExecutor(
            self.serial_conn,
            self.prompt_detector,
            self.retry_manager,
            logger=self.log_monitor.logger,
            metrics=self.log_monitor.metrics
        )
        
        # Initialize ROM monitor handler
        self.rommon_handler = RommonHandler(
            self.serial_conn,
            self.prompt_detector,
            self.state_machine,
            self.retry_manager,
            logger=self.log_monitor.logger,
            metrics=self.log_monitor.metrics
        )
        
        # Initialize password reset
        self.password_reset = PasswordReset(
            self.command_executor,
            self.state_machine,
            logger=self.log_monitor.logger,
            metrics=self.log_monitor.metrics,
            interactive=True
        )
        
        # Initialize system detector
        self.system_detector = SystemDetector(
            self.command_executor,
            logger=self.log_monitor.logger,
            metrics=self.log_monitor.metrics
        )
        
        return True
    
    def run_password_reset_workflow(self) -> bool:
        """Run complete password reset workflow"""
        self.log_monitor.logger.info("Starting password reset workflow...")
        
        workflow_steps = [
            ("Waiting for boot sequence", 1, 7),
            ("Sending break sequence", 2, 7),
            ("Entering ROM monitor", 3, 7),
            ("Setting configuration register", 4, 7),
            ("Rebooting router", 5, 7),
            ("Running system detection", 6, 7),
            ("Resetting password", 7, 7),
        ]
        
        try:
            # Step 1: Wait for boot
            self.tui.show_workflow_progress(*workflow_steps[0], "Monitoring boot sequence...")
            if not self.rommon_handler.wait_for_boot():
                self.tui.show_status("Boot sequence not detected, continuing anyway...", "warning")
            
            # Step 2: Send break
            self.tui.show_workflow_progress(*workflow_steps[1], "Sending break sequence...")
            if not self.rommon_handler.send_break_sequence():
                self.tui.show_error_dialog(
                    "Break Sequence Failed",
                    "Failed to enter ROM monitor",
                    ["Try power cycling the router", "Check serial connection", "Try manual break"]
                )
                return False
            
            # Step 3: ROM monitor entered
            self.tui.show_workflow_progress(*workflow_steps[2], "ROM monitor active")
            
            # Step 4: Set config register
            self.tui.show_workflow_progress(*workflow_steps[3], "Setting confreg 0x2142...")
            if not self.rommon_handler.set_config_register("0x2142"):
                return False
            
            # Step 5: Reboot
            self.tui.show_workflow_progress(*workflow_steps[4], "Rebooting router...")
            if not self.rommon_handler.reboot_router():
                return False
            
            # Wait for IOS boot
            self.tui.show_status("Waiting for IOS to boot...", "info")
            if not self.rommon_handler.wait_for_ios_boot():
                return False
            
            # Step 6: System detection
            self.state_machine.transition(RecoveryState.SYSTEM_DETECTION, "Running system detection")
            self.tui.show_workflow_progress(*workflow_steps[5], "Detecting system information...")
            detection_results = self.system_detector.detect_all()
            self.tui.show_detection_results(detection_results)
            
            # Step 7: Password reset
            self.tui.show_workflow_progress(*workflow_steps[6], "Resetting enable secret...")
            if not self.password_reset.complete_password_reset():
                self.log_monitor.logger.error("Password reset failed")
                return False
            
            self.tui.show_success_message("Password reset workflow completed successfully!")
            self.log_monitor.logger.info("Password reset workflow completed successfully")
            return True
            
        except Exception as e:
            self.log_monitor.logger.log_exception(e, "password reset workflow")
            self.state_machine.enter_error_state(e, "Password reset workflow")
            self.tui.show_error_dialog(
                "Workflow Error",
                str(e),
                ["Check logs for details", "Verify router connection", "Try again"]
            )
            return False
    
    def run_system_detection_only(self) -> bool:
        """Run system detection only"""
        if not self.command_executor:
            self.log_monitor.logger.error("Not connected to router")
            return False
        
        self.tui.show_status("Running system detection...", "info")
        results = self.system_detector.detect_all()
        self.tui.show_detection_results(results)
        
        # Export results
        export_file = self.system_detector.export_results("json")
        self.tui.show_status(f"Results exported to {export_file}", "success")
        
        return True
    
    def run_tui(self):
        """Run TUI main loop"""
        while True:
            # Get connection status
            if self.serial_conn and self.serial_conn.is_open():
                status = f"Connected to {self.serial_conn.port} @ {self.serial_conn.baudrate} baud"
            else:
                status = "Not Connected"
            
            choice = self.tui.show_main_menu(connection_status=status)
            
            if choice == "1":
                # Guided workflow
                if self.tui.show_guided_workflow():
                    # Now connect and run workflow
                    if not self.serial_conn:
                        self.serial_conn = SerialConnection(
                            logger=self.log_monitor.logger,
                            metrics=self.log_monitor.metrics
                        )
                    ports = self.serial_conn.detect_ports()
                    port = self.tui.show_port_selection(ports)
                    if port:
                        with self.tui.show_progress("Connecting to router"):
                            if self.connect(port):
                                self.tui.show_success_message(f"Connected to {port}")
                                # Run the password reset workflow
                                self.run_password_reset_workflow()
                            else:
                                self.tui.show_error_dialog(
                                    "Connection Failed",
                                    f"Failed to connect to {port}",
                                    [
                                        "Check cable connection",
                                        "Verify port permissions (user in dialout group)",
                                        "Check if port is already in use",
                                        "Try a different port"
                                    ]
                                )
            elif choice == "2":
                # Connect to router
                if not self.serial_conn:
                    self.serial_conn = SerialConnection(
                        logger=self.log_monitor.logger,
                        metrics=self.log_monitor.metrics
                    )
                ports = self.serial_conn.detect_ports()
                port = self.tui.show_port_selection(ports)
                if port:
                    with self.tui.show_progress("Connecting to router"):
                        if self.connect(port):
                            self.tui.show_success_message(f"Connected to {port}")
                        else:
                            self.tui.show_error_dialog(
                                "Connection Failed",
                                f"Failed to connect to {port}",
                                [
                                    "Check cable connection",
                                    "Verify port permissions (user in dialout group)",
                                    "Check if port is already in use",
                                    "Try a different port"
                                ]
                            )
            elif choice == "3":
                # Password reset workflow
                if not self.serial_conn or not self.serial_conn.is_open():
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 1 to connect"]
                    )
                    time.sleep(2)
                    continue
                
                if not self.tui.confirm("Start password reset workflow? This will reboot the router.", default=False):
                    continue
                
                self.tui.show_info_panel(
                    "Password Reset Workflow",
                    "This process will:\n"
                    "1. Send break sequence during boot\n"
                    "2. Enter ROM monitor\n"
                    "3. Set config register to skip startup config\n"
                    "4. Reboot router\n"
                    "5. Reset enable secret password\n"
                    "6. Restore config register\n"
                    "7. Save configuration"
                )
                
                if self.tui.confirm("Continue?", default=True):
                    self.run_password_reset_workflow()
            elif choice == "4":
                # System detection
                if not self.serial_conn or not self.serial_conn.is_open():
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 1 to connect"]
                    )
                    time.sleep(2)
                    continue
                
                with self.tui.show_progress("Running system detection"):
                    if self.run_system_detection_only():
                        export_format = self.tui.show_detection_results(self.system_detector.get_results())
                        if export_format:
                            export_file = self.system_detector.export_results(export_format)
                            self.tui.show_success_message(f"Results exported to {export_file}")
            elif choice == "5":
                # Interactive command mode
                if not self.command_executor:
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 1 to connect"]
                    )
                    time.sleep(2)
                    continue
                
                self.tui.show_info_panel(
                    "Interactive Command Mode",
                    "You can now execute any Cisco IOS command.\n"
                    "Type 'help' for available commands.\n"
                    "Type 'exit' to return to main menu."
                )
                interactive = InteractiveConfig(self.command_executor, logger=self.log_monitor.logger)
                interactive.start()
                
                # Auto-reconnect if connection was lost
                if self.auto_reconnect_enabled and (not self.serial_conn or not self.serial_conn.is_open()):
                    last_port = self.settings_manager.get("last_port")
                    if last_port:
                        self.tui.show_status("Connection lost, attempting to reconnect...", "warning")
                        if self.connect(last_port):
                            self.tui.show_success_message("Reconnected successfully")
                        else:
                            self.tui.show_error_dialog("Reconnection Failed", "Could not reconnect to router", 
                                                      ["Check cable connection", "Verify port is available"])
            elif choice == "6":
                # View logs
                project_root = Path(__file__).parent.parent
                log_dir = str(project_root / "logs")
                self.tui.show_log_viewer(log_dir)
            elif choice == "7":
                # Settings
                current_settings = self.settings_manager.get_all()
                updated = self.tui.show_settings_menu(current_settings)
                if updated:
                    if updated == {}:  # Reset to defaults
                        # Reload defaults
                        self.settings_manager = SettingsManager(
                            config_dir=str(Path(__file__).parent.parent / "config"),
                            logger=self.log_monitor.logger
                        )
                        self.tui.show_success_message("Settings reset to defaults")
                    else:
                        # Update specific settings
                        self.settings_manager.update(updated)
                        self.tui.show_success_message("Settings updated")
                        
                        # Apply settings that affect runtime
                        if "log_level" in updated:
                            self.log_monitor.logger.setLevel(getattr(logging, updated["log_level"].upper(), logging.INFO))
            elif choice == "9":
                # Show metrics
                metrics = self.log_monitor.get_current_metrics()
                self.tui.show_metrics(metrics)
            elif choice == "10":
                # Configuration backup/restore
                if not self.command_executor:
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 1 to connect"]
                    )
                    time.sleep(2)
                    continue
                
                project_root = Path(__file__).parent.parent
                backup_dir = str(project_root / "backups")
                self.tui.show_backup_menu(backup_dir, self.command_executor)
            elif choice == "11":
                # Individual detection options
                if not self.command_executor or not self.system_detector:
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 1 to connect"]
                    )
                    time.sleep(2)
                    continue
                
                self.tui.show_individual_detection_menu(self.system_detector)
            elif choice == "12":
                # Advanced password reset options
                if not self.command_executor or not self.password_reset:
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 1 to connect"]
                    )
                    time.sleep(2)
                    continue
                
                # Verify privileged access
                if not self.password_reset.verify_privileged_access():
                    self.tui.show_error_dialog(
                        "Privileged Access Required",
                        "Router must be in privileged mode (no password) to use advanced password reset options",
                        ["Run password reset workflow first (option 2)", "Or ensure router is in privileged mode"]
                    )
                    time.sleep(2)
                    continue
                
                self.tui.show_advanced_password_reset_menu(self.password_reset)
            elif choice == "8":
                # Exit
                break
        
        # Cleanup
        if self.serial_conn:
            self.serial_conn.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Cisco 4321 ISR Password Reset Tool")
    parser.add_argument("--port", help="TTY port (e.g., /dev/ttyS0)")
    parser.add_argument("--baud", type=int, default=9600, help="Baud rate (default: 9600)")
    parser.add_argument("--auto-detect", action="store_true", help="Auto-detect TTY port")
    parser.add_argument("--detect-only", action="store_true", help="Run system detection only")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--no-tui", action="store_true", help="Disable TUI, use CLI only")
    
    args = parser.parse_args()
    
    # Create application
    app = CiscoReset()
    
    if args.no_tui:
        # CLI mode
        if args.port or args.auto_detect:
            if app.connect(args.port, args.baud):
                if args.detect_only:
                    app.run_system_detection_only()
                else:
                    app.run_password_reset_workflow()
        else:
            parser.print_help()
    else:
        # TUI mode
        app.run_tui()


if __name__ == "__main__":
    main()
