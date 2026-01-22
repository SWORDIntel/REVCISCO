"""
Interactive password reset workflow
"""

import getpass
from typing import Optional, Tuple, Any
from command_executor import CommandExecutor
from prompt_detector import RouterState
from recovery_state_machine import RecoveryState, RecoveryStateMachine


class PasswordReset:
    """Password reset workflow"""
    
    def __init__(self, command_executor: CommandExecutor, state_machine: RecoveryStateMachine,
                 logger: Optional[Any] = None, metrics: Optional[Any] = None,
                 interactive: bool = True):
        self.command_executor = command_executor
        self.state_machine = state_machine
        self.logger = logger
        self.metrics = metrics
        self.interactive = interactive
        
    def verify_privileged_access(self) -> bool:
        """Verify router is in privileged mode without password"""
        if self.logger:
            self.logger.info("Verifying privileged access...")
        
        # Try to execute a privileged command
        success, output = self.command_executor.execute("show version", timeout=10.0)
        
        if success:
            # Check if we're in privileged mode
            state, _, _ = self.command_executor.prompt_detector.detect_prompt(output)
            if state == RouterState.PRIVILEGED_MODE:
                if self.logger:
                    self.logger.info("Privileged access verified (no password required)")
                return True
        
        if self.logger:
            self.logger.warning("Privileged access not available")
        return False
    
    def get_password_input(self, prompt: str = "Enter new enable secret password: ",
                          confirm: bool = True) -> Optional[str]:
        """Get password input from user"""
        if not self.interactive:
            if self.logger:
                self.logger.warning("Not in interactive mode, cannot get password")
            return None
        
        try:
            password = getpass.getpass(prompt)
            
            if confirm:
                password_confirm = getpass.getpass("Confirm password: ")
                if password != password_confirm:
                    if self.logger:
                        self.logger.error("Passwords do not match")
                    return None
            
            return password
        except (KeyboardInterrupt, EOFError):
            if self.logger:
                self.logger.warning("Password input cancelled")
            return None
    
    def reset_enable_secret(self, password: Optional[str] = None) -> bool:
        """Reset enable secret password"""
        if self.logger:
            self.logger.info("Resetting enable secret password...")
        
        self.state_machine.transition(RecoveryState.PASSWORD_RESET, "Resetting enable secret")
        
        # Get password if not provided
        if password is None:
            password = self.get_password_input("Enter new enable secret password: ")
            if not password:
                return False
        
        # Enter config mode
        if not self.command_executor.enter_config_mode():
            if self.logger:
                self.logger.error("Failed to enter configuration mode")
            return False
        
        # Set enable secret
        command = f"enable secret {password}"
        success, output = self.command_executor.execute(command, 
                                                       expected_prompt=RouterState.CONFIG_MODE,
                                                       timeout=10.0)
        
        if not success:
            if self.logger:
                self.logger.error("Failed to set enable secret")
            self.command_executor.exit_config_mode()
            return False
        
        # Exit config mode
        if not self.command_executor.exit_config_mode():
            if self.logger:
                self.logger.warning("Failed to exit configuration mode")
        
        if self.logger:
            self.logger.info("Enable secret password reset successfully")
        
        return True
    
    def reset_console_password(self, password: Optional[str] = None) -> bool:
        """Reset console password (optional)"""
        if password is None:
            if not self.interactive:
                return False
            password = self.get_password_input("Enter new console password (optional, press Enter to skip): ",
                                             confirm=False)
            if not password:
                return True  # User skipped
        
        if self.logger:
            self.logger.info("Resetting console password...")
        
        # Enter config mode
        if not self.command_executor.enter_config_mode():
            return False
        
        # Configure console line
        commands = [
            "line console 0",
            f"password {password}",
            "login"
        ]
        
        for cmd in commands:
            success, _ = self.command_executor.execute(cmd, 
                                                      expected_prompt=RouterState.CONFIG_MODE,
                                                      timeout=5.0)
            if not success:
                self.command_executor.exit_config_mode()
                return False
        
        # Exit config mode
        self.command_executor.exit_config_mode()
        
        if self.logger:
            self.logger.info("Console password reset successfully")
        
        return True
    
    def reset_vty_password(self, password: Optional[str] = None) -> bool:
        """Reset VTY (Telnet/SSH) password (optional)"""
        if password is None:
            if not self.interactive:
                return False
            password = self.get_password_input("Enter new VTY password (optional, press Enter to skip): ",
                                             confirm=False)
            if not password:
                return True  # User skipped
        
        if self.logger:
            self.logger.info("Resetting VTY password...")
        
        # Enter config mode
        if not self.command_executor.enter_config_mode():
            return False
        
        # Configure VTY lines
        commands = [
            "line vty 0 4",
            f"password {password}",
            "login"
        ]
        
        for cmd in commands:
            success, _ = self.command_executor.execute(cmd, 
                                                      expected_prompt=RouterState.CONFIG_MODE,
                                                      timeout=5.0)
            if not success:
                self.command_executor.exit_config_mode()
                return False
        
        # Exit config mode
        self.command_executor.exit_config_mode()
        
        if self.logger:
            self.logger.info("VTY password reset successfully")
        
        return True
    
    def restore_config_register(self) -> bool:
        """Restore configuration register to normal (0x2102)"""
        if self.logger:
            self.logger.info("Restoring configuration register to 0x2102...")
        
        # Enter config mode
        if not self.command_executor.enter_config_mode():
            return False
        
        # Set config register
        command = "config-register 0x2102"
        success, _ = self.command_executor.execute(command, 
                                                  expected_prompt=RouterState.CONFIG_MODE,
                                                  timeout=10.0)
        
        if not success:
            self.command_executor.exit_config_mode()
            return False
        
        # Exit config mode
        self.command_executor.exit_config_mode()
        
        if self.logger:
            self.logger.info("Configuration register restored to 0x2102")
        
        return True
    
    def save_configuration(self) -> bool:
        """Save configuration to startup-config"""
        if self.logger:
            self.logger.info("Saving configuration...")
        
        self.state_machine.transition(RecoveryState.CONFIG_SAVED, "Saving configuration")
        
        success = self.command_executor.save_config("startup-config")
        
        if success:
            if self.logger:
                self.logger.info("Configuration saved successfully")
        else:
            if self.logger:
                self.logger.error("Failed to save configuration")
        
        return success
    
    def verify_password_reset(self) -> bool:
        """Verify password reset was successful"""
        if self.logger:
            self.logger.info("Verifying password reset...")
        
        # Check running config for enable secret
        success, output = self.command_executor.execute("show running-config | include enable secret",
                                                       timeout=10.0)
        
        if success and "enable secret" in output.lower():
            if self.logger:
                self.logger.info("Password reset verified in running configuration")
            return True
        
        if self.logger:
            self.logger.warning("Could not verify password reset")
        return False
    
    def complete_password_reset(self, enable_password: Optional[str] = None,
                               console_password: Optional[str] = None,
                               vty_password: Optional[str] = None) -> bool:
        """
        Complete password reset workflow
        
        Returns:
            True if all steps successful
        """
        # Verify access
        if not self.verify_privileged_access():
            return False
        
        # Reset enable secret
        if not self.reset_enable_secret(enable_password):
            return False
        
        # Optional: Reset console password
        if console_password is not None or self.interactive:
            self.reset_console_password(console_password)
        
        # Optional: Reset VTY password
        if vty_password is not None or self.interactive:
            self.reset_vty_password(vty_password)
        
        # Restore config register
        if not self.restore_config_register():
            return False
        
        # Save configuration
        if not self.save_configuration():
            return False
        
        # Verify
        self.verify_password_reset()
        
        self.state_machine.transition(RecoveryState.COMPLETE, "Password reset complete")
        
        return True
