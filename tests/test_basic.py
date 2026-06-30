import pytest

def test_imports():
    """Test that all modules can be imported correctly."""
    from ciscoreset import logging_monitor
    from ciscoreset import prompt_detector
    from ciscoreset import retry_strategies
    from ciscoreset import recovery_state_machine
    from ciscoreset import serial_connection
    from ciscoreset import tui_interface

    assert logging_monitor is not None
    assert prompt_detector is not None
    assert retry_strategies is not None
    assert recovery_state_machine is not None
    assert serial_connection is not None
    assert tui_interface is not None

def test_prompt_detector():
    """Test prompt detection."""
    from ciscoreset.prompt_detector import PromptDetector
    detector = PromptDetector()
    state, hostname, _ = detector.detect_prompt("Router#")
    assert state is not None
    assert state.value == "privileged_mode"

def test_state_machine():
    """Test the recovery state machine transitions."""
    from ciscoreset.recovery_state_machine import RecoveryStateMachine, RecoveryState
    import logging
    sm = RecoveryStateMachine(logger=logging.getLogger("test"))
    sm.transition(RecoveryState.CONNECTED, "Test")
    assert sm.get_current_state() == RecoveryState.CONNECTED
