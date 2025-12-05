"""Configuration management system for storing and retrieving application settings."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet


class ConfigManager:
    """Manages application configuration with JSON persistence and encryption support."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize the ConfigManager.

        Args:
            config_dir: Directory where configuration files are stored
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        self.key_file = self.config_dir / ".key"
        self._config_cache: Dict[str, Any] = {}
        self._cipher = self._get_or_create_cipher()
        self._load_config()

    def _get_or_create_cipher(self) -> Fernet:
        """Get or create encryption cipher for sensitive data."""
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
        return Fernet(key)

    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self._config_cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config_cache = {}
        else:
            self._config_cache = {}

    def _save_config(self) -> None:
        """Save configuration to JSON file."""
        with open(self.config_file, "w") as f:
            json.dump(self._config_cache, f, indent=2)

    def save_config(self, key: str, value: Any) -> None:
        """
        Save a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config_cache[key] = value
        self._save_config()

    def load_config(self, key: str, default: Any = None) -> Any:
        """
        Load a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config_cache.get(key, default)

    def get_all_configs(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Dictionary of all configurations
        """
        return dict(self._config_cache)

    def clear_config(self, key: str) -> None:
        """
        Clear a configuration value.

        Args:
            key: Configuration key to clear
        """
        if key in self._config_cache:
            del self._config_cache[key]
            self._save_config()

    def encrypt_credential(self, credential: str) -> str:
        """
        Encrypt a credential string.

        Args:
            credential: Credential to encrypt

        Returns:
            Encrypted credential as string
        """
        encrypted = self._cipher.encrypt(credential.encode())
        return encrypted.decode()

    def decrypt_credential(self, encrypted_credential: str) -> str:
        """
        Decrypt a credential string.

        Args:
            encrypted_credential: Encrypted credential string

        Returns:
            Decrypted credential
        """
        decrypted = self._cipher.decrypt(encrypted_credential.encode())
        return decrypted.decode()

    def save_encrypted_credential(self, key: str, credential: str) -> None:
        """
        Save an encrypted credential.

        Args:
            key: Configuration key
            credential: Credential to encrypt and save
        """
        encrypted = self.encrypt_credential(credential)
        self.save_config(key, encrypted)

    def load_encrypted_credential(self, key: str) -> Optional[str]:
        """
        Load and decrypt a credential.

        Args:
            key: Configuration key

        Returns:
            Decrypted credential or None if not found
        """
        encrypted = self.load_config(key)
        if encrypted is None:
            return None
        try:
            return self.decrypt_credential(encrypted)
        except Exception:
            return None
