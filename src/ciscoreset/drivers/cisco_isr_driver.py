from typing import Optional, Tuple
from .base_driver import BaseDeviceDriver
from ..recovery_state_machine import RecoveryState

class CiscoISR4321Driver(BaseDeviceDriver):
    """Driver for Cisco 4321 ISR Routers"""
    
    @property
    def name(self) -> str:
        return "Cisco 4321 ISR"
        
    def get_break_sequence(self) -> bytes:
        # Default break is handled via pyserial's send_break(), but can fallback to Ctrl+C or similar
        return b'\\x03' # Ctrl+C as fallback
        
    def detect_prompt(self, output: str) -> Tuple[Optional[RecoveryState], Optional[str], Optional[str]]:
        # This would delegate to the existing prompt_detector logic for ISRs
        pass
        
    def get_password_reset_commands(self, new_password: str) -> list[str]:
        return [
            "configure terminal",
            f"enable secret {new_password}",
            "exit",
            "write memory"
        ]
