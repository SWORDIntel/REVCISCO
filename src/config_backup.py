"""
Configuration backup and restore utilities
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Any


class ConfigBackup:
    """Configuration backup and restore"""
    
    def __init__(self, backup_dir: str = "backups", logger: Optional[Any] = None):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger
        
    def backup_running_config(self, config: str, prefix: str = "running") -> Optional[str]:
        """Backup running configuration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_config_{timestamp}.txt"
        backup_file = self.backup_dir / filename
        
        try:
            with open(backup_file, 'w') as f:
                f.write(config)
            
            if self.logger:
                self.logger.info(f"Backed up {prefix} configuration to {backup_file}")
            
            return str(backup_file)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to backup configuration: {e}")
            return None
    
    def backup_startup_config(self, config: str) -> Optional[str]:
        """Backup startup configuration"""
        return self.backup_running_config(config, prefix="startup")
    
    def backup_config_register(self, value: str) -> Optional[str]:
        """Backup configuration register value"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"config_register_{timestamp}.txt"
        backup_file = self.backup_dir / filename
        
        try:
            with open(backup_file, 'w') as f:
                f.write(f"Original config register: {value}\n")
                f.write(f"Backup time: {datetime.now().isoformat()}\n")
            
            if self.logger:
                self.logger.info(f"Backed up config register to {backup_file}")
            
            return str(backup_file)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to backup config register: {e}")
            return None
    
    def restore_config(self, backup_file: str) -> Optional[str]:
        """Restore configuration from backup file"""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            if self.logger:
                self.logger.error(f"Backup file not found: {backup_file}")
            return None
        
        try:
            with open(backup_path, 'r') as f:
                config = f.read()
            
            if self.logger:
                self.logger.info(f"Restored configuration from {backup_file}")
            
            return config
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to restore configuration: {e}")
            return None
