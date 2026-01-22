"""
State machine for recovery process tracking with rollback capabilities
"""

import time
from typing import Optional, Dict, List, Callable, Any
from enum import Enum
from dataclasses import dataclass, field


class RecoveryState(Enum):
    """Recovery process states"""
    INITIAL = "initial"
    CONNECTED = "connected"
    WAITING_BOOT = "waiting_boot"
    SENDING_BREAK = "sending_break"
    ROM_MONITOR = "rom_monitor"
    CONFIG_REG_SET = "config_reg_set"
    REBOOTING = "rebooting"
    IOS_NO_CONFIG = "ios_no_config"
    SYSTEM_DETECTION = "system_detection"
    PASSWORD_RESET = "password_reset"
    CONFIG_SAVED = "config_saved"
    COMPLETE = "complete"
    ERROR = "error"
    ROLLBACK = "rollback"


@dataclass
class StateCheckpoint:
    """State checkpoint for rollback"""
    state: RecoveryState
    timestamp: float
    data: Dict = field(default_factory=dict)
    config_register: Optional[str] = None
    config_backup: Optional[str] = None


class RecoveryStateMachine:
    """State machine for tracking recovery process"""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        RecoveryState.INITIAL: [RecoveryState.CONNECTED, RecoveryState.ERROR],
        RecoveryState.CONNECTED: [RecoveryState.WAITING_BOOT, RecoveryState.ERROR],
        RecoveryState.WAITING_BOOT: [RecoveryState.SENDING_BREAK, RecoveryState.ERROR],
        RecoveryState.SENDING_BREAK: [RecoveryState.ROM_MONITOR, RecoveryState.SENDING_BREAK, RecoveryState.ERROR],
        RecoveryState.ROM_MONITOR: [RecoveryState.CONFIG_REG_SET, RecoveryState.ERROR],
        RecoveryState.CONFIG_REG_SET: [RecoveryState.REBOOTING, RecoveryState.ERROR],
        RecoveryState.REBOOTING: [RecoveryState.IOS_NO_CONFIG, RecoveryState.ERROR],
        RecoveryState.IOS_NO_CONFIG: [RecoveryState.SYSTEM_DETECTION, RecoveryState.PASSWORD_RESET, RecoveryState.ERROR],
        RecoveryState.SYSTEM_DETECTION: [RecoveryState.PASSWORD_RESET, RecoveryState.ERROR],
        RecoveryState.PASSWORD_RESET: [RecoveryState.CONFIG_SAVED, RecoveryState.ERROR],
        RecoveryState.CONFIG_SAVED: [RecoveryState.COMPLETE, RecoveryState.ERROR],
        RecoveryState.ERROR: [RecoveryState.ROLLBACK, RecoveryState.INITIAL],
        RecoveryState.ROLLBACK: [RecoveryState.INITIAL, RecoveryState.ERROR],
        RecoveryState.COMPLETE: [],  # Terminal state
    }
    
    def __init__(self, logger: Optional[Any] = None):
        self.current_state = RecoveryState.INITIAL
        self.state_history: List[Dict] = []
        self.checkpoints: List[StateCheckpoint] = []
        self.logger = logger
        self.original_config_register: Optional[str] = None
        self.config_backup: Optional[str] = None
        
    def transition(self, new_state: RecoveryState, reason: str = "", 
                  data: Optional[Dict] = None) -> bool:
        """
        Transition to new state
        
        Args:
            new_state: Target state
            reason: Reason for transition
            data: Optional data to store with transition
        
        Returns:
            True if transition is valid, False otherwise
        """
        if new_state not in self.VALID_TRANSITIONS.get(self.current_state, []):
            if self.logger:
                self.logger.error(
                    f"Invalid state transition: {self.current_state} -> {new_state}"
                )
            return False
        
        old_state = self.current_state
        timestamp = time.time()
        
        self.current_state = new_state
        
        transition_record = {
            'from_state': old_state.value,
            'to_state': new_state.value,
            'timestamp': timestamp,
            'reason': reason,
            'data': data or {}
        }
        self.state_history.append(transition_record)
        
        if self.logger:
            self.logger.log_state_transition(old_state.value, new_state.value, reason)
        
        return True
    
    def create_checkpoint(self, data: Optional[Dict] = None) -> StateCheckpoint:
        """Create a checkpoint at current state"""
        checkpoint = StateCheckpoint(
            state=self.current_state,
            timestamp=time.time(),
            data=data or {},
            config_register=self.original_config_register,
            config_backup=self.config_backup
        )
        self.checkpoints.append(checkpoint)
        
        if self.logger:
            self.logger.debug(f"Checkpoint created at state {self.current_state.value}")
        
        return checkpoint
    
    def restore_checkpoint(self, checkpoint: Optional[StateCheckpoint] = None) -> bool:
        """Restore from checkpoint"""
        if checkpoint is None:
            if not self.checkpoints:
                return False
            checkpoint = self.checkpoints[-1]
        
        self.current_state = checkpoint.state
        self.original_config_register = checkpoint.config_register
        self.config_backup = checkpoint.config_backup
        
        if self.logger:
            self.logger.info(f"Restored checkpoint at state {checkpoint.state.value}")
        
        return True
    
    def get_current_state(self) -> RecoveryState:
        """Get current state"""
        return self.current_state
    
    def get_state_history(self) -> List[Dict]:
        """Get state transition history"""
        return self.state_history.copy()
    
    def set_original_config_register(self, value: str):
        """Store original configuration register value"""
        self.original_config_register = value
        if self.logger:
            self.logger.debug(f"Stored original config register: {value}")
    
    def get_original_config_register(self) -> Optional[str]:
        """Get original configuration register value"""
        return self.original_config_register
    
    def set_config_backup(self, backup: str):
        """Store configuration backup"""
        self.config_backup = backup
        if self.logger:
            self.logger.debug("Stored configuration backup")
    
    def get_config_backup(self) -> Optional[str]:
        """Get configuration backup"""
        return self.config_backup
    
    def enter_error_state(self, error: Exception, reason: str = ""):
        """Enter error state"""
        error_reason = f"{reason}: {error}" if reason else str(error)
        self.transition(RecoveryState.ERROR, error_reason, {'error': str(error), 'error_type': type(error).__name__})
    
    def can_rollback(self) -> bool:
        """Check if rollback is possible"""
        return len(self.checkpoints) > 0
    
    def rollback(self) -> bool:
        """Rollback to last checkpoint"""
        if not self.can_rollback():
            if self.logger:
                self.logger.warning("No checkpoint available for rollback")
            return False
        
        if self.transition(RecoveryState.ROLLBACK, "Rolling back to checkpoint"):
            return self.restore_checkpoint()
        return False
    
    def is_terminal_state(self) -> bool:
        """Check if in terminal state"""
        return self.current_state in [RecoveryState.COMPLETE, RecoveryState.ERROR]
    
    def get_time_in_state(self, state: RecoveryState) -> float:
        """Get total time spent in a state"""
        total_time = 0.0
        entry_time = None
        
        for transition in self.state_history:
            if transition['to_state'] == state.value:
                entry_time = transition['timestamp']
            elif entry_time and transition['from_state'] == state.value:
                total_time += transition['timestamp'] - entry_time
                entry_time = None
        
        # If still in this state
        if entry_time and self.current_state == state:
            total_time += time.time() - entry_time
        
        return total_time
