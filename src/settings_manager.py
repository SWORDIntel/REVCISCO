"""
Settings management with persistence
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class SettingsManager:
    """Manage application settings with persistence"""
    
    def __init__(self, config_dir: str = "config", logger: Optional[Any] = None):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        self.logger = logger
        self.settings: Dict[str, Any] = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        default_settings = {
            "last_port": None,
            "default_baudrate": 9600,
            "log_level": "INFO",
            "auto_reconnect": True,
            "command_timeout": 30.0,
            "break_retry_count": 5,
            "enable_metrics": True,
            "auto_backup": True,
            "show_welcome": True,
            "theme": "default"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    default_settings.update(loaded)
                    return default_settings
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Failed to load settings: {e}, using defaults")
        
        return default_settings
    
    def save_settings(self) -> bool:
        """Save settings to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            if self.logger:
                self.logger.debug(f"Settings saved to {self.config_file}")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """Set a setting value"""
        self.settings[key] = value
        if save:
            return self.save_settings()
        return True
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings.copy()
    
    def update(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """Update multiple settings"""
        self.settings.update(updates)
        if save:
            return self.save_settings()
        return True
