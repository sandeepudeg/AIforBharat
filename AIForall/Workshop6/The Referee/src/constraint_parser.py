"""Constraint parsing and validation."""

from typing import Dict, Optional, Tuple
from pydantic import ValidationError as PydanticValidationError
from src.models import Constraint, ValidationError


class ConstraintParser:
    """Parses and validates user constraint inputs."""

    VALID_DATA_STRUCTURES = ["Relational", "JSON", "Key-Value"]
    VALID_CONSISTENCY_LEVELS = ["Strong", "Eventual"]
    VALID_QUERY_COMPLEXITIES = ["Simple", "Moderate", "Complex"]
    VALID_TEAM_EXPERTISE = ["Low", "Medium", "High"]

    @staticmethod
    def parse_constraints(raw_inputs: Dict) -> Tuple[Optional[Constraint], Optional[ValidationError]]:
        """Parse raw inputs into a Constraint object.
        
        Args:
            raw_inputs: Dictionary of raw user inputs
            
        Returns:
            Tuple of (Constraint object, ValidationError) - one will be None
        """
        try:
            constraint = Constraint(**raw_inputs)
            return constraint, None
        except PydanticValidationError as e:
            # Extract first error for user-friendly message
            error = e.errors()[0]
            field = error["loc"][0]
            msg = error["msg"]
            
            validation_error = ValidationError(
                field=str(field),
                message=f"Field '{field}': {msg}"
            )
            return None, validation_error

    @staticmethod
    def validate_data_structure(value: str) -> Tuple[bool, Optional[str]]:
        """Validate data structure value.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, str):
            return False, f"data_structure must be a string, got {type(value).__name__}"
        
        if value not in ConstraintParser.VALID_DATA_STRUCTURES:
            return False, f"data_structure must be one of {ConstraintParser.VALID_DATA_STRUCTURES}"
        
        return True, None

    @staticmethod
    def validate_read_write_ratio(value) -> Tuple[bool, Optional[str]]:
        """Validate read/write ratio value.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False, f"read_write_ratio must be an integer, got {type(value).__name__}"
        
        if not (0 <= int_value <= 100):
            return False, f"read_write_ratio must be between 0 and 100, got {int_value}"
        
        return True, None

    @staticmethod
    def validate_consistency_level(value: str) -> Tuple[bool, Optional[str]]:
        """Validate consistency level value.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, str):
            return False, f"consistency_level must be a string, got {type(value).__name__}"
        
        if value not in ConstraintParser.VALID_CONSISTENCY_LEVELS:
            return False, f"consistency_level must be one of {ConstraintParser.VALID_CONSISTENCY_LEVELS}"
        
        return True, None

    @staticmethod
    def validate_query_complexity(value: str) -> Tuple[bool, Optional[str]]:
        """Validate query complexity value.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, str):
            return False, f"query_complexity must be a string, got {type(value).__name__}"
        
        if value not in ConstraintParser.VALID_QUERY_COMPLEXITIES:
            return False, f"query_complexity must be one of {ConstraintParser.VALID_QUERY_COMPLEXITIES}"
        
        return True, None

    @staticmethod
    def validate_scale_gb(value) -> Tuple[bool, Optional[str]]:
        """Validate data scale value.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            return False, f"scale_gb must be a number, got {type(value).__name__}"
        
        if float_value <= 0:
            return False, f"scale_gb must be positive, got {float_value}"
        
        return True, None

    @staticmethod
    def validate_latency_ms(value) -> Tuple[bool, Optional[str]]:
        """Validate latency requirement value.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            float_value = float(value)
        except (ValueError, TypeError):
            return False, f"latency_ms must be a number, got {type(value).__name__}"
        
        if float_value <= 0:
            return False, f"latency_ms must be positive, got {float_value}"
        
        return True, None

    @staticmethod
    def validate_team_expertise(value: str) -> Tuple[bool, Optional[str]]:
        """Validate team expertise value.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(value, str):
            return False, f"team_expertise must be a string, got {type(value).__name__}"
        
        if value not in ConstraintParser.VALID_TEAM_EXPERTISE:
            return False, f"team_expertise must be one of {ConstraintParser.VALID_TEAM_EXPERTISE}"
        
        return True, None
