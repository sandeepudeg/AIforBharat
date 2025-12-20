"""Tests for data integrity and concurrent access handling.

Feature: supply-chain-optimizer, Property 33: Data Integrity
Validates: Requirements 8.3

Feature: supply-chain-optimizer, Property 34: Concurrent Access Safety
Validates: Requirements 8.4
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from hypothesis import given, strategies as st, assume
from sqlalchemy.exc import SQLAlchemyError

from src.database.integrity import (
    VersionedData,
    OptimisticLockManager,
    TransactionManager,
    DataValidator,
    ChecksumManager,
    ConflictResolutionStrategy,
    get_optimistic_lock_manager,
)


class TestVersionedData:
    """Test VersionedData wrapper for optimistic locking."""
    
    def test_versioned_data_initialization(self):
        """Test VersionedData initialization with default values."""
        data = {"sku": "PROD-001", "quantity": 100}
        versioned = VersionedData(data=data)
        
        assert versioned.data == data
        assert versioned.version == 1
        assert versioned.checksum != ""
        assert isinstance(versioned.last_modified, datetime)
    
    def test_checksum_calculation(self):
        """Test checksum calculation for data integrity."""
        data = {"sku": "PROD-001", "quantity": 100}
        versioned = VersionedData(data=data)
        
        # Same data should produce same checksum
        checksum1 = versioned.calculate_checksum()
        checksum2 = versioned.calculate_checksum()
        assert checksum1 == checksum2
        
        # Different data should produce different checksum
        versioned.data["quantity"] = 200
        checksum3 = versioned.calculate_checksum()
        assert checksum3 != checksum1
    
    def test_verify_integrity(self):
        """Test data integrity verification."""
        data = {"sku": "PROD-001", "quantity": 100}
        versioned = VersionedData(data=data)
        
        # Integrity should be valid initially
        assert versioned.verify_integrity() is True
        
        # Modify data without updating checksum
        versioned.data["quantity"] = 200
        assert versioned.verify_integrity() is False
        
        # Recalculate checksum
        versioned.checksum = versioned.calculate_checksum()
        assert versioned.verify_integrity() is True
    
    def test_increment_version(self):
        """Test version incrementing."""
        data = {"sku": "PROD-001", "quantity": 100}
        versioned = VersionedData(data=data)
        
        initial_version = versioned.version
        initial_modified = versioned.last_modified
        
        versioned.increment_version()
        
        assert versioned.version == initial_version + 1
        assert versioned.last_modified > initial_modified


class TestOptimisticLockManager:
    """Test OptimisticLockManager for concurrent access control."""
    
    def test_acquire_lock(self):
        """Test acquiring an optimistic lock."""
        manager = OptimisticLockManager()
        data = {"sku": "PROD-001", "quantity": 100}
        
        versioned = manager.acquire_lock("resource-1", data)
        
        assert versioned.data == data
        assert versioned.version == 1
    
    def test_release_lock(self):
        """Test releasing an optimistic lock."""
        manager = OptimisticLockManager()
        data = {"sku": "PROD-001", "quantity": 100}
        
        manager.acquire_lock("resource-1", data)
        manager.release_lock("resource-1")
        
        # Acquiring again should create new lock
        versioned = manager.acquire_lock("resource-1", data)
        assert versioned.version == 1
    
    def test_validate_version_success(self):
        """Test successful version validation."""
        manager = OptimisticLockManager()
        data = {"sku": "PROD-001", "quantity": 100}
        
        manager.acquire_lock("resource-1", data)
        
        # Version should match
        assert manager.validate_version("resource-1", 1) is True
    
    def test_validate_version_failure(self):
        """Test failed version validation."""
        manager = OptimisticLockManager()
        data = {"sku": "PROD-001", "quantity": 100}
        
        manager.acquire_lock("resource-1", data)
        
        # Wrong version should not match
        assert manager.validate_version("resource-1", 2) is False
    
    def test_update_with_lock_success(self):
        """Test successful update with optimistic locking."""
        manager = OptimisticLockManager()
        data = {"sku": "PROD-001", "quantity": 100}
        
        manager.acquire_lock("resource-1", data)
        
        new_data = {"sku": "PROD-001", "quantity": 150}
        success, error = manager.update_with_lock("resource-1", 1, new_data)
        
        assert success is True
        assert error is None
        assert manager._locks["resource-1"].data == new_data
        assert manager._locks["resource-1"].version == 2
    
    def test_update_with_lock_version_conflict_abort(self):
        """Test version conflict with ABORT strategy."""
        manager = OptimisticLockManager()
        data = {"sku": "PROD-001", "quantity": 100}
        
        manager.acquire_lock("resource-1", data)
        
        new_data = {"sku": "PROD-001", "quantity": 150}
        success, error = manager.update_with_lock(
            "resource-1",
            2,  # Wrong version
            new_data,
            strategy=ConflictResolutionStrategy.ABORT
        )
        
        assert success is False
        assert error is not None
        assert "Version conflict" in error
    
    def test_update_with_lock_last_write_wins(self):
        """Test LAST_WRITE_WINS conflict resolution strategy."""
        manager = OptimisticLockManager()
        data = {"sku": "PROD-001", "quantity": 100}
        
        manager.acquire_lock("resource-1", data)
        
        new_data = {"sku": "PROD-001", "quantity": 150}
        success, error = manager.update_with_lock(
            "resource-1",
            2,  # Wrong version
            new_data,
            strategy=ConflictResolutionStrategy.LAST_WRITE_WINS
        )
        
        assert success is True
        assert error is None
        assert manager._locks["resource-1"].data == new_data
        assert manager._locks["resource-1"].version == 2
    
    def test_update_with_lock_first_write_wins(self):
        """Test FIRST_WRITE_WINS conflict resolution strategy."""
        manager = OptimisticLockManager()
        data = {"sku": "PROD-001", "quantity": 100}
        
        manager.acquire_lock("resource-1", data)
        
        new_data = {"sku": "PROD-001", "quantity": 150}
        success, error = manager.update_with_lock(
            "resource-1",
            2,  # Wrong version
            new_data,
            strategy=ConflictResolutionStrategy.FIRST_WRITE_WINS
        )
        
        assert success is False
        assert error is not None
        assert "First write wins" in error
    
    def test_update_with_lock_merge_strategy(self):
        """Test MERGE conflict resolution strategy."""
        manager = OptimisticLockManager()
        data = {"sku": "PROD-001", "quantity": 100, "category": "Electronics"}
        
        manager.acquire_lock("resource-1", data)
        
        new_data = {"quantity": 150, "supplier": "SUP-001"}
        success, error = manager.update_with_lock(
            "resource-1",
            2,  # Wrong version
            new_data,
            strategy=ConflictResolutionStrategy.MERGE
        )
        
        assert success is True
        assert error is None
        # Merged data should contain both old and new values
        merged = manager._locks["resource-1"].data
        assert merged["quantity"] == 150  # New value
        assert merged["supplier"] == "SUP-001"  # New value
        assert merged["sku"] == "PROD-001"  # Old value preserved


class TestTransactionManager:
    """Test TransactionManager for multi-step operations."""
    
    def test_begin_transaction(self):
        """Test beginning a transaction."""
        mock_session = MagicMock()
        manager = TransactionManager(mock_session)
        
        manager.begin_transaction("txn-1")
        
        assert "txn-1" in manager._transaction_stack
    
    def test_commit_transaction_success(self):
        """Test successful transaction commit."""
        mock_session = MagicMock()
        manager = TransactionManager(mock_session)
        
        manager.begin_transaction("txn-1")
        success = manager.commit_transaction("txn-1")
        
        assert success is True
        assert "txn-1" not in manager._transaction_stack
        mock_session.commit.assert_called_once()
    
    def test_rollback_transaction_success(self):
        """Test successful transaction rollback."""
        mock_session = MagicMock()
        manager = TransactionManager(mock_session)
        
        manager.begin_transaction("txn-1")
        success = manager.rollback_transaction("txn-1")
        
        assert success is True
        assert "txn-1" not in manager._transaction_stack
        mock_session.rollback.assert_called_once()
    
    def test_execute_transaction_success(self):
        """Test successful multi-step transaction execution."""
        mock_session = MagicMock()
        manager = TransactionManager(mock_session)
        
        operation1_called = False
        operation2_called = False
        
        def operation1():
            nonlocal operation1_called
            operation1_called = True
        
        def operation2():
            nonlocal operation2_called
            operation2_called = True
        
        success, error = manager.execute_transaction("txn-1", [operation1, operation2])
        
        assert success is True
        assert error is None
        assert operation1_called is True
        assert operation2_called is True
        mock_session.commit.assert_called_once()
    
    def test_execute_transaction_failure(self):
        """Test failed transaction execution with rollback."""
        mock_session = MagicMock()
        manager = TransactionManager(mock_session)
        
        def failing_operation():
            raise ValueError("Operation failed")
        
        success, error = manager.execute_transaction("txn-1", [failing_operation])
        
        assert success is False
        assert error is not None
        assert "Operation failed" in error
        mock_session.rollback.assert_called_once()


class TestDataValidator:
    """Test DataValidator for data integrity validation."""
    
    def test_validate_referential_integrity_success(self):
        """Test successful referential integrity validation."""
        data = {"sku": "PROD-001", "quantity": 100, "warehouse": "WH-001"}
        required_fields = ["sku", "quantity"]
        
        valid, error = DataValidator.validate_referential_integrity(data, required_fields)
        
        assert valid is True
        assert error is None
    
    def test_validate_referential_integrity_missing_fields(self):
        """Test referential integrity validation with missing fields."""
        data = {"sku": "PROD-001"}
        required_fields = ["sku", "quantity", "warehouse"]
        
        valid, error = DataValidator.validate_referential_integrity(data, required_fields)
        
        assert valid is False
        assert error is not None
        assert "quantity" in error
        assert "warehouse" in error
    
    def test_validate_data_types_success(self):
        """Test successful data type validation."""
        data = {"sku": "PROD-001", "quantity": 100, "price": 10.50}
        type_constraints = {"sku": str, "quantity": int, "price": float}
        
        valid, error = DataValidator.validate_data_types(data, type_constraints)
        
        assert valid is True
        assert error is None
    
    def test_validate_data_types_failure(self):
        """Test data type validation failure."""
        data = {"sku": "PROD-001", "quantity": "100"}  # Wrong type
        type_constraints = {"sku": str, "quantity": int}
        
        valid, error = DataValidator.validate_data_types(data, type_constraints)
        
        assert valid is False
        assert error is not None
        assert "quantity" in error
    
    def test_validate_value_ranges_success(self):
        """Test successful value range validation."""
        data = {"quantity": 100, "price": 10.50}
        range_constraints = {"quantity": (0, 1000), "price": (0.0, 100.0)}
        
        valid, error = DataValidator.validate_value_ranges(data, range_constraints)
        
        assert valid is True
        assert error is None
    
    def test_validate_value_ranges_failure(self):
        """Test value range validation failure."""
        data = {"quantity": 1500}  # Outside range
        range_constraints = {"quantity": (0, 1000)}
        
        valid, error = DataValidator.validate_value_ranges(data, range_constraints)
        
        assert valid is False
        assert error is not None
        assert "1500" in error


class TestChecksumManager:
    """Test ChecksumManager for data integrity verification."""
    
    def test_calculate_checksum(self):
        """Test checksum calculation."""
        data = {"sku": "PROD-001", "quantity": 100}
        
        checksum = ChecksumManager.calculate_checksum(data)
        
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 produces 64 hex characters
    
    def test_checksum_consistency(self):
        """Test that same data produces same checksum."""
        data = {"sku": "PROD-001", "quantity": 100}
        
        checksum1 = ChecksumManager.calculate_checksum(data)
        checksum2 = ChecksumManager.calculate_checksum(data)
        
        assert checksum1 == checksum2
    
    def test_checksum_difference(self):
        """Test that different data produces different checksums."""
        data1 = {"sku": "PROD-001", "quantity": 100}
        data2 = {"sku": "PROD-001", "quantity": 200}
        
        checksum1 = ChecksumManager.calculate_checksum(data1)
        checksum2 = ChecksumManager.calculate_checksum(data2)
        
        assert checksum1 != checksum2
    
    def test_verify_checksum_success(self):
        """Test successful checksum verification."""
        data = {"sku": "PROD-001", "quantity": 100}
        checksum = ChecksumManager.calculate_checksum(data)
        
        valid = ChecksumManager.verify_checksum(data, checksum)
        
        assert valid is True
    
    def test_verify_checksum_failure(self):
        """Test failed checksum verification."""
        data = {"sku": "PROD-001", "quantity": 100}
        wrong_checksum = "0" * 64
        
        valid = ChecksumManager.verify_checksum(data, wrong_checksum)
        
        assert valid is False
    
    def test_calculate_batch_checksum(self):
        """Test batch checksum calculation."""
        data_list = [
            {"sku": "PROD-001", "quantity": 100},
            {"sku": "PROD-002", "quantity": 200},
        ]
        
        checksum = ChecksumManager.calculate_batch_checksum(data_list)
        
        assert isinstance(checksum, str)
        assert len(checksum) == 64


class TestConcurrentAccessSafety:
    """Test concurrent access safety with multiple operations.
    
    Feature: supply-chain-optimizer, Property 34: Concurrent Access Safety
    Validates: Requirements 8.4
    """
    
    def test_concurrent_updates_with_optimistic_locking(self):
        """Test that concurrent updates are handled safely with optimistic locking.
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        manager = OptimisticLockManager()
        resource_id = "inventory-1"
        initial_data = {"sku": "PROD-001", "quantity": 100}
        
        # Simulate two concurrent readers - capture their versions at read time
        versioned1 = manager.acquire_lock(resource_id, initial_data)
        version_at_read1 = versioned1.version  # Reader 1 reads version 1
        
        # First writer updates successfully
        new_data1 = {"sku": "PROD-001", "quantity": 150}
        success1, _ = manager.update_with_lock(
            resource_id,
            version_at_read1,
            new_data1,
            strategy=ConflictResolutionStrategy.ABORT
        )
        assert success1 is True
        
        # Now version should be 2
        versioned_after_update = manager._locks[resource_id]
        version_at_read2 = 1  # Reader 2 read the old version before update
        
        # Second writer should detect version conflict
        new_data2 = {"sku": "PROD-001", "quantity": 200}
        success2, error2 = manager.update_with_lock(
            resource_id,
            version_at_read2,
            new_data2,
            strategy=ConflictResolutionStrategy.ABORT
        )
        assert success2 is False
        assert error2 is not None
    
    def test_transaction_isolation(self):
        """Test transaction isolation for concurrent operations.
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        mock_session = MagicMock()
        manager = TransactionManager(mock_session)
        
        # Simulate two concurrent transactions
        manager.begin_transaction("txn-1")
        manager.begin_transaction("txn-2")
        
        assert len(manager._transaction_stack) == 2
        
        # Commit first transaction
        manager.commit_transaction("txn-1")
        assert len(manager._transaction_stack) == 1
        
        # Commit second transaction
        manager.commit_transaction("txn-2")
        assert len(manager._transaction_stack) == 0
    
    def test_data_integrity_with_concurrent_modifications(self):
        """Test data integrity is maintained during concurrent modifications.
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        manager = OptimisticLockManager()
        resource_id = "product-1"
        initial_data = {"sku": "PROD-001", "quantity": 100, "price": 10.50}
        
        # Acquire lock and verify initial integrity
        versioned = manager.acquire_lock(resource_id, initial_data)
        assert versioned.verify_integrity() is True
        
        # Update data
        new_data = {"sku": "PROD-001", "quantity": 150, "price": 10.50}
        success, _ = manager.update_with_lock(resource_id, 1, new_data)
        assert success is True
        
        # Verify integrity after update
        updated_versioned = manager._locks[resource_id]
        assert updated_versioned.verify_integrity() is True
        assert updated_versioned.version == 2


