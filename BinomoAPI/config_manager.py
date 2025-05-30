"""
Professional configuration management for BinomoAPI

This module provides centralized configuration management with support for
environment variables, configuration files, and secure credential handling.
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BinomoConfig:
    """Professional configuration manager for BinomoAPI."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "binomo_config.json"
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Default configuration
        self._config = {
            "api": {
                "demo_mode": True,
                "enable_logging": True,
                "log_level": "INFO",
                "connection_timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 1.0
            },
            "trading": {
                "default_asset": "EUR/USD",
                "min_trade_amount": 1.0,
                "max_trade_amount": 1000.0,
                "default_duration": 60,
                "risk_percentage": 2.0,  # Max % of balance per trade
                "max_concurrent_trades": 5
            },
            "security": {
                "device_id": None,  # Will be generated if not provided
                "session_timeout": 3600,  # 1 hour
                "auto_logout": True
            }
        }
        
        # Load from file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self._merge_config(file_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.warning(f"Could not load config file: {e}")
        
        # Override with environment variables
        self._load_env_vars()
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration with existing."""
        for section, values in new_config.items():
            if section in self._config:
                self._config[section].update(values)
            else:
                self._config[section] = values
    
    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        env_mapping = {
            "BINOMO_DEMO_MODE": ("api", "demo_mode", bool),
            "BINOMO_LOG_LEVEL": ("api", "log_level", str),
            "BINOMO_DEVICE_ID": ("security", "device_id", str),
            "BINOMO_DEFAULT_ASSET": ("trading", "default_asset", str),
            "BINOMO_MIN_TRADE_AMOUNT": ("trading", "min_trade_amount", float),
            "BINOMO_MAX_TRADE_AMOUNT": ("trading", "max_trade_amount", float),
            "BINOMO_RISK_PERCENTAGE": ("trading", "risk_percentage", float),
        }
        
        for env_var, (section, key, var_type) in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    if var_type == bool:
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    elif var_type == float:
                        value = float(value)
                    elif var_type == int:
                        value = int(value)
                    
                    self._config[section][key] = value
                    logger.debug(f"Loaded {env_var} from environment")
                except ValueError as e:
                    logger.warning(f"Invalid value for {env_var}: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value."""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
    
    def save(self, filename: Optional[str] = None) -> None:
        """Save configuration to file."""
        filename = filename or self.config_file
        try:
            with open(filename, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Configuration saved to {filename}")
        except Exception as e:
            logger.error(f"Could not save config: {e}")
    
    def get_credentials(self) -> tuple[Optional[str], Optional[str]]:
        """Get credentials from environment variables."""
        email = os.getenv("BINOMO_EMAIL")
        password = os.getenv("BINOMO_PASSWORD")
        
        if not email or not password:
            logger.warning(
                "Credentials not found in environment variables. "
                "Set BINOMO_EMAIL and BINOMO_PASSWORD environment variables."
            )
        
        return email, password
    
    def get_device_id(self) -> str:
        """Get or generate device ID."""
        device_id = self.get("security", "device_id")
        
        if not device_id:
            # Generate a unique device ID
            import uuid
            device_id = f"binomo-api-{uuid.uuid4().hex[:16]}"
            self.set("security", "device_id", device_id)
            logger.info(f"Generated new device ID: {device_id}")
        
        return device_id
    
    def validate_trade_params(self, amount: float, asset: str = None) -> Dict[str, Any]:
        """Validate trading parameters against configuration."""
        errors = []
        warnings = []
        
        min_amount = self.get("trading", "min_trade_amount", 1.0)
        max_amount = self.get("trading", "max_trade_amount", 1000.0)
        
        if amount < min_amount:
            errors.append(f"Trade amount ${amount} below minimum ${min_amount}")
        elif amount > max_amount:
            errors.append(f"Trade amount ${amount} above maximum ${max_amount}")
        
        risk_percentage = self.get("trading", "risk_percentage", 2.0)
        if risk_percentage > 5.0:
            warnings.append(f"Risk percentage {risk_percentage}% is quite high")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def create_sample_config(self, filename: str = "binomo_config_sample.json") -> None:
        """Create a sample configuration file."""
        sample_config = {
            "api": {
                "demo_mode": True,
                "enable_logging": True,
                "log_level": "INFO",
                "connection_timeout": 30
            },
            "trading": {
                "default_asset": "EUR/USD",
                "min_trade_amount": 1.0,
                "max_trade_amount": 100.0,
                "default_duration": 60,
                "risk_percentage": 2.0,
                "max_concurrent_trades": 3
            },
            "security": {
                "device_id": "your-unique-device-id",
                "session_timeout": 3600,
                "auto_logout": True
            },
            "_comments": {
                "demo_mode": "Set to false for live trading",
                "risk_percentage": "Maximum percentage of balance per trade",
                "device_id": "Unique identifier for your trading setup"
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(sample_config, f, indent=2)
            print(f"✅ Sample configuration created: {filename}")
            print("📝 Edit this file and rename to 'binomo_config.json' to use")
        except Exception as e:
            logger.error(f"Could not create sample config: {e}")

# Global configuration instance
config = BinomoConfig()

def get_config() -> BinomoConfig:
    """Get the global configuration instance."""
    return config
