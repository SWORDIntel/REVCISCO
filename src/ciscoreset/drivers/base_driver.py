from abc import ABC, abstractmethod
from typing import Optional, Tuple
from ..recovery_state_machine import RecoveryState

class BaseDeviceDriver(ABC):
    """Abstract base class for all device drivers"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the driver/platform"""
        pass
        
    @abstractmethod
    def get_break_sequence(self) -> bytes:
        """Return the appropriate break sequence for this device"""
        pass
        
    @abstractmethod
    def detect_prompt(self, output: str) -> Tuple[Optional[RecoveryState], Optional[str], Optional[str]]:
        """
        Analyze output to determine current prompt state.
        Returns: (RecoveryState, hostname, raw_prompt)
        """
        pass
        
    @abstractmethod
    def get_password_reset_commands(self, new_password: str) -> list[str]:
        """Return the sequence of commands needed to reset the password"""
        pass
