"""Data integrity and concurrent access handling utilities.

This module provides:
- Optimistic locking for concurrent updates
- Transaction support for multi-step operations
- Data validation and checksums
- Conflict resolution strategies
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional, Callable, TypeVar, List
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.config import logger

T = TypeVar('T')


class ConflictResolutionStrategy(str, Enum):
    """Strategies for resolving concurrent access conflicts."""
    
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    MERGE = "merge"
    ABORT = "abort"


@dataclass
class VersionedData:
    """Data wrapper with version information for optimistic locking."""
    
    data: Dict[str, Any]
    version: int = 1
    last_modified: datetime = field(default_factory=datetime.utcnow)
    checksum: str = ""
    
    def __post_init__(self):
        """Calculate checksum after initialization."""
        if not self.checksum:
            self.checksum = self.calculate_checksum()
    
    def calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of data for integrity verification."""
        data_str = json.dumps(self.data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify data integrity by comparing checksums."""
        current_checksum = self.calculate_checksum()
        return current_checksum == self.checksum
    
    def increment_version(self) -> None:
        """Increment version number for optimistic locking."""
        self.version += 1
        self.last_modified = datetime.utcnow()
        self.checksum = self.calculate_checksum()


class OptimisticLockManager:
    """Manages optimistic locking for concurrent updates."""
    
    def __init__(self):
        """Initialize the optimistic lock manager."""
        self._locks: Dict[str, VersionedData] = {}
    
    def acquire_lock(self, resource_id: str, data: Dict[str, Any]) -> VersionedData:
        """Acquire an optimistic lock on a resource.
        
        Args:
            resource_id: Unique identifier for the resource
            data: Current data for the resource
            
        Returns:
            VersionedData with version information
        """
        if resource_id not in self._locks:
            self._locks[resource_id] = VersionedData(data=data)
            logger.debug(f"Optimistic lock acquired for resource: {resource_id}")
        return self._locks[resource_id]
    
    def release_lock(self, resource_id: str) -> None:
        """Release an optimistic lock on a resource.
        
        Args:
            resource_id: Unique identifier for the resource
        """
        if resource_id in self._locks:
            del self._locks[resource_id]
            logger.debug(f"Optimistic lock released for resource: {resource_id}")
    
    def validate_version(self, resource_id: str, expected_version: int) -> bool:
        """Validate that the current version matches expected version.
        
        Args:
            resource_id: Unique identifier for the resource
            expected_version: Expected version number
            
        Returns:
            True if versions match, False otherwise
        """
        if resource_id not in self._locks:
            return False
        
        current_version = self._locks[resource_id].version
        return current_version == expected_version
    
    def update_with_lock(
        self,
        resource_id: str,
        expected_version: int,
        new_data: Dict[str, Any],
        strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.ABORT
    ) -> tuple[bool, Optional[str]]:
        """Attempt to update data with optimistic locking.
        
        Args:
            resource_id: Unique identifier for the resource
            expected_version: Expected version number
            new_data: New data to store
            strategy: Conflict resolution strategy
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if resource_id not in self._locks:
            return False, f"Resource {resource_id} not found"
        
        versioned_data = self._locks[resource_id]
        
        # Check if version matches (optimistic lock validation)
        if versioned_data.version != expected_version:
            error_msg = (
                f"Version conflict for resource {resource_id}: "
                f"expected {expected_version}, got {versioned_data.version}"
            )
            
            if strategy == ConflictResolutionStrategy.ABORT:
                logger.warning(error_msg)
                return False, error_msg
            elif strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
                logger.info(f"Applying LAST_WRITE_WINS strategy for {resource_id}")
                versioned_data.data = new_data
                versioned_data.increment_version()
                return True, None
            elif strategy == ConflictResolutionStrategy.FIRST_WRITE_WINS:
                logger.info(f"Applying FIRST_WRITE_WINS strategy for {resource_id}")
                return False, "First write wins: update rejected"
            elif strategy == ConflictResolutionStrategy.MERGE:
                logger.info(f"Applying MERGE strategy for {resource_id}")
                merged_data = self._merge_data(versioned_data.data, new_data)
                versioned_data.data = merged_data
                versioned_data.increment_version()
                return True, None
        
        # Version matches, update data
        versioned_data.data = new_data
        versioned_data.increment_version()
        logger.debug(f"Data updated for resource {resource_id}, new version: {versioned_data.version}")
        return True, None
    
    @staticmethod
    def _merge_data(old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge old and new data, preferring new values.
        
        Args:
            old_data: Previous data
            new_data: New data
            
        Returns:
            Merged data dictionary
        """
        merged = old_data.copy()
        merged.update(new_data)
        return merged


class TransactionManager:
    """Manages database transactions for multi-step operations."""
    
    def __init__(self, session: Session):
        """Initialize transaction manager.
        
        Args:
            session: SQLAlchemy database session
        """
        self.session = session
        self._transaction_stack: List[str] = []
    
    def begin_transaction(self, transaction_id: str) -> None:
        """Begin a new transaction.
        
        Args:
            transaction_id: Unique identifier for the transaction
        """
        self._transaction_stack.append(transaction_id)
        logger.debug(f"Transaction started: {transaction_id}")
    
    def commit_transaction(self, transaction_id: str) -> bool:
        """Commit a transaction.
        
        Args:
            transaction_id: Unique identifier for the transaction
            
        Returns:
            True if commit successful, False otherwise
        """
        try:
            if transaction_id not in self._transaction_stack:
                logger.warning(f"Transaction {transaction_id} not found in stack")
                return False
            
            self.session.commit()
            self._transaction_stack.remove(transaction_id)
            logger.debug(f"Transaction committed: {transaction_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to commit transaction {transaction_id}: {str(e)}")
            self.session.rollback()
            return False
    
    def rollback_transaction(self, transaction_id: str) -> bool:
        """Rollback a transaction.
        
        Args:
            transaction_id: Unique identifier for the transaction
            
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            if transaction_id not in self._transaction_stack:
                logger.warning(f"Transaction {transaction_id} not found in stack")
                return False
            
            self.session.rollback()
            self._transaction_stack.remove(transaction_id)
            logger.debug(f"Transaction rolled back: {transaction_id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to rollback transaction {transaction_id}: {str(e)}")
            return False
    
    def execute_transaction(
        self,
        transaction_id: str,
        operations: List[Callable[[], Any]]
    ) -> tuple[bool, Optional[str]]:
        """Execute multiple operations in a single transaction.
        
        Args:
            transaction_id: Unique identifier for the transaction
            operations: List of callable operations to execute
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        self.begin_transaction(transaction_id)
        
        try:
            for operation in operations:
                operation()
            
            if self.commit_transaction(transaction_id):
                logger.info(f"Transaction {transaction_id} completed successfully")
                return True, None
            else:
                return False, f"Failed to commit transaction {transaction_id}"
        except Exception as e:
            error_msg = f"Transaction {transaction_id} failed: {str(e)}"
            logger.error(error_msg)
            self.rollback_transaction(transaction_id)
            return False, error_msg


class DataValidator:
    """Validates data integrity and constraints."""
    
    @staticmethod
    def validate_referential_integrity(
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> tuple[bool, Optional[str]]:
        """Validate that all required fields are present.
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            
        Returns:
            Tuple of (valid: bool, error_message: Optional[str])
        """
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.warning(error_msg)
            return False, error_msg
        
        return True, None
    
    @staticmethod
    def validate_data_types(
        data: Dict[str, Any],
        type_constraints: Dict[str, type]
    ) -> tuple[bool, Optional[str]]:
        """Validate that data types match constraints.
        
        Args:
            data: Data to validate
            type_constraints: Dictionary mapping field names to expected types
            
        Returns:
            Tuple of (valid: bool, error_message: Optional[str])
        """
        for field_name, expected_type in type_constraints.items():
            if field_name in data:
                if not isinstance(data[field_name], expected_type):
                    error_msg = (
                        f"Field '{field_name}' has type {type(data[field_name]).__name__}, "
                        f"expected {expected_type.__name__}"
                    )
                    logger.warning(error_msg)
                    return False, error_msg
        
        return True, None
    
    @staticmethod
    def validate_value_ranges(
        data: Dict[str, Any],
        range_constraints: Dict[str, tuple[Any, Any]]
    ) -> tuple[bool, Optional[str]]:
        """Validate that numeric values are within specified ranges.
        
        Args:
            data: Data to validate
            range_constraints: Dictionary mapping field names to (min, max) tuples
            
        Returns:
            Tuple of (valid: bool, error_message: Optional[str])
        """
        for field_name, (min_val, max_val) in range_constraints.items():
            if field_name in data:
                value = data[field_name]
                if not (min_val <= value <= max_val):
                    error_msg = (
                        f"Field '{field_name}' value {value} is outside range "
                        f"[{min_val}, {max_val}]"
                    )
                    logger.warning(error_msg)
                    return False, error_msg
        
        return True, None


class ChecksumManager:
    """Manages checksums for data integrity verification."""
    
    @staticmethod
    def calculate_checksum(data: Dict[str, Any]) -> str:
        """Calculate SHA256 checksum for data.
        
        Args:
            data: Data to checksum
            
        Returns:
            Hexadecimal checksum string
        """
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    @staticmethod
    def verify_checksum(data: Dict[str, Any], expected_checksum: str) -> bool:
        """Verify data integrity using checksum.
        
        Args:
            data: Data to verify
            expected_checksum: Expected checksum value
            
        Returns:
            True if checksum matches, False otherwise
        """
        calculated_checksum = ChecksumManager.calculate_checksum(data)
        return calculated_checksum == expected_checksum
    
    @staticmethod
    def calculate_batch_checksum(data_list: List[Dict[str, Any]]) -> str:
        """Calculate checksum for a batch of data items.
        
        Args:
            data_list: List of data dictionaries
            
        Returns:
            Hexadecimal checksum string
        """
        combined_data = json.dumps(data_list, sort_keys=True, default=str)
        return hashlib.sha256(combined_data.encode()).hexdigest()


# Global instances
_optimistic_lock_manager = OptimisticLockManager()


def get_optimistic_lock_manager() -> OptimisticLockManager:
    """Get the global optimistic lock manager instance.
    
    Returns:
        OptimisticLockManager instance
    """
    return _optimistic_lock_manager
