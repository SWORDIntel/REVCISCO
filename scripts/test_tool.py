#!/usr/bin/env python3
"""
Simple test script to verify tool components
"""

import sys
from pathlib import Path

# Add src directory to path
script_dir = Path(__file__).parent
src_dir = script_dir.parent / "src"
sys.path.insert(0, str(src_dir))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from logging_monitor import LoggingMonitor
        print("✓ LoggingMonitor")
    except Exception as e:
        print(f"✗ LoggingMonitor: {e}")
        return False
    
    try:
        from prompt_detector import PromptDetector
        print("✓ PromptDetector")
    except Exception as e:
        print(f"✗ PromptDetector: {e}")
        return False
    
    try:
        from retry_strategies import RetryManager
        print("✓ RetryManager")
    except Exception as e:
        print(f"✗ RetryManager: {e}")
        return False
    
    try:
        from recovery_state_machine import RecoveryStateMachine
        print("✓ RecoveryStateMachine")
    except Exception as e:
        print(f"✗ RecoveryStateMachine: {e}")
        return False
    
    try:
        from serial_connection import SerialConnection
        print("✓ SerialConnection")
    except Exception as e:
        print(f"✗ SerialConnection: {e}")
        return False
    
    try:
        from tui_interface import TUIInterface
        print("✓ TUIInterface")
    except Exception as e:
        print(f"✗ TUIInterface: {e}")
        return False
    
    print("\nAll imports successful!")
    return True

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from logging_monitor import LoggingMonitor
        log_monitor = LoggingMonitor(log_dir="logs", monitoring_dir="monitoring", log_level="INFO")
        log_monitor.logger.info("Test log message")
        print("✓ Logging system")
    except Exception as e:
        print(f"✗ Logging system: {e}")
        return False
    
    try:
        from prompt_detector import PromptDetector
        detector = PromptDetector()
        state, hostname, _ = detector.detect_prompt("Router#")
        if state and state.value == "privileged_mode":
            print("✓ Prompt detection")
        else:
            print("✗ Prompt detection: Wrong state detected")
            return False
    except Exception as e:
        print(f"✗ Prompt detection: {e}")
        return False
    
    try:
        from recovery_state_machine import RecoveryStateMachine, RecoveryState
        sm = RecoveryStateMachine()
        sm.transition(RecoveryState.CONNECTED, "Test")
        if sm.get_current_state() == RecoveryState.CONNECTED:
            print("✓ State machine")
        else:
            print("✗ State machine: State transition failed")
            return False
    except Exception as e:
        print(f"✗ State machine: {e}")
        return False
    
    try:
        from serial_connection import SerialConnection
        conn = SerialConnection()
        ports = conn.detect_ports()
        print(f"✓ Serial port detection (found {len(ports)} ports)")
    except Exception as e:
        print(f"✗ Serial port detection: {e}")
        return False
    
    print("\nAll basic functionality tests passed!")
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("Cisco 4321 ISR Password Reset Tool - Component Test")
    print("=" * 80)
    print()
    
    if test_imports():
        if test_basic_functionality():
            print("\n" + "=" * 80)
            print("All tests passed! Tool is ready to use.")
            print("=" * 80)
            sys.exit(0)
        else:
            print("\nSome functionality tests failed.")
            sys.exit(1)
    else:
        print("\nImport tests failed. Check dependencies.")
        sys.exit(1)
