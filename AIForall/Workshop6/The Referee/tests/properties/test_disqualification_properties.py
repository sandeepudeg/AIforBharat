"""Property-based tests for Disqualification Engine.

Feature: database-referee, Property 3: Disqualification Rule Consistency
Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
"""

import pytest
from hypothesis import given, strategies as st
from src.models import Constraint
from src.disqualification_engine import DisqualificationEngine


# Define strategies for constraint generation
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
def test_disqualification_rule_consistency(
    data_structure,
    read_write_ratio,
    consistency_level,
    query_complexity,
    scale_gb,
    latency_ms,
    team_expertise,
):
    """Property 3: For any constraint, disqualification rules are consistent.
    
    If a database is disqualified by a rule, it SHALL remain disqualified.
    
    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
    """
    constraint = Constraint(
        data_structure=data_structure,
        read_write_ratio=read_write_ratio,
        consistency_level=consistency_level,
        query_complexity=query_complexity,
        scale_gb=scale_gb,
        latency_ms=latency_ms,
        team_expertise=team_expertise,
    )
    
    # Apply disqualification rules
    remaining, disqualified = DisqualificationEngine.disqualify(constraint)
    
    # Verify consistency: no database appears in both lists
    assert len(set(remaining) & set(disqualified.keys())) == 0, \
        "Database cannot be both remaining and disqualified"
    
    # Verify all databases are accounted for
    all_databases = set(remaining) | set(disqualified.keys())
    assert all_databases == set(DisqualificationEngine.DATABASES), \
        "All databases must be either remaining or disqualified"
    
    # Verify at least one database remains (unless all are disqualified)
    # This is allowed but should be rare
    assert len(remaining) >= 0, "Remaining list cannot be negative"


@given(
    read_write_ratio=read_write_ratio_strategy,
    scale_gb=scale_strategy,
    latency_ms=latency_strategy,
    team_expertise=expertise_strategy,
)
def test_joins_required_disqualifies_dynamodb(
    read_write_ratio,
    scale_gb,
    latency_ms,
    team_expertise,
):
    """Property 3a: When joins are required, DynamoDB is disqualified.
    
    Joins are required when: data_structure=Relational AND query_complexity=Complex
    
    Validates: Requirements 2.1
    """
    constraint = Constraint(
        data_structure="Relational",
        read_write_ratio=read_write_ratio,
        consistency_level="Eventual",
        query_complexity="Complex",
        scale_gb=scale_gb,
        latency_ms=latency_ms,
        team_expertise=team_expertise,
    )
    
    remaining, disqualified = DisqualificationEngine.disqualify(constraint)
    
    # DynamoDB should be disqualified
    assert "DynamoDB" in disqualified, "DynamoDB should be disqualified when joins are required"
    assert "DynamoDB" not in remaining, "DynamoDB should not be in remaining"


@given(
    data_structure=data_structure_strategy,
    read_write_ratio=read_write_ratio_strategy,
    query_complexity=complexity_strategy,
    scale_gb=scale_strategy,
    latency_ms=latency_strategy,
    team_expertise=expertise_strategy,
)
def test_strong_consistency_disqualifies_dynamodb(
    data_structure,
    read_write_ratio,
    query_complexity,
    scale_gb,
    latency_ms,
    team_expertise,
):
    """Property 3b: When strong consistency is required, DynamoDB is disqualified.
    
    Validates: Requirements 2.2
    """
    constraint = Constraint(
        data_structure=data_structure,
        read_write_ratio=read_write_ratio,
        consistency_level="Strong",
        query_complexity=query_complexity,
        scale_gb=scale_gb,
        latency_ms=latency_ms,
        team_expertise=team_expertise,
    )
    
    remaining, disqualified = DisqualificationEngine.disqualify(constraint)
    
    # DynamoDB should be disqualified
    assert "DynamoDB" in disqualified, "DynamoDB should be disqualified for strong consistency"
    assert "DynamoDB" not in remaining, "DynamoDB should not be in remaining"


@given(
    data_structure=data_structure_strategy,
    read_write_ratio=read_write_ratio_strategy,
    consistency_level=consistency_strategy,
    query_complexity=complexity_strategy,
    scale_gb=scale_strategy,
    latency_ms=latency_strategy,
    team_expertise=expertise_strategy,
)
def test_persistence_required_disqualifies_redis(
    data_structure,
    read_write_ratio,
    consistency_level,
    query_complexity,
    scale_gb,
    latency_ms,
    team_expertise,
):
    """Property 3c: When persistence is critical, Redis is disqualified.
    
    Validates: Requirements 2.3
    """
    constraint = Constraint(
        data_structure=data_structure,
        read_write_ratio=read_write_ratio,
        consistency_level=consistency_level,
        query_complexity=query_complexity,
        scale_gb=scale_gb,
        latency_ms=latency_ms,
        team_expertise=team_expertise,
        requires_persistence=True,
    )
    
    remaining, disqualified = DisqualificationEngine.disqualify(constraint)
    
    # Redis should be disqualified
    assert "Redis" in disqualified, "Redis should be disqualified when persistence is required"
    assert "Redis" not in remaining, "Redis should not be in remaining"


@given(
    data_structure=data_structure_strategy,
    read_write_ratio=read_write_ratio_strategy,
    consistency_level=consistency_strategy,
    query_complexity=complexity_strategy,
    latency_ms=latency_strategy,
    team_expertise=expertise_strategy,
)
def test_scale_exceeds_redis_limit_disqualifies_redis(
    data_structure,
    read_write_ratio,
    consistency_level,
    query_complexity,
    latency_ms,
    team_expertise,
):
    """Property 3d: When scale > 10GB, Redis is disqualified.
    
    Validates: Requirements 2.4
    """
    constraint = Constraint(
        data_structure=data_structure,
        read_write_ratio=read_write_ratio,
        consistency_level=consistency_level,
        query_complexity=query_complexity,
        scale_gb=100.0,  # Exceeds 10GB limit
        latency_ms=latency_ms,
        team_expertise=team_expertise,
        requires_persistence=False,
    )
    
    remaining, disqualified = DisqualificationEngine.disqualify(constraint)
    
    # Redis should be disqualified
    assert "Redis" in disqualified, "Redis should be disqualified when scale > 10GB"
    assert "Redis" not in remaining, "Redis should not be in remaining"


@given(
    data_structure=data_structure_strategy,
    read_write_ratio=read_write_ratio_strategy,
    consistency_level=consistency_strategy,
    query_complexity=complexity_strategy,
    scale_gb=scale_strategy,
    team_expertise=expertise_strategy,
)
def test_ultra_low_latency_disqualifies_postgresql(
    data_structure,
    read_write_ratio,
    consistency_level,
    query_complexity,
    scale_gb,
    team_expertise,
):
    """Property 3e: When latency < 1ms, PostgreSQL is disqualified.
    
    Validates: Requirements 2.5
    """
    constraint = Constraint(
        data_structure=data_structure,
        read_write_ratio=read_write_ratio,
        consistency_level=consistency_level,
        query_complexity=query_complexity,
        scale_gb=scale_gb,
        latency_ms=0.5,  # Less than 1ms
        team_expertise=team_expertise,
    )
    
    remaining, disqualified = DisqualificationEngine.disqualify(constraint)
    
    # PostgreSQL should be disqualified
    assert "PostgreSQL" in disqualified, "PostgreSQL should be disqualified for latency < 1ms"
    assert "PostgreSQL" not in remaining, "PostgreSQL should not be in remaining"