class TestDataIntegrity:
    """Test data integrity constraints and validation.
    
    Feature: supply-chain-optimizer, Property 33: Data Integrity
    Validates: Requirements 8.3
    """
    
    def test_referential_integrity_enforcement(self):
        """Test that referential integrity is enforced.
        
        Property: *For any* stored data, the system should maintain referential 
        integrity (no orphaned records) and prevent data corruption or loss.
        """
        # Test that required fields are enforced
        data = {"sku": "PROD-001"}  # Missing quantity
        required_fields = ["sku", "quantity", "warehouse"]
        
        valid, error = DataValidator.validate_referential_integrity(data, required_fields)
        
        assert valid is False
        assert error is not None
    
    def test_data_corruption_detection(self):
        """Test that data corruption is detected via checksums.
        
        Property: *For any* stored data, the system should maintain referential 
        integrity (no orphaned records) and prevent data corruption or loss.
        """
        data = {"sku": "PROD-001", "quantity": 100}
        versioned = VersionedData(data=data)
        
        # Verify initial integrity
        assert versioned.verify_integrity() is True
        
        # Simulate data corruption
        versioned.data["quantity"] = 200
        
        # Corruption should be detected
        assert versioned.verify_integrity() is False
    
    def test_data_validation_prevents_invalid_states(self):
        """Test that data validation prevents invalid states.
        
        Property: *For any* stored data, the system should maintain referential 
        integrity (no orphaned records) and prevent data corruption or loss.
        """
        # Test type validation
        data = {"quantity": "not_a_number"}
        type_constraints = {"quantity": int}
        
        valid, error = DataValidator.validate_data_types(data, type_constraints)
        
        assert valid is False
        assert error is not None
        
        # Test range validation
        data = {"quantity": -100}
        range_constraints = {"quantity": (0, 10000)}
        
        valid, error = DataValidator.validate_value_ranges(data, range_constraints)
        
        assert valid is False
        assert error is not None


