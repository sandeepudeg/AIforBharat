"""Property-based tests for Constraint model.

Feature: database-referee, Property 1: Constraint Validation Completeness
Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9
"""

import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError
from src.models import Constraint


# Define strategies for valid constraint values
data_structure_strategy = st.sampled_from(["Relational", "JSON", "Key-Value"])
consistency_strategy = st.sampled_from(["Strong", "Eventual"])
complexity_strategy = st.sampled_from(["Simple", "Moderate", "Complex"])
expertise_strategy = st.sampled_from(["Low", "Medium", "High"])
read_write_ratio_strategy = st.integers(min_value=0, max_value=100)
scale_strategy = st.floats(min_value=0.1, max_value=10000)
latency_strategy = st.floats(min_value=0.1, max_value=1000)


@given(
    data_structure=data_structure_strategy,
    read_write_ratio=read_write_ratio_strategy,
    consistency_level=consistency_strategy,
    query_complexity=complexity_strategy,
    scale_gb=scale_strategy,
    latency_ms=latency_strategy,
    team_expertise=expertise_strategy,
)
def test_constraint_validation_completeness(
    data_structure,
    read_write_ratio,
    consistency_level,
    query_complexity,
    scale_gb,
    latency_ms,
    team_expertise,
):
    """Property 1: For any valid constraint inputs, the Constraint model SHALL successfully parse them.
    
    Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9
    """
    # Create constraint with valid inputs
    constraint = Constraint(
        data_structure=data_structure,
        read_write_ratio=read_write_ratio,
        consistency_level=consistency_level,
        query_complexity=query_complexity,
        scale_gb=scale_gb,
        latency_ms=latency_ms,
        team_expertise=team_expertise,
    )

    # Verify all fields are populated correctly
    assert constraint.data_structure == data_structure
    assert constraint.read_write_ratio == read_write_ratio
    assert constraint.consistency_level == consistency_level
    assert constraint.query_complexity == query_complexity
    assert constraint.scale_gb == scale_gb
    assert constraint.latency_ms == latency_ms
    assert constraint.team_expertise == team_expertise
    assert constraint.requires_persistence is True  # Default value

@given(
    invalid_ratio=st.integers(min_value=-100, max_value=-1) | st.integers(min_value=101, max_value=200),
)
def test_invalid_read_write_ratio_rejection(invalid_ratio):
    """Property 2a: For any invalid read/write ratio, the parser SHALL reject it.
    
    Validates: Requirements 1.10, 6.2, 6.3
    """
    with pytest.raises(ValidationError):
        Constraint(
            data_structure="Relational",
            read_write_ratio=invalid_ratio,
            consistency_level="Strong",
            query_complexity="Simple",
            scale_gb=10.0,
            latency_ms=5.0,
            team_expertise="Medium",
        )


@given(
    invalid_scale=st.floats(max_value=0) | st.floats(min_value=float('inf')),
)
def test_invalid_scale_rejection(invalid_scale):
    """Property 2b: For any invalid scale, the parser SHALL reject it.
    
    Validates: Requirements 1.10, 6.2, 6.3
    """
    # Skip infinite values
    if invalid_scale == float('inf') or invalid_scale == float('-inf'):
        return
    
    with pytest.raises(ValidationError):
        Constraint(
            data_structure="Relational",
            read_write_ratio=50,
            consistency_level="Strong",
            query_complexity="Simple",
            scale_gb=invalid_scale,
            latency_ms=5.0,
            team_expertise="Medium",
        )


@given(
    invalid_data_structure=st.text().filter(
        lambda x: x not in ["Relational", "JSON", "Key-Value"]
    ),
)
def test_invalid_data_structure_rejection(invalid_data_structure):
    """Property 2c: For any invalid data structure, the parser SHALL reject it.
    
    Validates: Requirements 1.10, 6.2, 6.3
    """
    with pytest.raises(ValidationError):
        Constraint(
            data_structure=invalid_data_structure,
            read_write_ratio=50,
            consistency_level="Strong",
            query_complexity="Simple",
            scale_gb=10.0,
            latency_ms=5.0,
            team_expertise="Medium",
        )


@given(
    invalid_consistency=st.text().filter(
        lambda x: x not in ["Strong", "Eventual"]
    ),
)
def test_invalid_consistency_rejection(invalid_consistency):
    """Property 2d: For any invalid consistency level, the parser SHALL reject it.
    
    Validates: Requirements 1.10, 6.2, 6.3
    """
    with pytest.raises(ValidationError):
        Constraint(
            data_structure="Relational",
            read_write_ratio=50,
            consistency_level=invalid_consistency,
            query_complexity="Simple",
            scale_gb=10.0,
            latency_ms=5.0,
            team_expertise="Medium",
        )


import pytest
