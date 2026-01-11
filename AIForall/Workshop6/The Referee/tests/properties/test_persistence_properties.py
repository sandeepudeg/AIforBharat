"""Property-based tests for constraint persistence."""

import pytest
from hypothesis import given, strategies as st
from src.models import Constraint
from src.persistence import PersistenceManager


@given(
    data_structure=st.sampled_from(["Relational", "JSON", "Key-Value"]),
    read_write_ratio=st.integers(0, 100),
    consistency_level=st.sampled_from(["Strong", "Eventual"]),
    query_complexity=st.sampled_from(["Simple", "Moderate", "Complex"]),
    scale_gb=st.floats(0.1, 10000),
    latency_ms=st.floats(0.1, 1000),
    team_expertise=st.sampled_from(["Low", "Medium", "High"]),
    requires_persistence=st.booleans(),
)
def test_persistence_round_trip(
    data_structure,
    read_write_ratio,
    consistency_level,
    query_complexity,
    scale_gb,
    latency_ms,
    team_expertise,
    requires_persistence,
):
    """Property: Save → Load → Compare should be identical.

    This property validates that any constraint can be saved and loaded
    without losing information or changing values.
    """
    constraint = Constraint(
        data_structure=data_structure,
        read_write_ratio=read_write_ratio,
        consistency_level=consistency_level,
        query_complexity=query_complexity,
        scale_gb=scale_gb,
        latency_ms=latency_ms,
        team_expertise=team_expertise,
        requires_persistence=requires_persistence,
    )

    # Generate unique config name
    config_name = f"test_{id(constraint)}_{hash(str(constraint))}"

    try:
        # Save
        saved = PersistenceManager.save_configuration(config_name, constraint)
        assert saved, "Failed to save configuration"

        # Load
        loaded = PersistenceManager.load_configuration(config_name)
        assert loaded is not None, "Failed to load configuration"

        # Compare all fields
        assert loaded.data_structure == constraint.data_structure
        assert loaded.read_write_ratio == constraint.read_write_ratio
        assert loaded.consistency_level == constraint.consistency_level
        assert loaded.query_complexity == constraint.query_complexity
        assert loaded.scale_gb == constraint.scale_gb
        assert loaded.latency_ms == constraint.latency_ms
        assert loaded.team_expertise == constraint.team_expertise
        assert loaded.requires_persistence == constraint.requires_persistence
    finally:
        # Cleanup
        PersistenceManager.delete_configuration(config_name)


def test_persistence_list_configurations():
    """Test that list_configurations returns all saved configurations."""
    # Create test configurations
    configs_to_create = [
        ("test_config_1", Constraint(
            data_structure="Relational",
            read_write_ratio=50,
            consistency_level="Strong",
            query_complexity="Simple",
            scale_gb=10.0,
            latency_ms=5.0,
            team_expertise="Medium",
            requires_persistence=True,
        )),
        ("test_config_2", Constraint(
            data_structure="JSON",
            read_write_ratio=80,
            consistency_level="Eventual",
            query_complexity="Complex",
            scale_gb=100.0,
            latency_ms=1.0,
            team_expertise="High",
            requires_persistence=False,
        )),
    ]

    try:
        # Save configurations
        for name, constraint in configs_to_create:
            saved = PersistenceManager.save_configuration(name, constraint)
            assert saved, f"Failed to save {name}"

        # List configurations
        configs = PersistenceManager.list_configurations()

        # Verify all saved configs are in the list
        for name, _ in configs_to_create:
            assert name in configs, f"{name} not found in list"
    finally:
        # Cleanup
        for name, _ in configs_to_create:
            PersistenceManager.delete_configuration(name)


def test_persistence_delete_configuration():
    """Test that delete_configuration removes saved configurations."""
    config_name = "test_delete_config"
    constraint = Constraint(
        data_structure="Key-Value",
        read_write_ratio=90,
        consistency_level="Eventual",
        query_complexity="Simple",
        scale_gb=1.0,
        latency_ms=0.5,
        team_expertise="Low",
        requires_persistence=False,
    )

    try:
        # Save configuration
        saved = PersistenceManager.save_configuration(config_name, constraint)
        assert saved, "Failed to save configuration"

        # Verify it exists
        loaded = PersistenceManager.load_configuration(config_name)
        assert loaded is not None, "Configuration not found after save"

        # Delete configuration
        deleted = PersistenceManager.delete_configuration(config_name)
        assert deleted, "Failed to delete configuration"

        # Verify it's gone
        loaded = PersistenceManager.load_configuration(config_name)
        assert loaded is None, "Configuration still exists after delete"
    finally:
        # Cleanup (in case test fails)
        PersistenceManager.delete_configuration(config_name)


def test_persistence_load_nonexistent():
    """Test that loading a nonexistent configuration returns None."""
    result = PersistenceManager.load_configuration("nonexistent_config_xyz")
    assert result is None, "Should return None for nonexistent configuration"


def test_persistence_delete_nonexistent():
    """Test that deleting a nonexistent configuration returns False."""
    result = PersistenceManager.delete_configuration("nonexistent_config_xyz")
    assert result is False, "Should return False for nonexistent configuration"


def test_persistence_invalid_name():
    """Test that invalid names are handled gracefully."""
    constraint = Constraint(
        data_structure="Relational",
        read_write_ratio=50,
        consistency_level="Strong",
        query_complexity="Simple",
        scale_gb=10.0,
        latency_ms=5.0,
        team_expertise="Medium",
        requires_persistence=True,
    )

    # Test with empty name
    result = PersistenceManager.save_configuration("", constraint)
    assert result is False, "Should reject empty name"

    # Test with None name
    result = PersistenceManager.save_configuration(None, constraint)
    assert result is False, "Should reject None name"


def test_persistence_special_characters_in_name():
    """Test that special characters in names are handled safely."""
    config_name = "test_config_!@#$%^&*()"
    constraint = Constraint(
        data_structure="Relational",
        read_write_ratio=50,
        consistency_level="Strong",
        query_complexity="Simple",
        scale_gb=10.0,
        latency_ms=5.0,
        team_expertise="Medium",
        requires_persistence=True,
    )

    try:
        # Save with special characters
        saved = PersistenceManager.save_configuration(config_name, constraint)
        assert saved, "Failed to save configuration with special characters"

        # Load it back
        loaded = PersistenceManager.load_configuration(config_name)
        assert loaded is not None, "Failed to load configuration with special characters"
        assert loaded.data_structure == constraint.data_structure
    finally:
        # Cleanup
        PersistenceManager.delete_configuration(config_name)
