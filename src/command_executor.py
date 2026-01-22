"""
Robust command execution with retries and verification
"""

import time
import re
from typing import Optional, Tuple, List, Callable, Any
from prompt_detector import PromptDetector, RouterState
from retry_strategies import RetryManager, RetryConfig


class CommandExecutor:
    """Robust command execution with retries and verification"""
    
    def __init__(self, serial_conn, prompt_detector: PromptDetector,
                 retry_manager: RetryManager, logger: Optional[Any] = None,
                 metrics: Optional[Any] = None):
        self.serial_conn = serial_conn
        self.prompt_detector = prompt_detector
        self.retry_manager = retry_manager
        self.logger = logger
        self.metrics = metrics
        
        # Pagination handling
        self.more_pattern = re.compile(r'--More--', re.IGNORECASE)
        self.pagination_keys = [' ', '\r', 'q']
        
    def execute(self, command: str, expected_prompt: Optional[RouterState] = None,
               timeout: float = 30.0, retry: bool = True,
               wait_for_echo: bool = True) -> Tuple[bool, str]:
        """
        Execute a command and wait for response
        
        Args:
            command: Command to execute
            expected_prompt: Expected prompt state after command
            timeout: Timeout in seconds
            retry: Whether to retry on failure
            wait_for_echo: Whether to wait for command echo
        
        Returns:
            Tuple of (success, output)
        """
        def _execute():
            return self._execute_once(command, expected_prompt, timeout, wait_for_echo)
        
        if retry:
            config = RetryConfig(max_retries=3, base_delay=1.0)
            try:
                success, output = self.retry_manager.retry(
                    f"execute_{command.split()[0]}",
                    _execute,
                    config=config,
                    permanent_errors=[ValueError]  # Don't retry syntax errors
                )
                return success, output
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Command execution failed after retries: {e}")
                return False, str(e)
        else:
            return _execute()
    
    def _execute_once(self, command: str, expected_prompt: Optional[RouterState],
                     timeout: float, wait_for_echo: bool) -> Tuple[bool, str]:
        """Execute command once (internal)"""
        start_time = time.time()
        
        # Clear output buffer
        self.serial_conn.clear_output_buffer()
        
        # Send command
        written = self.serial_conn.write(command)
        if written == 0:
            return False, "Failed to write command"
        
        # Wait for command echo
        if wait_for_echo:
            echo_timeout = min(2.0, timeout / 3)
            echo_output = self.serial_conn.read_output(echo_timeout)
            if command.strip() not in echo_output:
                if self.logger:
                    self.logger.debug("Command echo not detected, continuing anyway")
        
        # Read output until prompt appears
        output = ""
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            chunk = self.serial_conn.read_output(0.5)
            if chunk:
                output += chunk
                
                # Check for pagination
                if self.more_pattern.search(output):
                    # Send space to continue
                    self.serial_conn.write(' ')
                    time.sleep(0.1)
                    continue
                
                # Check for prompt
                state, hostname, match_info = self.prompt_detector.detect_prompt(output)
                if state is not None:
                    if expected_prompt is None or state == expected_prompt:
                        duration = time.time() - start_time
                        if self.metrics:
                            self.metrics.record_command_execution(duration)
                            self.metrics.record_response_time(duration)
                        return True, output
                    elif state == RouterState.ERROR:
                        # Error detected
                        duration = time.time() - start_time
                        if self.metrics:
                            self.metrics.record_command_execution(duration)
                        return False, output
            
            time.sleep(0.1)
        
        # Timeout
        duration = time.time() - start_time
        if self.metrics:
            self.metrics.record_timeout()
            self.metrics.record_command_execution(duration)
        
        if self.logger:
            self.logger.warning(f"Command execution timeout: {command}")
        
        return False, output
    
    def execute_with_verification(self, command: str, verification_func: Callable[[str], bool],
                                 timeout: float = 30.0) -> Tuple[bool, str]:
        """
        Execute command and verify result
        
        Args:
            command: Command to execute
            verification_func: Function to verify output (returns True if successful)
            timeout: Timeout in seconds
        
        Returns:
            Tuple of (success, output)
        """
        success, output = self.execute(command, timeout=timeout)
        
        if success:
            if verification_func(output):
                return True, output
            else:
                if self.logger:
                    self.logger.warning(f"Command verification failed: {command}")
                return False, output
        
        return success, output
    
    def enter_config_mode(self) -> bool:
        """Enter configuration mode"""
        success, output = self.execute("configure terminal", 
                                      expected_prompt=RouterState.CONFIG_MODE,
                                      timeout=10.0)
        return success
    
    def exit_config_mode(self) -> bool:
        """Exit configuration mode"""
        success, output = self.execute("end", 
                                      expected_prompt=RouterState.PRIVILEGED_MODE,
                                      timeout=10.0)
        if not success:
            # Try 'exit' instead
            success, output = self.execute("exit", 
                                          expected_prompt=RouterState.PRIVILEGED_MODE,
                                          timeout=10.0)
        return success
    
    def save_config(self, filename: str = "startup-config") -> bool:
        """Save configuration"""
        command = f"copy running-config {filename}"
        success, output = self.execute(command, timeout=60.0)
        
        # Handle potential prompts
        if "Destination filename" in output:
            # Send Enter to accept default
            self.serial_conn.write('\r')
            time.sleep(1.0)
            output += self.serial_conn.read_output(10.0)
        
        # Verify save success
        if "bytes copied" in output.lower() or "[OK]" in output:
            if self.logger:
                self.logger.info("Configuration saved successfully")
            return True
        else:
            if self.logger:
                self.logger.warning(f"Configuration save may have failed: {output[-200:]}")
            return False
    
    def send_password(self, password: str) -> bool:
        """Send password (suppress echo)"""
        # Passwords are typically sent without echo
        written = self.serial_conn.write(password + '\r')
        time.sleep(0.5)  # Wait for processing
        return written > 0
