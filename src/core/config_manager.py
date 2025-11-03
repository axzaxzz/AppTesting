"""
Configuration Manager for Wave.AI
Handles loading, saving, and validating user settings
"""

import json
import os
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """Manages application configuration"""
    
    DEFAULT_CONFIG = {
        "github": {
            "repo_url": "",
            "branch": "main",
            "auto_push": True,
            "auto_pull": True,
            "sync_interval": 30
        },
        "local": {
            "code_directory": "",
            "watch_patterns": ["*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.html", "*.css", "*.json", "*.md"]
        },
        "perplexity": {
            "url": "https://www.perplexity.ai",
            "custom_prompt_enabled": True,
            "custom_prompt_template": "coding_assistant"
        },
        "ui": {
            "theme": "dark",
            "max_tabs": 5,
            "show_notifications": True,
            "window_width": 1400,
            "window_height": 900
        },
        "sync": {
            "commit_prefix": "[Wave.AI Auto]",
            "conflict_strategy": "manual",
            "auto_commit_on_save": True,
            "commit_message_template": "[Wave.AI Auto] {timestamp}: {files_changed}"
        },
        "version_control": {
            "max_history": 100,
            "checkpoint_interval": 300,
            "auto_checkpoint": True
        }
    }
    
    def __init__(self, config_path="config/settings.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        # Save default config if file didn't exist
        if not self.config_path.exists():
            self.save()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        else:
            # Create default config file
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            # Return defaults first, save will be called after config is set
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge loaded config with defaults"""
        merged = default.copy()
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged
    
    def save(self):
        """Save current configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get(self, key_path: str, default=None) -> Any:
        """
        Get configuration value using dot notation
        Example: config.get('github.repo_url')
        """
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value: Any, save_immediately=True):
        """
        Set configuration value using dot notation
        Example: config.set('github.repo_url', 'https://github.com/user/repo')
        """
        keys = key_path.split('.')
        config_ref = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        # Set the value
        config_ref[keys[-1]] = value
        
        if save_immediately:
            self.save()
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if not self.get('github.repo_url'):
            errors.append("GitHub repository URL is not set")
        
        if not self.get('local.code_directory'):
            errors.append("Local code directory is not set")
        
        # Validate paths
        code_dir = self.get('local.code_directory')
        if code_dir and not Path(code_dir).exists():
            errors.append(f"Local code directory does not exist: {code_dir}")
        
        # Validate sync interval
        sync_interval = self.get('github.sync_interval')
        if sync_interval < 10:
            errors.append("Sync interval must be at least 10 seconds")
        
        return (len(errors) == 0, errors)
    
    def is_configured(self) -> bool:
        """Check if essential configuration is complete"""
        return bool(self.get('github.repo_url') and self.get('local.code_directory'))
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
    
    def export_config(self, export_path: str):
        """Export configuration to a different file"""
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def import_config(self, import_path: str):
        """Import configuration from another file"""
        with open(import_path, 'r', encoding='utf-8') as f:
            imported = json.load(f)
            self.config = self._merge_configs(self.DEFAULT_CONFIG, imported)
            self.save()


# Global config instance
config = ConfigManager()

