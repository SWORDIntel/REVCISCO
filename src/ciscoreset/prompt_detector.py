"""
Advanced prompt detection using regex patterns for Cisco IOS/IOS XE
"""

import re
import time
from typing import Optional, Tuple, Dict
from enum import Enum


class RouterState(Enum):
    """Router state enumeration"""
    UNKNOWN = "unknown"
    BOOTING = "booting"
    ROM_MONITOR = "rom_monitor"
    USER_MODE = "user_mode"
    PRIVILEGED_MODE = "privileged_mode"
    CONFIG_MODE = "config_mode"
    PASSWORD_PROMPT = "password_prompt"
    ERROR = "error"


class PromptDetector:
    """Advanced prompt detection with regex patterns"""
    
    # Prompt patterns
    ROM_MONITOR_PATTERNS = [
        re.compile(r'rommon\s*\d+>\s*', re.IGNORECASE),
        re.compile(r'rommon>\s*', re.IGNORECASE),
        re.compile(r'\(rommon\)>\s*', re.IGNORECASE),
    ]
    
    USER_MODE_PATTERNS = [
        re.compile(r'([A-Za-z0-9_-]+)\s*>\s*$', re.MULTILINE),
    ]
    
    PRIVILEGED_MODE_PATTERNS = [
        re.compile(r'([A-Za-z0-9_-]+)\s*#\s*$', re.MULTILINE),
    ]
    
    CONFIG_MODE_PATTERNS = [
        re.compile(r'([A-Za-z0-9_-]+)\s*\(config[^)]*\)#\s*$', re.MULTILINE),
        re.compile(r'([A-Za-z0-9_-]+)\s*\(config\)#\s*$', re.MULTILINE),
        re.compile(r'([A-Za-z0-9_-]+)\s*\(config-[^)]+\)#\s*$', re.MULTILINE),
    ]
    
    PASSWORD_PROMPT_PATTERNS = [
        re.compile(r'[Pp]assword:\s*$', re.MULTILINE),
        re.compile(r'[Ee]nter\s+[Pp]assword:\s*$', re.MULTILINE),
        re.compile(r'[Pp]assword\s+for\s+[^:]+:\s*$', re.MULTILINE),
    ]
    
    BOOT_PATTERNS = [
        re.compile(r'System Bootstrap', re.IGNORECASE),
        re.compile(r'Initializing', re.IGNORECASE),
        re.compile(r'Loading', re.IGNORECASE),
        re.compile(r'Starting', re.IGNORECASE),
        re.compile(r'Cisco IOS', re.IGNORECASE),
        re.compile(r'Cisco IOS XE', re.IGNORECASE),
    ]
    
    ERROR_PATTERNS = [
        re.compile(r'% Invalid input', re.IGNORECASE),
        re.compile(r'% Invalid command', re.IGNORECASE),
        re.compile(r'% Incomplete command', re.IGNORECASE),
        re.compile(r'% Ambiguous command', re.IGNORECASE),
        re.compile(r'% Error', re.IGNORECASE),
        re.compile(r'% Unknown command', re.IGNORECASE),
    ]
    
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.last_detected_state = RouterState.UNKNOWN
        self.last_hostname: Optional[str] = None
        
    def detect_prompt(self, output: str) -> Tuple[Optional[RouterState], Optional[str], Optional[Dict]]:
        """
        Detect router prompt/state from output
        
        Returns:
            Tuple of (state, hostname, match_info)
        """
        # Check for ROM monitor
        for pattern in self.ROM_MONITOR_PATTERNS:
            match = pattern.search(output)
            if match:
                self.last_detected_state = RouterState.ROM_MONITOR
                return RouterState.ROM_MONITOR, None, {'match': match.group()}
        
        # Check for password prompt
        for pattern in self.PASSWORD_PROMPT_PATTERNS:
            match = pattern.search(output)
            if match:
                self.last_detected_state = RouterState.PASSWORD_PROMPT
                return RouterState.PASSWORD_PROMPT, None, {'match': match.group()}
        
        # Check for config mode
        for pattern in self.CONFIG_MODE_PATTERNS:
            match = pattern.search(output)
            if match:
                hostname = match.group(1)
                self.last_hostname = hostname
                self.last_detected_state = RouterState.CONFIG_MODE
                return RouterState.CONFIG_MODE, hostname, {'match': match.group(), 'hostname': hostname}
        
        # Check for privileged mode
        for pattern in self.PRIVILEGED_MODE_PATTERNS:
            match = pattern.search(output)
            if match:
                hostname = match.group(1)
                self.last_hostname = hostname
                self.last_detected_state = RouterState.PRIVILEGED_MODE
                return RouterState.PRIVILEGED_MODE, hostname, {'match': match.group(), 'hostname': hostname}
        
        # Check for user mode
        for pattern in self.USER_MODE_PATTERNS:
            match = pattern.search(output)
            if match:
                hostname = match.group(1)
                self.last_hostname = hostname
                self.last_detected_state = RouterState.USER_MODE
                return RouterState.USER_MODE, hostname, {'match': match.group(), 'hostname': hostname}
        
        # Check for boot sequence
        for pattern in self.BOOT_PATTERNS:
            if pattern.search(output):
                self.last_detected_state = RouterState.BOOTING
                return RouterState.BOOTING, None, {}
        
        # Check for errors
        for pattern in self.ERROR_PATTERNS:
            match = pattern.search(output)
            if match:
                return RouterState.ERROR, None, {'error': match.group()}
        
        return None, None, None
    
    def wait_for_prompt(self, output_buffer: str, target_state: Optional[RouterState] = None,
                       timeout: Optional[float] = None) -> Tuple[Optional[RouterState], Optional[str], Optional[Dict]]:
        """
        Wait for a specific prompt or any prompt
        
        Args:
            output_buffer: Current output buffer to check
            target_state: Specific state to wait for (None for any)
            timeout: Timeout in seconds (uses default if None)
        
        Returns:
            Tuple of (state, hostname, match_info) or (None, None, None) if timeout
        """
        timeout = timeout or self.timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            state, hostname, match_info = self.detect_prompt(output_buffer)
            
            if state is not None:
                if target_state is None or state == target_state:
                    return state, hostname, match_info
            
            time.sleep(0.1)  # Small delay before next check
        
        return None, None, None
    
    def is_booting(self, output: str) -> bool:
        """Check if router is in boot sequence"""
        for pattern in self.BOOT_PATTERNS:
            if pattern.search(output):
                return True
        return False
    
    def has_error(self, output: str) -> bool:
        """Check if output contains error messages"""
        for pattern in self.ERROR_PATTERNS:
            if pattern.search(output):
                return True
        return False
    
    def requires_password(self, output: str) -> bool:
        """Check if password is required"""
        state, _, _ = self.detect_prompt(output)
        return state == RouterState.PASSWORD_PROMPT
    
    def get_current_state(self) -> RouterState:
        """Get last detected state"""
        return self.last_detected_state
    
    def get_hostname(self) -> Optional[str]:
        """Get last detected hostname"""
        return self.last_hostname
