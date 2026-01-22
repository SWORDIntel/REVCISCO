"""
ROM monitor automation with break sequence and config register manipulation
"""

import time
import re
from typing import Optional, Tuple, Any
from serial_connection import SerialConnection
from prompt_detector import PromptDetector, RouterState
from recovery_state_machine import RecoveryStateMachine, RecoveryState
from retry_strategies import RetryManager, RetryConfig


class RommonHandler:
    """Handles ROM monitor entry and configuration"""
    
    def __init__(self, serial_conn: SerialConnection, prompt_detector: PromptDetector,
                 state_machine: RecoveryStateMachine, retry_manager: RetryManager,
                 logger: Optional[Any] = None, metrics: Optional[Any] = None):
        self.serial_conn = serial_conn
        self.prompt_detector = prompt_detector
        self.state_machine = state_machine
        self.retry_manager = retry_manager
        self.logger = logger
        self.metrics = metrics
        
    def wait_for_boot(self, timeout: float = 60.0) -> bool:
        """Wait for boot sequence to start"""
        if self.logger:
            self.logger.info("Waiting for boot sequence...")
        
        self.state_machine.transition(RecoveryState.WAITING_BOOT, "Waiting for boot")
        
        start_time = time.time()
        boot_detected = False
        
        while time.time() - start_time < timeout:
            output = self.serial_conn.get_output_buffer()
            
            if self.prompt_detector.is_booting(output):
                boot_detected = True
                if self.logger:
                    self.logger.info("Boot sequence detected")
                break
            
            time.sleep(0.5)
        
        return boot_detected
    
    def send_break_sequence(self, timeout: float = 60.0) -> bool:
        """Send break sequence during boot"""
        if self.logger:
            self.logger.info("Sending break sequence...")
        
        self.state_machine.transition(RecoveryState.SENDING_BREAK, "Sending break sequence")
        
        start_time = time.time()
        break_success = False
        
        # Try multiple break attempts
        max_attempts = 5
        attempt_interval = 2.0
        
        for attempt in range(1, max_attempts + 1):
            if time.time() - start_time > timeout:
                break
            
            if self.logger:
                self.logger.info(f"Break attempt {attempt}/{max_attempts}")
            
            # Send break
            success = self.serial_conn.send_break()
            
            if success:
                # Wait a bit and check for ROM monitor
                time.sleep(1.0)
                output = self.serial_conn.get_output_buffer()
                state, _, _ = self.prompt_detector.detect_prompt(output)
                
                if state == RouterState.ROM_MONITOR:
                    break_success = True
                    if self.metrics:
                        self.metrics.record_rommon_entry(time.time())
                    if self.logger:
                        self.logger.info(f"ROM monitor entered on attempt {attempt}")
                    break
            
            # Wait before next attempt
            if attempt < max_attempts:
                time.sleep(attempt_interval)
        
        if not break_success:
            if self.logger:
                self.logger.error("Failed to enter ROM monitor after break sequence")
            return False
        
        self.state_machine.transition(RecoveryState.ROM_MONITOR, "Entered ROM monitor")
        return True
    
    def set_config_register(self, value: str = "0x2142") -> bool:
        """Set configuration register in ROM monitor"""
        if self.logger:
            self.logger.info(f"Setting configuration register to {value}")
        
        def _set_confreg():
            # Send confreg command
            self.serial_conn.write(f"confreg {value}")
            time.sleep(1.0)
            
            # Read response
            output = self.serial_conn.read_output(5.0)
            
            # Verify
            if value.lower() in output.lower() or "0x2142" in output:
                return True
            else:
                # Try reading confreg to verify
                self.serial_conn.write("confreg")
                time.sleep(1.0)
                verify_output = self.serial_conn.read_output(5.0)
                return value.lower() in verify_output.lower()
        
        config = RetryConfig(max_retries=3, base_delay=2.0)
        try:
            success = self.retry_manager.retry("set_confreg", _set_confreg, config=config)
            
            if success:
                self.state_machine.transition(RecoveryState.CONFIG_REG_SET, 
                                             f"Config register set to {value}")
                if self.logger:
                    self.logger.info(f"Configuration register set to {value}")
            else:
                if self.logger:
                    self.logger.error("Failed to set configuration register")
            
            return success
        except Exception as e:
            if self.logger:
                self.logger.log_exception(e, "setting config register")
            return False
    
    def reboot_router(self) -> bool:
        """Reboot router from ROM monitor"""
        if self.logger:
            self.logger.info("Rebooting router...")
        
        self.state_machine.transition(RecoveryState.REBOOTING, "Rebooting router")
        
        # Send reset command
        self.serial_conn.write("reset")
        time.sleep(2.0)
        
        # Clear output buffer
        self.serial_conn.clear_output_buffer()
        
        if self.logger:
            self.logger.info("Reset command sent, waiting for reboot...")
        
        return True
    
    def wait_for_ios_boot(self, timeout: float = 120.0) -> bool:
        """Wait for IOS to boot without startup config"""
        if self.logger:
            self.logger.info("Waiting for IOS to boot...")
        
        start_time = time.time()
        boot_start_time = start_time
        
        while time.time() - start_time < timeout:
            output = self.serial_conn.get_output_buffer()
            
            # Check for boot sequence
            if self.prompt_detector.is_booting(output):
                boot_start_time = time.time()
                continue
            
            # Check for IOS prompt (privileged or user mode)
            state, hostname, _ = self.prompt_detector.detect_prompt(output)
            
            if state in [RouterState.PRIVILEGED_MODE, RouterState.USER_MODE]:
                boot_duration = time.time() - boot_start_time
                if self.metrics:
                    self.metrics.record_boot_duration(boot_duration)
                
                if self.logger:
                    self.logger.info(f"IOS booted successfully (state: {state.value}, hostname: {hostname})")
                
                self.state_machine.transition(RecoveryState.IOS_NO_CONFIG, 
                                             f"IOS booted without startup config")
                return True
            
            time.sleep(0.5)
        
        if self.logger:
            self.logger.error("Timeout waiting for IOS boot")
        return False
    
    def enter_rommon(self, boot_timeout: float = 60.0, break_timeout: float = 60.0) -> bool:
        """
        Complete ROM monitor entry process
        
        Args:
            boot_timeout: Timeout to wait for boot sequence
            break_timeout: Timeout for break sequence attempts
        
        Returns:
            True if successfully entered ROM monitor
        """
        # Wait for boot
        if not self.wait_for_boot(boot_timeout):
            if self.logger:
                self.logger.warning("Boot sequence not detected, attempting break anyway")
        
        # Send break sequence
        if not self.send_break_sequence(break_timeout):
            return False
        
        return True
    
    def complete_recovery_setup(self) -> bool:
        """
        Complete ROM monitor recovery setup:
        1. Enter ROM monitor
        2. Set config register to 0x2142
        3. Reboot router
        4. Wait for IOS boot
        
        Returns:
            True if all steps successful
        """
        # Enter ROM monitor
        if not self.enter_rommon():
            return False
        
        # Set config register
        if not self.set_config_register("0x2142"):
            return False
        
        # Reboot
        if not self.reboot_router():
            return False
        
        # Wait for IOS boot
        if not self.wait_for_ios_boot():
            return False
        
        return True