def test_get_optimistic_lock_manager():
    """Test getting the global optimistic lock manager instance."""
    manager1 = get_optimistic_lock_manager()
    manager2 = get_optimistic_lock_manager()
    
    # Should return same instance
    assert manager1 is manager2


# Property-Based Tests

@given(
    sku=st.text(min_size=1, max_size=20),
    quantity=st.integers(min_value=0, max_value=100000),
    price=st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False),
    warehouse_id=st.text(min_size=1, max_size=20)
)
def test_property_data_integrity_round_trip(sku, quantity, price, warehouse_id):
    """Property test for data integrity round trip.
    
    Feature: supply-chain-optimizer, Property 33: Data Integrity
    Validates: Requirements 8.3
    
    Property: *For any* stored data, the system should maintain referential 
    integrity (no orphaned records) and prevent data corruption or loss.
    
    This property tests that:
    1. Data can be stored with integrity checks
    2. Data can be retrieved without corruption
    3. Checksums verify data integrity
    4. Version tracking maintains consistency
    """
    # Create inventory data
    inventory_data = {
        "sku": sku,
        "quantity": quantity,
        "price": price,
        "warehouse_id": warehouse_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Store data with versioning
    manager = OptimisticLockManager()
    resource_id = f"inventory-{sku}-{warehouse_id}"
    versioned = manager.acquire_lock(resource_id, inventory_data)
    
    # Verify initial integrity
    assert versioned.verify_integrity() is True, "Initial data should have valid integrity"
    assert versioned.version == 1, "Initial version should be 1"
    
    # Verify checksum is consistent
    checksum1 = versioned.calculate_checksum()
    checksum2 = versioned.calculate_checksum()
    assert checksum1 == checksum2, "Checksums should be consistent for same data"
    
    # Verify data is not corrupted
    assert versioned.data["sku"] == sku, "SKU should be preserved"
    assert versioned.data["quantity"] == quantity, "Quantity should be preserved"
    assert versioned.data["price"] == price, "Price should be preserved"
    assert versioned.data["warehouse_id"] == warehouse_id, "Warehouse ID should be preserved"
    
    # Update data and verify version increments
    updated_data = inventory_data.copy()
    updated_data["quantity"] = quantity + 10
    
    success, error = manager.update_with_lock(resource_id, 1, updated_data)
    assert success is True, "Update should succeed with correct version"
    assert error is None, "No error should occur on successful update"
    
    # Verify version incremented
    updated_versioned = manager._locks[resource_id]
    assert updated_versioned.version == 2, "Version should increment after update"
    assert updated_versioned.verify_integrity() is True, "Updated data should maintain integrity"
    
    # Verify new data is stored correctly
    assert updated_versioned.data["quantity"] == quantity + 10, "Updated quantity should be stored"
    assert updated_versioned.data["sku"] == sku, "SKU should remain unchanged"


@given(
    data_dict=st.dictionaries(
        keys=st.text(min_size=1, max_size=10),
        values=st.one_of(
            st.integers(min_value=0, max_value=1000),
            st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
            st.text(max_size=20)
        ),
        min_size=1,
        max_size=5
    )
)
def test_property_checksum_consistency(data_dict):
    """Property test for checksum consistency.
    
    Feature: supply-chain-optimizer, Property 33: Data Integrity
    Validates: Requirements 8.3
    
    Property: *For any* stored data, the system should maintain referential 
    integrity (no orphaned records) and prevent data corruption or loss.
    
    This property tests that:
    1. Same data always produces same checksum
    2. Different data produces different checksums
    3. Checksums can verify data integrity
    """
    # Calculate checksum multiple times
    checksum1 = ChecksumManager.calculate_checksum(data_dict)
    checksum2 = ChecksumManager.calculate_checksum(data_dict)
    checksum3 = ChecksumManager.calculate_checksum(data_dict)
    
    # All checksums should be identical
    assert checksum1 == checksum2, "Checksums should be consistent"
    assert checksum2 == checksum3, "Checksums should be consistent"
    
    # Verify checksum is valid
    assert ChecksumManager.verify_checksum(data_dict, checksum1) is True, \
        "Checksum verification should succeed for original data"
    
    # Modify data and verify checksum changes
    modified_dict = data_dict.copy()
    # Add a new key-value pair
    modified_dict["_modified"] = "true"
    
    checksum_modified = ChecksumManager.calculate_checksum(modified_dict)
    assert checksum_modified != checksum1, "Modified data should have different checksum"
    
    # Verify checksum fails for modified data
    assert ChecksumManager.verify_checksum(data_dict, checksum_modified) is False, \
        "Checksum verification should fail for modified data"


@given(
    required_fields=st.lists(
        st.text(min_size=1, max_size=20),
        min_size=1,
        max_size=5,
        unique=True
    )
)
def test_property_referential_integrity_validation(required_fields):
    """Property test for referential integrity validation.
    
    Feature: supply-chain-optimizer, Property 33: Data Integrity
    Validates: Requirements 8.3
    
    Property: *For any* stored data, the system should maintain referential 
    integrity (no orphaned records) and prevent data corruption or loss.
    
    This property tests that:
    1. Data with all required fields passes validation
    2. Data missing required fields fails validation
    3. Validation errors identify missing fields
    """
    # Create data with all required fields
    complete_data = {field: f"value_{field}" for field in required_fields}
    
    # Validation should pass
    valid, error = DataValidator.validate_referential_integrity(complete_data, required_fields)
    assert valid is True, "Data with all required fields should pass validation"
    assert error is None, "No error should occur for valid data"
    
    # Remove one field and test
    if len(required_fields) > 0:
        incomplete_data = complete_data.copy()
        missing_field = required_fields[0]
        del incomplete_data[missing_field]
        
        # Validation should fail
        valid, error = DataValidator.validate_referential_integrity(incomplete_data, required_fields)
        assert valid is False, "Data missing required fields should fail validation"
        assert error is not None, "Error should be provided for missing fields"
        assert missing_field in error, "Error should identify the missing field"


@given(
    quantity=st.integers(min_value=-1000, max_value=100000),
    price=st.floats(min_value=-1000.0, max_value=10000.0, allow_nan=False, allow_infinity=False),
    lead_time=st.integers(min_value=-100, max_value=365)
)
def test_property_data_type_validation(quantity, price, lead_time):
    """Property test for data type validation.
    
    Feature: supply-chain-optimizer, Property 33: Data Integrity
    Validates: Requirements 8.3
    
    Property: *For any* stored data, the system should maintain referential 
    integrity (no orphaned records) and prevent data corruption or loss.
    
    This property tests that:
    1. Data with correct types passes validation
    2. Data with incorrect types fails validation
    3. Type validation prevents invalid states
    """
    data = {
        "quantity": quantity,
        "price": price,
        "lead_time": lead_time
    }
    
    type_constraints = {
        "quantity": int,
        "price": float,
        "lead_time": int
    }
    
    # Validation should pass (types are correct)
    valid, error = DataValidator.validate_data_types(data, type_constraints)
    assert valid is True, "Data with correct types should pass validation"
    assert error is None, "No error should occur for valid types"
    
    # Test with wrong type
    wrong_type_data = {
        "quantity": "not_a_number",
        "price": price,
        "lead_time": lead_time
    }
    
    valid, error = DataValidator.validate_data_types(wrong_type_data, type_constraints)
    assert valid is False, "Data with wrong types should fail validation"
    assert error is not None, "Error should be provided for type mismatch"


@given(
    quantity=st.integers(min_value=0, max_value=100000),
    price=st.floats(min_value=0.01, max_value=10000.0, allow_nan=False, allow_infinity=False)
)
def test_property_value_range_validation(quantity, price):
    """Property test for value range validation.
    
    Feature: supply-chain-optimizer, Property 33: Data Integrity
    Validates: Requirements 8.3
    
    Property: *For any* stored data, the system should maintain referential 
    integrity (no orphaned records) and prevent data corruption or loss.
    
    This property tests that:
    1. Values within valid ranges pass validation
    2. Values outside valid ranges fail validation
    3. Range validation prevents invalid states
    """
    data = {
        "quantity": quantity,
        "price": price
    }
    
    range_constraints = {
        "quantity": (0, 100000),
        "price": (0.01, 10000.0)
    }
    
    # Validation should pass (values are within ranges)
    valid, error = DataValidator.validate_value_ranges(data, range_constraints)
    assert valid is True, "Values within valid ranges should pass validation"
    assert error is None, "No error should occur for valid ranges"
    
    # Test with value outside range
    out_of_range_data = {
        "quantity": 150000,  # Outside range
        "price": price
    }
    
    valid, error = DataValidator.validate_value_ranges(out_of_range_data, range_constraints)
    assert valid is False, "Values outside valid ranges should fail validation"
    assert error is not None, "Error should be provided for out-of-range values"


class TestTransactionRollbackOnErrors:
    """Test transaction rollback behavior when errors occur.
    
    Feature: supply-chain-optimizer, Property 34: Concurrent Access Safety
    Validates: Requirements 8.4
    """
    
    def test_transaction_rollback_on_operation_error(self):
        """Test that transaction rolls back when an operation fails.
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        mock_session = MagicMock()
        manager = TransactionManager(mock_session)
        
        operation_executed = False
        
        def failing_operation():
            nonlocal operation_executed
            operation_executed = True
            raise RuntimeError("Operation failed")
        
        success, error = manager.execute_transaction("txn-1", [failing_operation])
        
        assert success is False
        assert error is not None
        assert "Operation failed" in error
        assert operation_executed is True
        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()
    
    def test_transaction_rollback_on_partial_failure(self):
        """Test that transaction rolls back when second operation fails.
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        mock_session = MagicMock()
        manager = TransactionManager(mock_session)
        
        operation1_executed = False
        operation2_executed = False
        
        def operation1():
            nonlocal operation1_executed
            operation1_executed = True
        
        def operation2():
            nonlocal operation2_executed
            operation2_executed = True
            raise ValueError("Second operation failed")
        
        success, error = manager.execute_transaction("txn-1", [operation1, operation2])
        
        assert success is False
        assert error is not None
        assert "Second operation failed" in error
        assert operation1_executed is True
        assert operation2_executed is True
        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()
    
    def test_transaction_rollback_on_database_error(self):
        """Test that transaction rolls back on database errors.
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        mock_session = MagicMock()
        mock_session.commit.side_effect = SQLAlchemyError("Database connection lost")
        manager = TransactionManager(mock_session)
        
        def operation():
            pass
        
        success, error = manager.execute_transaction("txn-1", [operation])
        
        assert success is False
        assert error is not None
        assert "Failed to commit transaction" in error or "Database connection lost" in error
        mock_session.rollback.assert_called_once()
    
    def test_transaction_rollback_idempotent(self):
        """Test that rolling back a transaction multiple times is safe.
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        mock_session = MagicMock()
        manager = TransactionManager(mock_session)
        
        manager.begin_transaction("txn-1")
        
        # First rollback should succeed
        success1 = manager.rollback_transaction("txn-1")
        assert success1 is True
        
        # Second rollback should fail gracefully (transaction not in stack)
        success2 = manager.rollback_transaction("txn-1")
        assert success2 is False


class TestDataValidationScenarios:
    """Test data validation in various scenarios.
    
    Feature: supply-chain-optimizer, Property 33: Data Integrity
    Validates: Requirements 8.3
    """
    
    def test_validate_empty_data_with_required_fields(self):
        """Test validation of empty data against required fields.
        
        Property: *For any* stored data, the system should maintain referential 
        integrity (no orphaned records) and prevent data corruption or loss.
        """
        data = {}
        required_fields = ["sku", "quantity", "warehouse"]
        
        valid, error = DataValidator.validate_referential_integrity(data, required_fields)
        
        assert valid is False
        assert error is not None
        assert "sku" in error
        assert "quantity" in error
        assert "warehouse" in error
    
    def test_validate_partial_data_with_required_fields(self):
        """Test validation of partial data against required fields.
        
        Property: *For any* stored data, the system should maintain referential 
        integrity (no orphaned records) and prevent data corruption or loss.
        """
        data = {"sku": "PROD-001"}
        required_fields = ["sku", "quantity", "warehouse"]
        
        valid, error = DataValidator.validate_referential_integrity(data, required_fields)
        
        assert valid is False
        assert error is not None
        assert "quantity" in error
        assert "warehouse" in error
        assert "sku" not in error  # sku is present
    
    def test_validate_extra_fields_with_required_fields(self):
        """Test validation allows extra fields beyond required fields.
        
        Property: *For any* stored data, the system should maintain referential 
        integrity (no orphaned records) and prevent data corruption or loss.
        """
        data = {
            "sku": "PROD-001",
            "quantity": 100,
            "warehouse": "WH-001",
            "extra_field": "extra_value"
        }
        required_fields = ["sku", "quantity", "warehouse"]
        
        valid, error = DataValidator.validate_referential_integrity(data, required_fields)
        
        assert valid is True
        assert error is None
    
    def test_validate_mixed_types_with_constraints(self):
        """Test validation with mixed data types.
        
        Property: *For any* stored data, the system should maintain referential 
        integrity (no orphaned records) and prevent data corruption or loss.
        """
        data = {
            "sku": "PROD-001",
            "quantity": 100,
            "price": 10.50,
            "active": True
        }
        type_constraints = {
            "sku": str,
            "quantity": int,
            "price": float,
            "active": bool
        }
        
        valid, error = DataValidator.validate_data_types(data, type_constraints)
        
        assert valid is True
        assert error is None
    
    def test_validate_boundary_values(self):
        """Test validation with boundary values.
        
        Property: *For any* stored data, the system should maintain referential 
        integrity (no orphaned records) and prevent data corruption or loss.
        """
        data = {
            "quantity": 0,  # Minimum boundary
            "price": 10000.0  # Maximum boundary
        }
        range_constraints = {
            "quantity": (0, 100000),
            "price": (0.01, 10000.0)
        }
        
        valid, error = DataValidator.validate_value_ranges(data, range_constraints)
        
        assert valid is True
        assert error is None
    
    def test_validate_just_outside_boundaries(self):
        """Test validation with values just outside boundaries.
        
        Property: *For any* stored data, the system should maintain referential 
        integrity (no orphaned records) and prevent data corruption or loss.
        """
        # Test minimum boundary violation
        data1 = {"quantity": -1}
        range_constraints = {"quantity": (0, 100000)}
        
        valid1, error1 = DataValidator.validate_value_ranges(data1, range_constraints)
        assert valid1 is False
        assert error1 is not None
        
        # Test maximum boundary violation
        data2 = {"price": 10000.01}
        range_constraints2 = {"price": (0.01, 10000.0)}
        
        valid2, error2 = DataValidator.validate_value_ranges(data2, range_constraints2)
        assert valid2 is False
        assert error2 is not None


class TestConcurrentAccessEdgeCases:
    """Test edge cases in concurrent access scenarios.
    
    Feature: supply-chain-optimizer, Property 34: Concurrent Access Safety
    Validates: Requirements 8.4
    """
    
    def test_concurrent_access_to_nonexistent_resource(self):
        """Test concurrent access to a resource that doesn't exist.
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        manager = OptimisticLockManager()
        
        # Try to update a resource that was never acquired
        new_data = {"sku": "PROD-001", "quantity": 100}
        success, error = manager.update_with_lock("nonexistent", 1, new_data)
        
        assert success is False
        assert error is not None
        assert "not found" in error
    
    def test_concurrent_access_with_version_zero(self):
        """Test concurrent access with version zero (invalid).
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        manager = OptimisticLockManager()
        data = {"sku": "PROD-001", "quantity": 100}
        
        manager.acquire_lock("resource-1", data)
        
        # Try to update with version 0 (invalid)
        new_data = {"sku": "PROD-001", "quantity": 150}
        success, error = manager.update_with_lock("resource-1", 0, new_data)
        
        assert success is False
        assert error is not None
    
    def test_concurrent_access_with_negative_version(self):
        """Test concurrent access with negative version (invalid).
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        manager = OptimisticLockManager()
        data = {"sku": "PROD-001", "quantity": 100}
        
        manager.acquire_lock("resource-1", data)
        
        # Try to update with negative version
        new_data = {"sku": "PROD-001", "quantity": 150}
        success, error = manager.update_with_lock("resource-1", -1, new_data)
        
        assert success is False
        assert error is not None
    
    def test_multiple_sequential_updates_maintain_consistency(self):
        """Test that multiple sequential updates maintain data consistency.
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        manager = OptimisticLockManager()
        resource_id = "inventory-1"
        
        # Initial data
        data = {"sku": "PROD-001", "quantity": 100}
        versioned = manager.acquire_lock(resource_id, data)
        
        # First update
        data1 = {"sku": "PROD-001", "quantity": 150}
        success1, _ = manager.update_with_lock(resource_id, 1, data1)
        assert success1 is True
        assert manager._locks[resource_id].version == 2
        
        # Second update
        data2 = {"sku": "PROD-001", "quantity": 200}
        success2, _ = manager.update_with_lock(resource_id, 2, data2)
        assert success2 is True
        assert manager._locks[resource_id].version == 3
        
        # Third update
        data3 = {"sku": "PROD-001", "quantity": 250}
        success3, _ = manager.update_with_lock(resource_id, 3, data3)
        assert success3 is True
        assert manager._locks[resource_id].version == 4
        
        # Verify final data
        assert manager._locks[resource_id].data["quantity"] == 250
        assert manager._locks[resource_id].verify_integrity() is True
    
    def test_release_and_reacquire_lock(self):
        """Test releasing and reacquiring a lock.
        
        Property: *For any* concurrent access to the same data by multiple agents, 
        the system should prevent data conflicts and maintain consistency through 
        proper locking or versioning.
        """
        manager = OptimisticLockManager()
        resource_id = "inventory-1"
        data = {"sku": "PROD-001", "quantity": 100}
        
        # Acquire lock
        versioned1 = manager.acquire_lock(resource_id, data)
        assert versioned1.version == 1
        
        # Release lock
        manager.release_lock(resource_id)
        
        # Reacquire lock - should create new lock with version 1
        versioned2 = manager.acquire_lock(resource_id, data)
        assert versioned2.version == 1


@given(
    sku=st.text(min_size=1, max_size=20),
    initial_quantity=st.integers(min_value=0, max_value=10000),
    update1_quantity=st.integers(min_value=0, max_value=10000),
    update2_quantity=st.integers(min_value=0, max_value=10000),
    update3_quantity=st.integers(min_value=0, max_value=10000)
)
def test_property_concurrent_access_safety(sku, initial_quantity, update1_quantity, update2_quantity, update3_quantity):
    """Property test for concurrent access safety with optimistic locking.
    
    Feature: supply-chain-optimizer, Property 34: Concurrent Access Safety
    Validates: Requirements 8.4
    
    Property: *For any* concurrent access to the same data by multiple agents, 
    the system should prevent data conflicts and maintain consistency through 
    proper locking or versioning.
    
    This property tests that:
    1. Multiple concurrent readers can read the same data without conflicts
    2. Concurrent writers detect version conflicts and handle them appropriately
    3. Version numbers increment correctly with each update
    4. Data integrity is maintained across concurrent operations
    5. Conflict resolution strategies work correctly
    """
    manager = OptimisticLockManager()
    resource_id = f"inventory-{sku}"
    
    # Initial data
    initial_data = {
        "sku": sku,
        "quantity": initial_quantity,
        "warehouse": "WH-001",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Simulate multiple concurrent readers reading the same data
    versioned_reader1 = manager.acquire_lock(resource_id, initial_data)
    version_at_read1 = versioned_reader1.version
    
    versioned_reader2 = manager.acquire_lock(resource_id, initial_data)
    version_at_read2 = versioned_reader2.version
    
    # Both readers should see the same version
    assert version_at_read1 == version_at_read2, \
        "Concurrent readers should see the same version"
    assert version_at_read1 == 1, \
        "Initial version should be 1"
    
    # First writer updates with correct version
    update1_data = initial_data.copy()
    update1_data["quantity"] = update1_quantity
    
    success1, error1 = manager.update_with_lock(
        resource_id,
        version_at_read1,
        update1_data,
        strategy=ConflictResolutionStrategy.ABORT
    )
    
    assert success1 is True, "First writer should succeed with correct version"
    assert error1 is None, "No error should occur for first writer"
    
    # Verify version incremented
    versioned_after_update1 = manager._locks[resource_id]
    assert versioned_after_update1.version == 2, \
        "Version should increment after first update"
    assert versioned_after_update1.data["quantity"] == update1_quantity, \
        "Data should be updated correctly"
    
    # Second writer (who read old version) should detect conflict
    update2_data = initial_data.copy()
    update2_data["quantity"] = update2_quantity
    
    success2, error2 = manager.update_with_lock(
        resource_id,
        version_at_read2,  # Old version
        update2_data,
        strategy=ConflictResolutionStrategy.ABORT
    )
    
    assert success2 is False, "Second writer should fail with old version (ABORT strategy)"
    assert error2 is not None, "Error should be provided for version conflict"
    assert "Version conflict" in error2, "Error should mention version conflict"
    
    # Verify data was not corrupted by failed update
    versioned_after_conflict = manager._locks[resource_id]
    assert versioned_after_conflict.version == 2, \
        "Version should not change after failed update"
    assert versioned_after_conflict.data["quantity"] == update1_quantity, \
        "Data should not be modified by failed update"
    assert versioned_after_conflict.verify_integrity() is True, \
        "Data integrity should be maintained after conflict"
    
    # Test LAST_WRITE_WINS strategy for conflict resolution
    update3_data = initial_data.copy()
    update3_data["quantity"] = update3_quantity
    
    success3, error3 = manager.update_with_lock(
        resource_id,
        version_at_read2,  # Old version
        update3_data,
        strategy=ConflictResolutionStrategy.LAST_WRITE_WINS
    )
    
    assert success3 is True, "Update should succeed with LAST_WRITE_WINS strategy"
    assert error3 is None, "No error should occur with LAST_WRITE_WINS"
    
    # Verify version incremented and data updated
    versioned_after_lww = manager._locks[resource_id]
    assert versioned_after_lww.version == 3, \
        "Version should increment with LAST_WRITE_WINS"
    assert versioned_after_lww.data["quantity"] == update3_quantity, \
        "Data should be updated with LAST_WRITE_WINS"
    assert versioned_after_lww.verify_integrity() is True, \
        "Data integrity should be maintained with LAST_WRITE_WINS"
    
    # Test MERGE strategy for conflict resolution
    merge_data = initial_data.copy()
    merge_data["quantity"] = 5000
    merge_data["supplier"] = "SUP-001"  # New field
    
    success_merge, error_merge = manager.update_with_lock(
        resource_id,
        version_at_read2,  # Old version
        merge_data,
        strategy=ConflictResolutionStrategy.MERGE
    )
    
    assert success_merge is True, "Update should succeed with MERGE strategy"
    assert error_merge is None, "No error should occur with MERGE"
    
    # Verify merged data contains both old and new values
    versioned_after_merge = manager._locks[resource_id]
    assert versioned_after_merge.version == 4, \
        "Version should increment with MERGE"
    assert versioned_after_merge.data["quantity"] == 5000, \
        "New quantity should be in merged data"
    assert versioned_after_merge.data["supplier"] == "SUP-001", \
        "New supplier field should be in merged data"
    assert versioned_after_merge.data["sku"] == sku, \
        "Original SKU should be preserved in merged data"
    assert versioned_after_merge.verify_integrity() is True, \
        "Data integrity should be maintained with MERGE"
    
    # Test FIRST_WRITE_WINS strategy
    fww_data = initial_data.copy()
    fww_data["quantity"] = 7000
    
    success_fww, error_fww = manager.update_with_lock(
        resource_id,
        version_at_read2,  # Old version
        fww_data,
        strategy=ConflictResolutionStrategy.FIRST_WRITE_WINS
    )
    
    assert success_fww is False, "Update should fail with FIRST_WRITE_WINS strategy"
    assert error_fww is not None, "Error should be provided with FIRST_WRITE_WINS"
    assert "First write wins" in error_fww, "Error should mention first write wins"
    
    # Verify data was not modified by failed FIRST_WRITE_WINS
    versioned_after_fww = manager._locks[resource_id]
    assert versioned_after_fww.version == 4, \
        "Version should not change after failed FIRST_WRITE_WINS"
    assert versioned_after_fww.data["quantity"] == 5000, \
        "Data should not be modified by failed FIRST_WRITE_WINS"
    assert versioned_after_fww.verify_integrity() is True, \
        "Data integrity should be maintained after failed FIRST_WRITE_WINS"
