"""
Main tool script for Cisco 4321 ISR Password Reset
"""

import argparse
import bz2
import gzip
import grp
import json
import lzma
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile
import zlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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

        self.project_root = Path(__file__).parent.parent
        
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
        self.config_backup = ConfigBackup(backup_dir=str(self.project_root / "backups"), logger=self.log_monitor.logger)
        
        # Initialize settings manager
        self.settings_manager = SettingsManager(
            config_dir=str(self.project_root / "config"),
            logger=self.log_monitor.logger
        )
        self.recovery_state_file = self.project_root / "config" / "recovery_state.json"
        
        # Auto-reconnect flag
        self.auto_reconnect_enabled = self.settings_manager.get("auto_reconnect", True)

    def _save_recovery_phase(self, phase: str, next_step: str, details: Optional[Dict] = None) -> None:
        """Persist recovery progress so interrupted workflows can be resumed safely."""
        state = {
            "phase": phase,
            "next_step": next_step,
            "details": details or {},
            "timestamp": datetime.now().isoformat(timespec="seconds")
        }
        try:
            self.recovery_state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.recovery_state_file, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.log_monitor.logger.warning(f"Could not save recovery state: {e}")

    def _load_recovery_phase(self) -> Optional[Dict]:
        """Load persisted recovery progress if present."""
        if not self.recovery_state_file.exists():
            return None
        try:
            with open(self.recovery_state_file, "r") as f:
                return json.load(f)
        except Exception as e:
            self.log_monitor.logger.warning(f"Could not load recovery state: {e}")
            return None

    def _clear_recovery_phase(self) -> None:
        """Clear persisted recovery progress after successful completion."""
        try:
            if self.recovery_state_file.exists():
                self.recovery_state_file.unlink()
        except Exception as e:
            self.log_monitor.logger.warning(f"Could not clear recovery state: {e}")

    def _show_resume_warning_if_needed(self) -> None:
        """Warn users when a previous recovery likely needs cleanup."""
        state = self._load_recovery_phase()
        if not state:
            return
        self.tui.show_recovery_resume_notice(state)

    def _user_in_dialout_group(self) -> bool:
        """Check Linux serial-port group access for the current user."""
        try:
            dialout_gid = grp.getgrnam("dialout").gr_gid
            supplementary = [g.gr_gid for g in grp.getgrall() if self._current_username() in g.gr_mem]
            return dialout_gid in os.getgroups() or dialout_gid in supplementary
        except KeyError:
            return False
        except Exception as e:
            self.log_monitor.logger.debug(f"Could not check dialout group membership: {e}")
            return False

    def _current_username(self) -> str:
        """Return current username for group checks."""
        try:
            import getpass
            return getpass.getuser()
        except Exception:
            return ""

    def _default_baudrate(self) -> int:
        """Return the configured Cisco console baudrate."""
        return int(self.settings_manager.get("default_baudrate", 9600))

    def _select_port_for_4321(self) -> Optional[str]:
        """Run Cisco 4321 ISR preflight and select a serial port."""
        if not self.serial_conn:
            self.serial_conn = SerialConnection(
                logger=self.log_monitor.logger,
                metrics=self.log_monitor.metrics
            )

        ports = self.serial_conn.detect_ports()
        baudrate = self._default_baudrate()
        if not self.tui.show_cisco_4321_preflight(
            ports,
            baudrate=baudrate,
            in_dialout_group=self._user_in_dialout_group()
        ):
            return None

        return self.tui.show_port_selection(ports)

    def _select_port_for_pin_discovery(self) -> Optional[str]:
        """Run receive-only UART pin discovery safety checks and select a port."""
        if not self.serial_conn:
            self.serial_conn = SerialConnection(
                logger=self.log_monitor.logger,
                metrics=self.log_monitor.metrics
            )

        ports = self.serial_conn.detect_ports()
        baudrate = self._default_baudrate()
        if not self.tui.show_uart_pin_discovery_intro(
            ports,
            baudrate=baudrate,
            in_dialout_group=self._user_in_dialout_group()
        ):
            return None

        return self.tui.show_port_selection(ports)

    def _check_cisco_4321_identity(self) -> None:
        """Best-effort model check after connection."""
        if not self.command_executor:
            return

        identity = {
            "model": "Unknown",
            "serial": "Unknown",
            "ios_version": "Unknown",
            "is_4321": False,
            "status": "Unable to verify model from current prompt"
        }

        try:
            success, version_output = self.command_executor.execute("show version", timeout=12.0, retry=False)
            if success:
                version_match = re.search(r'Cisco IOS XE Software, Version\s+([^\r\n]+)', version_output, re.IGNORECASE)
                if not version_match:
                    version_match = re.search(r'Version\s+([0-9][^\s,]+)', version_output, re.IGNORECASE)
                if version_match:
                    identity["ios_version"] = version_match.group(1).strip()
                if re.search(r'\b(?:ISR4321|4321)\b', version_output, re.IGNORECASE):
                    identity["is_4321"] = True
                    identity["model"] = "Cisco ISR4321"

            success, inventory_output = self.command_executor.execute("show inventory", timeout=12.0, retry=False)
            if success:
                pid_match = re.search(r'PID:\s*([A-Z0-9-]+)', inventory_output, re.IGNORECASE)
                sn_match = re.search(r'SN:\s*([A-Z0-9]+)', inventory_output, re.IGNORECASE)
                if pid_match:
                    identity["model"] = pid_match.group(1)
                    if "4321" in identity["model"]:
                        identity["is_4321"] = True
                if sn_match:
                    identity["serial"] = sn_match.group(1)

            identity["status"] = (
                "Detected Cisco 4321 ISR target"
                if identity["is_4321"]
                else "Connected, but model was not confirmed as Cisco 4321 ISR"
            )
        except Exception as e:
            self.log_monitor.logger.debug(f"Cisco 4321 identity check failed: {e}")

        self.tui.show_router_identity(identity)
        
    def connect(self, port: Optional[str] = None, baudrate: int = 9600,
                verify_identity: bool = True) -> bool:
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

        if verify_identity:
            self._check_cisco_4321_identity()
        
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
            self._save_recovery_phase(
                "waiting_boot",
                "Power cycle the Cisco 4321 ISR and wait for boot output."
            )
            self.tui.show_workflow_progress(*workflow_steps[0], "Monitoring boot sequence...")
            if not self.rommon_handler.wait_for_boot():
                self.tui.show_status("Boot sequence not detected, continuing anyway...", "warning")
            
            # Step 2: Send break
            self._save_recovery_phase(
                "sending_break",
                "Enter ROMmon, then set confreg 0x2142."
            )
            self.tui.show_workflow_progress(*workflow_steps[1], "Sending break sequence...")
            if not self.rommon_handler.send_break_sequence():
                if not self._handle_break_failure():
                    return False
            
            # Step 3: ROM monitor entered
            self._save_recovery_phase(
                "rommon",
                "Set config register to 0x2142 and reboot."
            )
            self.tui.show_workflow_progress(*workflow_steps[2], "ROM monitor active")
            
            # Step 4: Set config register
            self.tui.show_workflow_progress(*workflow_steps[3], "Setting confreg 0x2142...")
            if not self.rommon_handler.set_config_register("0x2142"):
                return False
            self._save_recovery_phase(
                "confreg_2142_set",
                "Reboot, reset passwords, then restore config-register 0x2102.",
                {"critical_cleanup": "config-register 0x2102 must be restored before completion"}
            )
            
            # Step 5: Reboot
            self.tui.show_workflow_progress(*workflow_steps[4], "Rebooting router...")
            if not self.rommon_handler.reboot_router():
                return False
            
            # Wait for IOS boot
            self.tui.show_status("Waiting for IOS to boot...", "info")
            if not self.rommon_handler.wait_for_ios_boot():
                return False
            self._save_recovery_phase(
                "ios_no_config",
                "Back up config, reset password, restore config-register 0x2102, and save."
            )

            # Backup before changing passwords or writing configuration.
            self._offer_pre_change_backup()
            
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
            
            self._clear_recovery_phase()
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

    def _handle_break_failure(self) -> bool:
        """Offer practical recovery choices when automated break fails."""
        while True:
            choice = self.tui.show_break_failure_menu()

            if choice == "retry":
                self.tui.show_status("Retrying Cisco 4321 ISR break sequence...", "info")
                if self.rommon_handler.send_break_sequence():
                    return True
            elif choice == "manual":
                self.tui.show_rommon_manual_assistant()
                output = self.serial_conn.get_output_buffer() if self.serial_conn else ""
                state, _, _ = self.prompt_detector.detect_prompt(output)
                if state and state.value == "rom_monitor":
                    return True
                if self.tui.confirm("Is the router now at a rommon prompt?", default=False):
                    return True
            else:
                self.tui.show_error_dialog(
                    "Break Sequence Failed",
                    "Failed to enter ROM monitor",
                    ["Retry during early boot", "Check console cable", "Use the manual ROMmon assistant"]
                )
                return False

    def _offer_pre_change_backup(self) -> None:
        """Offer a best-effort backup before password/config changes."""
        if not self.command_executor:
            return

        if not self.settings_manager.get("auto_backup", True):
            return

        if not self.tui.confirm(
            "Back up Cisco 4321 ISR startup/running config before password changes?",
            default=True
        ):
            return

        backup_results = []
        with self.tui.show_progress("Backing up Cisco 4321 ISR configuration"):
            for label, command, backup_func in [
                ("startup", "show startup-config", self.config_backup.backup_startup_config),
                ("running", "show running-config", self.config_backup.backup_running_config),
            ]:
                try:
                    success, output = self.command_executor.execute(command, timeout=30.0)
                    if success and output.strip():
                        backup_file = backup_func(output)
                        if backup_file:
                            backup_results.append(f"{label}: {backup_file}")
                    else:
                        self.log_monitor.logger.warning(f"Could not back up {label} config: {output[-200:]}")
                except Exception as e:
                    self.log_monitor.logger.warning(f"Could not back up {label} config: {e}")

            config_register_backup = self.config_backup.backup_config_register(
                "Recovery workflow active; expected normal value after completion: 0x2102"
            )
            if config_register_backup:
                backup_results.append(f"config-register note: {config_register_backup}")

        if backup_results:
            self.tui.show_success_message("Backup complete:\n" + "\n".join(backup_results))
        else:
            self.tui.show_status("No configuration backup was created; continuing workflow.", "warning")
    
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

    def run_uart_firmware_dump(self) -> bool:
        """Capture a raw firmware/image stream from UART to disk."""
        if not self.serial_conn or not self.serial_conn.is_open():
            self.tui.show_error_dialog(
                "Not Connected",
                "Please connect to the Cisco 4321 ISR first",
                ["Select option 3 to connect", "Start the firmware stream before capture"]
            )
            return False

        dump_dir = self.project_root / "firmware_dumps"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_file = str(dump_dir / f"uart_dump_{timestamp}.bin")
        settings = self.tui.show_uart_dump_menu(default_file)
        if not settings:
            return False

        self.tui.show_status(
            "Starting raw UART capture. Begin or continue firmware transmission now.",
            "warning"
        )
        try:
            result = self.serial_conn.dump_raw_to_file(**settings)
            self.tui.show_uart_dump_result(result)
            if self.tui.confirm("Try to decompress this dump now?", default=False):
                self.decompress_firmware_dump(result["output_file"])
            return True
        except Exception as e:
            self.log_monitor.logger.log_exception(e, "UART firmware dump")
            self.tui.show_error_dialog(
                "UART Dump Failed",
                str(e),
                ["Verify the serial connection is open", "Check disk space", "Retry with a longer idle timeout"]
            )
            return False

    def run_uart_pin_discovery(self) -> bool:
        """Receive-only listener to help identify candidate UART_DEBUG GND/RX pins."""
        port = self._select_port_for_pin_discovery()
        if not port:
            return False

        log_dir = self.project_root / "logs"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_log = str(log_dir / f"uart_pin_discovery_{timestamp}.log")
        settings = self.tui.show_uart_discovery_settings(default_log)
        if not settings:
            return False
        output_path = Path(settings["output_file"]).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        session_file = output_path.with_suffix(output_path.suffix + ".session.json")
        session = {
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "port": port,
            "cable_type": settings.get("cable_type", "unknown"),
            "cable_note": settings.get("cable_note", "unknown"),
            "ground_label": settings.get("ground_label", "unknown"),
            "rx_labels": settings.get("rx_labels", [settings.get("rx_label", "unknown")]),
            "baudrates": settings.get("baudrates", [settings.get("baudrate", self._default_baudrate())]),
            "duration": settings.get("duration"),
            "notes": settings.get("notes", "none"),
            "attempts": [],
            "pin_map": {}
        }

        attempts: List[Dict[str, Any]] = []
        attempt_index = 1
        found_boot_text = False
        with open(output_path, "w", encoding="utf-8", errors="replace") as log_file:
            self._write_discovery_session_header(log_file, session)
            for rx_label in session["rx_labels"]:
                for baudrate in session["baudrates"]:
                    attempt = {
                        "attempt_index": attempt_index,
                        "port": port,
                        "cable_type": session["cable_type"],
                        "ground_label": session["ground_label"],
                        "rx_label": rx_label,
                        "baudrate": int(baudrate)
                    }
                    attempt_index += 1
                    if not self.tui.confirm_uart_discovery_attempt(attempt):
                        attempt["classification"] = "skipped"
                        attempts.append(attempt)
                        continue

                    result = self._run_uart_discovery_attempt(port, settings, attempt, log_file)
                    attempts.append(result)
                    found_boot_text = found_boot_text or result["detected_boot_text"]
                    self.tui.show_uart_discovery_result(result)
                    if result["detected_boot_text"]:
                        break
                if found_boot_text:
                    break

        session["ended_at"] = datetime.now().isoformat(timespec="seconds")
        session["attempts"] = attempts
        session["pin_map"] = self._build_uart_pin_map(session["ground_label"], attempts)
        session["combined_log_file"] = str(output_path)
        session["session_file"] = str(session_file)
        session_file.write_text(json.dumps(session, indent=2), encoding="utf-8")
        self.tui.show_uart_discovery_session_result(session)

        successful = [attempt for attempt in attempts if attempt.get("detected_boot_text")]
        if successful:
            best = successful[0]
            if self.tui.confirm("Show TX introduction checklist now?", default=False):
                self.tui.show_uart_tx_intro_checklist(best["ground_label"], best["rx_label"])
        return found_boot_text

    def _run_uart_discovery_attempt(self, port: str, settings: Dict[str, Any],
                                    attempt: Dict[str, Any], log_file: Any) -> Dict[str, Any]:
        """Run one receive-only UART discovery attempt."""
        baudrate = int(attempt["baudrate"])
        discovery_conn = SerialConnection(
            port=port,
            baudrate=baudrate,
            logger=self.log_monitor.logger,
            metrics=self.log_monitor.metrics
        )
        if not discovery_conn.open(port, baudrate):
            result = {
                **attempt,
                "bytes_captured": 0,
                "output_file": getattr(log_file, "name", "unknown"),
                "detected_boot_text": False,
                "classification": "connection_failed",
                "sample": ""
            }
            self.tui.show_error_dialog(
                "Discovery Connection Failed",
                f"Could not open {port}",
                ["Check USB UART permissions", "Close other serial tools", "Try a different adapter port"]
            )
            return result

        try:
            self.tui.show_status(
                f"Listening receive-only at {baudrate} baud. Power cycle the Cisco 4321 ISR now and watch for boot text.",
                "warning"
            )
            output = discovery_conn.read_output(settings["duration"])
            classification, detected = self._classify_uart_discovery_output(output)
            result = {
                **attempt,
                "bytes_captured": len(output.encode("utf-8", errors="replace")),
                "output_file": getattr(log_file, "name", "unknown"),
                "detected_boot_text": detected,
                "classification": classification,
                "sample": output
            }
            self._write_discovery_attempt_log(log_file, settings, result, output)
            return result
        finally:
            discovery_conn.close()

    def _classify_uart_discovery_output(self, output: str) -> tuple:
        """Classify discovery output into boot text, unreadable data, readable unknown, or no output."""
        boot_patterns = [
            "System Bootstrap",
            "Cisco IOS",
            "Cisco IOS XE",
            "ROMMON",
            "Initializing",
            "Readonly ROMMON"
        ]
        if any(pattern.lower() in output.lower() for pattern in boot_patterns):
            return "boot_text", True
        if not output:
            return "no_output", False

        printable = sum(1 for char in output if char.isprintable() or char in "\r\n\t")
        printable_ratio = printable / max(len(output), 1)
        if "\ufffd" in output or printable_ratio < 0.65:
            return "unreadable_output", False
        return "readable_unknown", False

    def _write_discovery_session_header(self, log_file: Any, session: Dict[str, Any]) -> None:
        """Write metadata for a UART discovery session log."""
        log_file.write("# UART Pin Discovery Session Log\n")
        log_file.write(f"# Started: {session['started_at']}\n")
        log_file.write(f"# Port: {session['port']}\n")
        log_file.write(f"# Cable type: {session['cable_type']}\n")
        log_file.write(f"# Cable note: {session['cable_note']}\n")
        log_file.write(f"# Cisco ground candidate: {session['ground_label']}\n")
        log_file.write(f"# RX candidates: {', '.join(session['rx_labels'])}\n")
        log_file.write(f"# Baud rates: {', '.join(str(baud) for baud in session['baudrates'])}\n")
        log_file.write(f"# Notes: {session.get('notes', 'none')}\n")
        log_file.write("# Wiring rule: adapter GND plus adapter RX only; TX/power/control pins disconnected.\n\n")

    def _write_discovery_attempt_log(self, log_file: Any, settings: Dict[str, Any],
                                     result: Dict[str, Any], output: str) -> None:
        """Append one attempt and its captured text to the combined session log."""
        log_file.write(f"# --- attempt {result['attempt_index']} ---\n")
        log_file.write(f"# Timestamp: {datetime.now().isoformat(timespec='seconds')}\n")
        log_file.write(f"# Baud rate: {result['baudrate']}\n")
        log_file.write(f"# Cable type: {result['cable_type']}\n")
        log_file.write(f"# Cable note: {settings.get('cable_note', 'unknown')}\n")
        log_file.write(f"# Cisco ground candidate: {result['ground_label']}\n")
        log_file.write(f"# Cisco RX-test candidate: {result['rx_label']}\n")
        log_file.write(f"# Classification: {result['classification']}\n")
        log_file.write(f"# Bytes captured: {result['bytes_captured']}\n")
        log_file.write("# --- captured output follows ---\n")
        log_file.write(output)
        log_file.write("\n# --- end attempt ---\n\n")
        log_file.flush()

    def _build_uart_pin_map(self, ground_label: str, attempts: List[Dict[str, Any]]) -> Dict[str, str]:
        """Build a simple pin map from discovery attempt results."""
        pin_map = {ground_label: "likely GND candidate"}
        for attempt in attempts:
            rx_label = attempt.get("rx_label", "unknown")
            classification = attempt.get("classification", "unknown")
            if classification == "boot_text":
                pin_map[rx_label] = f"likely Cisco TX/output at {attempt.get('baudrate')} baud"
            elif classification == "readable_unknown":
                pin_map[rx_label] = f"readable output, verify baud/content at {attempt.get('baudrate')} baud"
            elif classification == "unreadable_output":
                pin_map[rx_label] = "activity seen, likely wrong baud/noise/inverted UART"
            elif classification == "no_output":
                pin_map.setdefault(rx_label, "silent for tested baud(s)")
            elif classification == "skipped":
                pin_map.setdefault(rx_label, "skipped")
            elif classification == "connection_failed":
                pin_map.setdefault(rx_label, "not tested; connection failed")
        return pin_map

    def _detect_compression_format(self, input_path: Path) -> str:
        """Detect common compression/archive formats by magic bytes."""
        with open(input_path, "rb") as f:
            magic = f.read(8)

        if magic.startswith(b"\x1f\x8b"):
            return "gzip"
        if magic.startswith(b"BZh"):
            return "bzip2"
        if magic.startswith(b"\xfd7zXZ\x00"):
            return "xz"
        if magic.startswith(b"PK\x03\x04"):
            return "zip"
        if tarfile.is_tarfile(input_path):
            return "tar"
        return "zlib"

    def _find_working_binwalk(self) -> Optional[str]:
        """Find a binwalk executable that starts successfully."""
        candidates = [
            Path.home() / ".cargo" / "bin" / "binwalk",
            self.project_root / "venv" / "bin" / "binwalk",
            shutil.which("binwalk")
        ]

        for candidate in candidates:
            if not candidate:
                continue
            path = str(candidate)
            if not Path(path).exists():
                continue
            try:
                result = subprocess.run(
                    [path, "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return path
            except Exception:
                continue
        return None

    def _extract_with_binwalk(self, input_path: Path, output: Path) -> None:
        """Extract firmware with binwalk CLI."""
        binwalk_path = self._find_working_binwalk()
        if not binwalk_path:
            raise RuntimeError(
                "No working binwalk executable found. Install with: "
                "cargo install --git https://github.com/ReFirmLabs/binwalk.git binwalk"
            )

        output.mkdir(parents=True, exist_ok=True)
        commands = [
            [binwalk_path, "--extract", "--directory", str(output), str(input_path)],
            [binwalk_path, "-e", "--directory", str(output), str(input_path)],
            [binwalk_path, "-e", str(input_path)],
        ]
        last_error = ""
        for command in commands:
            result = subprocess.run(command, capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                return
            last_error = (result.stderr or result.stdout or "").strip()

        raise RuntimeError(f"binwalk extraction failed: {last_error}")

    def decompress_firmware_dump(self, input_file: str, output_path: Optional[str] = None,
                                 format_hint: str = "auto") -> Optional[Dict[str, str]]:
        """Decompress or extract a captured firmware dump."""
        input_path = Path(input_file).expanduser()
        if not input_path.exists():
            self.tui.show_error_dialog("Dump Not Found", f"File does not exist: {input_path}")
            return None

        fmt = self._detect_compression_format(input_path) if format_hint == "auto" else format_hint
        default_output = input_path.with_suffix(input_path.suffix + ".decompressed")
        if fmt in ["zip", "tar", "binwalk"]:
            default_output = input_path.with_suffix(input_path.suffix + "_extracted")

        output = Path(output_path).expanduser() if output_path else default_output
        output.parent.mkdir(parents=True, exist_ok=True)

        try:
            if fmt == "gzip":
                with gzip.open(input_path, "rb") as src, open(output, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            elif fmt == "bzip2":
                with bz2.open(input_path, "rb") as src, open(output, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            elif fmt == "xz":
                with lzma.open(input_path, "rb") as src, open(output, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            elif fmt == "zip":
                output.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(input_path, "r") as archive:
                    archive.extractall(output)
            elif fmt == "tar":
                output.mkdir(parents=True, exist_ok=True)
                with tarfile.open(input_path, "r:*") as archive:
                    archive.extractall(output)
            elif fmt == "binwalk":
                self._extract_with_binwalk(input_path, output)
            elif fmt == "zlib":
                data = input_path.read_bytes()
                try:
                    decompressed = zlib.decompress(data)
                except zlib.error:
                    decompressed = zlib.decompress(data, -zlib.MAX_WBITS)
                output.write_bytes(decompressed)
            else:
                raise ValueError(f"Unsupported decompression format: {fmt}")

            result = {
                "input_file": str(input_path),
                "output_path": str(output),
                "format": fmt
            }
            self.tui.show_decompression_result(result)
            return result
        except Exception as e:
            self.log_monitor.logger.log_exception(e, "firmware dump decompression")
            self.tui.show_error_dialog(
                "Decompression Failed",
                str(e),
                [
                    "Confirm the dump starts at the compressed data header",
                    "Try a different format instead of auto",
                    "Use binwalk externally for unknown Cisco container formats"
                ]
            )
            return None

    def run_firmware_decompression(self) -> bool:
        """Prompt for an existing firmware dump and decompress it."""
        settings = self.tui.show_decompression_menu(str(self.project_root / "firmware_dumps"))
        if not settings:
            return False
        return self.decompress_firmware_dump(**settings) is not None
    
    def run_tui(self):
        """Run TUI main loop"""
        self._show_resume_warning_if_needed()
        while True:
            # Get connection status
            if self.serial_conn and self.serial_conn.is_open():
                status = f"Connected to {self.serial_conn.port} @ {self.serial_conn.baudrate} baud"
            else:
                status = "Not Connected"
            
            choice = self.tui.show_main_menu(connection_status=status)
            
            if choice == "1":
                # Receive-only UART pin discovery
                self.run_uart_pin_discovery()
            elif choice == "2":
                # Guided workflow
                if self.tui.show_guided_workflow():
                    # Now connect and run workflow
                    port = self._select_port_for_4321()
                    if port:
                        with self.tui.show_progress("Connecting to router"):
                            if self.connect(port, self._default_baudrate(), verify_identity=False):
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
            elif choice == "3":
                # Connect to router
                port = self._select_port_for_4321()
                if port:
                    with self.tui.show_progress("Connecting to router"):
                        if self.connect(port, self._default_baudrate()):
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
            elif choice == "4":
                # Password reset workflow
                if not self.serial_conn or not self.serial_conn.is_open():
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 3 to connect"]
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
            elif choice == "5":
                # System detection
                if not self.serial_conn or not self.serial_conn.is_open():
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 3 to connect"]
                    )
                    time.sleep(2)
                    continue
                
                with self.tui.show_progress("Running system detection"):
                    if self.run_system_detection_only():
                        export_format = self.tui.show_detection_results(self.system_detector.get_results())
                        if export_format:
                            export_file = self.system_detector.export_results(export_format)
                            self.tui.show_success_message(f"Results exported to {export_file}")
            elif choice == "6":
                # Interactive command mode
                if not self.command_executor:
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 3 to connect"]
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
            elif choice == "7":
                # View logs
                project_root = Path(__file__).parent.parent
                log_dir = str(project_root / "logs")
                self.tui.show_log_viewer(log_dir)
            elif choice == "8":
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
            elif choice == "10":
                # Show metrics
                metrics = self.log_monitor.get_current_metrics()
                self.tui.show_metrics(metrics)
            elif choice == "11":
                # Configuration backup/restore
                if not self.command_executor:
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 3 to connect"]
                    )
                    time.sleep(2)
                    continue
                
                project_root = Path(__file__).parent.parent
                backup_dir = str(project_root / "backups")
                self.tui.show_backup_menu(backup_dir, self.command_executor)
            elif choice == "12":
                # Individual detection options
                if not self.command_executor or not self.system_detector:
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 3 to connect"]
                    )
                    time.sleep(2)
                    continue
                
                self.tui.show_individual_detection_menu(self.system_detector)
            elif choice == "13":
                # Advanced password reset options
                if not self.command_executor or not self.password_reset:
                    self.tui.show_error_dialog(
                        "Not Connected",
                        "Please connect to router first",
                        ["Select option 3 to connect"]
                    )
                    time.sleep(2)
                    continue
                
                # Verify privileged access
                if not self.password_reset.verify_privileged_access():
                    self.tui.show_error_dialog(
                        "Privileged Access Required",
                        "Router must be in privileged mode (no password) to use advanced password reset options",
                        ["Run password reset workflow first (option 4)", "Or ensure router is in privileged mode"]
                    )
                    time.sleep(2)
                    continue
                
                self.tui.show_advanced_password_reset_menu(self.password_reset)
            elif choice == "14":
                # Raw UART firmware/image dump
                self.run_uart_firmware_dump()
            elif choice == "15":
                # Decompress an existing dump
                self.run_firmware_decompression()
            elif choice == "9":
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
