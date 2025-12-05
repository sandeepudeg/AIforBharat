"""Tests for ConfigManager."""

import pytest
import tempfile
import json
from pathlib import Path
from hypothesis import given, strategies as st
from src.config_manager import ConfigManager


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_config_manager_save_and_load(temp_config_dir):
    """Test saving and loading configuration values."""
    manager = ConfigManager(config_dir=temp_config_dir)
    
    manager.save_config("test_key", "test_value")
    loaded_value = manager.load_config("test_key")
    
    assert loaded_value == "test_value"


def test_config_manager_load_nonexistent_key(temp_config_dir):
    """Test loading a non-existent key returns default."""
    manager = ConfigManager(config_dir=temp_config_dir)
    
    loaded_value = manager.load_config("nonexistent", default="default_value")
    
    assert loaded_value == "default_value"


def test_config_manager_get_all_configs(temp_config_dir):
    """Test getting all configurations."""
    manager = ConfigManager(config_dir=temp_config_dir)
    
    manager.save_config("key1", "value1")
    manager.save_config("key2", "value2")
    
    all_configs = manager.get_all_configs()
    
    assert all_configs["key1"] == "value1"
    assert all_configs["key2"] == "value2"


def test_config_manager_clear_config(temp_config_dir):
    """Test clearing a configuration value."""
    manager = ConfigManager(config_dir=temp_config_dir)
    
    manager.save_config("test_key", "test_value")
    manager.clear_config("test_key")
    
    loaded_value = manager.load_config("test_key")
    
    assert loaded_value is None


def test_config_manager_persistence(temp_config_dir):
    """Test that configuration persists across instances."""
    manager1 = ConfigManager(config_dir=temp_config_dir)
    manager1.save_config("persistent_key", "persistent_value")
    
    manager2 = ConfigManager(config_dir=temp_config_dir)
    loaded_value = manager2.load_config("persistent_key")
    
    assert loaded_value == "persistent_value"


def test_config_manager_encrypt_decrypt_credential(temp_config_dir):
    """Test encrypting and decrypting credentials."""
    manager = ConfigManager(config_dir=temp_config_dir)
    
    original_credential = "my_secret_password"
    encrypted = manager.encrypt_credential(original_credential)
    decrypted = manager.decrypt_credential(encrypted)
    
    assert decrypted == original_credential
    assert encrypted != original_credential


def test_config_manager_save_encrypted_credential(temp_config_dir):
    """Test saving and loading encrypted credentials."""
    manager = ConfigManager(config_dir=temp_config_dir)
    
    credential = "api_key_12345"
    manager.save_encrypted_credential("api_key", credential)
    
    loaded_credential = manager.load_encrypted_credential("api_key")
    
    assert loaded_credential == credential


def test_config_manager_complex_values(temp_config_dir):
    """Test saving and loading complex data structures."""
    manager = ConfigManager(config_dir=temp_config_dir)
    
    complex_value = {
        "nested": {
            "key": "value",
            "list": [1, 2, 3]
        },
        "array": ["a", "b", "c"]
    }
    
    manager.save_config("complex", complex_value)
    loaded_value = manager.load_config("complex")
    
    assert loaded_value == complex_value



# Property-Based Tests

@given(
    key=st.text(min_size=1, max_size=50),
    value=st.one_of(
        st.text(),
        st.integers(),
        st.booleans(),
        st.lists(st.text()),
        st.dictionaries(st.text(max_size=20), st.text())
    )
)
def test_config_persistence_round_trip(key, value):
    """
    **Feature: lazy-automation-platform, Property 19: Configuration Persistence Round Trip**
    
    For any configuration settings saved to storage, loading them back should produce 
    an equivalent configuration object.
    
    **Validates: Requirements 7.1, 7.2**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save configuration
        manager1 = ConfigManager(config_dir=tmpdir)
        manager1.save_config(key, value)
        
        # Load configuration in a new instance
        manager2 = ConfigManager(config_dir=tmpdir)
        loaded_value = manager2.load_config(key)
        
        # Verify round-trip equivalence
        assert loaded_value == value, f"Round-trip failed: {value} != {loaded_value}"


@given(
    key=st.text(min_size=1, max_size=50),
    initial_value=st.one_of(
        st.text(),
        st.integers(),
        st.booleans(),
        st.lists(st.text()),
        st.dictionaries(st.text(max_size=20), st.text())
    ),
    updated_value=st.one_of(
        st.text(),
        st.integers(),
        st.booleans(),
        st.lists(st.text()),
        st.dictionaries(st.text(max_size=20), st.text())
    )
)
def test_config_update_immediacy(key, initial_value, updated_value):
    """
    **Feature: lazy-automation-platform, Property 20: Configuration Update Immediacy**
    
    For any configuration modification, the system should update the stored settings 
    immediately and reflect changes in the UI.
    
    **Validates: Requirements 7.3**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ConfigManager(config_dir=tmpdir)
        
        # Save initial configuration
        manager.save_config(key, initial_value)
        
        # Verify initial value is immediately available
        assert manager.load_config(key) == initial_value
        
        # Update configuration
        manager.save_config(key, updated_value)
        
        # Verify updated value is immediately available in same instance
        assert manager.load_config(key) == updated_value
        
        # Verify updated value persists to disk immediately
        manager2 = ConfigManager(config_dir=tmpdir)
        assert manager2.load_config(key) == updated_value


@given(
    credential=st.text(min_size=1, max_size=200)
)
def test_credential_encryption(credential):
    """
    **Feature: lazy-automation-platform, Property 50: Credential Encryption**
    
    For any provided credentials (email, cloud storage, API keys), the system should 
    encrypt and store them securely.
    
    **Validates: Requirements 16.1**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ConfigManager(config_dir=tmpdir)
        
        # Encrypt the credential
        encrypted = manager.encrypt_credential(credential)
        
        # Verify encrypted credential is different from original
        assert encrypted != credential, "Encrypted credential should differ from original"
        
        # Verify encrypted credential can be decrypted back to original
        decrypted = manager.decrypt_credential(encrypted)
        assert decrypted == credential, "Decrypted credential should match original"
        
        # Verify encrypted credential can be saved and loaded
        manager.save_encrypted_credential("test_cred", credential)
        loaded_credential = manager.load_encrypted_credential("test_cred")
        assert loaded_credential == credential, "Loaded credential should match original"
        
        # Verify encrypted credential persists across instances
        manager2 = ConfigManager(config_dir=tmpdir)
        loaded_credential2 = manager2.load_encrypted_credential("test_cred")
        assert loaded_credential2 == credential, "Credential should persist across instances"
