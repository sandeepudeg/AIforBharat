"""Property-based tests for Scoring Engine.

Feature: database-referee, Property 4: Score Normalization Bounds
Validates: Requirements 3.1-3.11
"""

import pytest
from hypothesis import given, strategies as st
from src.models import Constraint
from src.scoring_engine import ScoringEngine


# Define strategies
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
def test_score_normalization_bounds(
    data_structure,
    read_write_ratio,
    consistency_level,
    query_complexity,
    scale_gb,
    latency_ms,
    team_expertise,
):
    """Property 4: All final scores are within [0, 10] range.
    
    Validates: Requirements 3.11
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
    
    candidates = ["PostgreSQL", "DynamoDB", "Redis"]
    scores = ScoringEngine.score_databases(constraint, candidates)
    
    # All scores must be within [0, 10]
    for db, score in scores.items():
        assert 0 <= score <= 10, f"{db} score {score} is outside [0, 10]"


@given(
    data_structure=data_structure_strategy,
    read_write_ratio=read_write_ratio_strategy,
    consistency_level=consistency_strategy,
    query_complexity=complexity_strategy,
    scale_gb=scale_strategy,
    latency_ms=latency_strategy,
    team_expertise=expertise_strategy,
)
def test_component_score_bounds(
    data_structure,
    read_write_ratio,
    consistency_level,
    query_complexity,
    scale_gb,
    latency_ms,
    team_expertise,
):
    """Property 6: All component scores are within [0, 1] range.
    
    Validates: Requirements 3.6-3.10
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
    
    for db in ["PostgreSQL", "DynamoDB", "Redis"]:
        # Test each component score
        data_score = ScoringEngine.calculate_data_structure_match(db, constraint)
        assert 0 <= data_score <= 1, f"Data structure score {data_score} out of bounds"
        
        consistency_score = ScoringEngine.calculate_consistency_match(db, constraint)
        assert 0 <= consistency_score <= 1, f"Consistency score {consistency_score} out of bounds"
        
        query_score = ScoringEngine.calculate_query_flexibility(db, constraint)
        assert 0 <= query_score <= 1, f"Query score {query_score} out of bounds"
        
        cost_score = ScoringEngine.calculate_cost_score(db, constraint)
        assert 0 <= cost_score <= 1, f"Cost score {cost_score} out of bounds"
        
        latency_score = ScoringEngine.calculate_latency_score(db, constraint)
        assert 0 <= latency_score <= 1, f"Latency score {latency_score} out of bounds"


@given(
    data_structure=data_structure_strategy,
    read_write_ratio=read_write_ratio_strategy,
    consistency_level=consistency_strategy,
    query_complexity=complexity_strategy,
    scale_gb=scale_strategy,
    latency_ms=latency_strategy,
    team_expertise=expertise_strategy,
)
def test_score_monotonicity_with_adjustments(
    data_structure,
    read_write_ratio,
    consistency_level,
    query_complexity,
    scale_gb,
    latency_ms,
    team_expertise,
):
    """Property 5: Adjusted scores are >= base scores (monotonicity).
    
    Validates: Requirements 3.3, 3.4, 3.5
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
    
    for db in ["PostgreSQL", "DynamoDB", "Redis"]:
        # Calculate base score
        data_score = ScoringEngine.calculate_data_structure_match(db, constraint)
        consistency_score = ScoringEngine.calculate_consistency_match(db, constraint)
        query_score = ScoringEngine.calculate_query_flexibility(db, constraint)
        cost_score = ScoringEngine.calculate_cost_score(db, constraint)
        latency_score = ScoringEngine.calculate_latency_score(db, constraint)
        
        base_score = (
            data_score * ScoringEngine.BASE_WEIGHTS["data_structure_match"] +
            consistency_score * ScoringEngine.BASE_WEIGHTS["consistency_match"] +
            query_score * ScoringEngine.BASE_WEIGHTS["query_flexibility"] +
            cost_score * ScoringEngine.BASE_WEIGHTS["cost_score"] +
            latency_score * ScoringEngine.BASE_WEIGHTS["latency_score"]
        )
        
        # Apply adjustments
        adjusted_score = ScoringEngine.apply_adjustments(base_score, constraint, db)
        
        # Adjusted score should be >= base score (or very close due to rounding)
        # Allow small tolerance for floating point errors
        assert adjusted_score >= base_score - 0.01, \
            f"{db}: adjusted score {adjusted_score} < base score {base_score}"


@given(
    read_write_ratio=read_write_ratio_strategy,
    consistency_level=consistency_strategy,
    query_complexity=complexity_strategy,
    scale_gb=scale_strategy,
    latency_ms=latency_strategy,
    team_expertise=expertise_strategy,
)
def test_relational_complex_queries_boost_postgresql(
    read_write_ratio,
    consistency_level,
    query_complexity,
    scale_gb,
    latency_ms,
    team_expertise,
):
    """Property 5a: Relational + Complex queries boost PostgreSQL score.
    
    Validates: Requirements 3.3
    """
    constraint = Constraint(
        data_structure="Relational",
        read_write_ratio=read_write_ratio,
        consistency_level=consistency_level,
        query_complexity="Complex",
        scale_gb=scale_gb,
        latency_ms=latency_ms,
        team_expertise=team_expertise,
    )
    
    candidates = ["PostgreSQL", "DynamoDB", "Redis"]
    scores = ScoringEngine.score_databases(constraint, candidates)
    
    # PostgreSQL should score higher than DynamoDB for complex relational queries
    assert scores["PostgreSQL"] > scores["DynamoDB"], \
        "PostgreSQL should score higher for complex relational queries"


@given(
    data_structure=data_structure_strategy,
    read_write_ratio=read_write_ratio_strategy,
    query_complexity=complexity_strategy,
    scale_gb=scale_strategy,
    latency_ms=latency_strategy,
    team_expertise=expertise_strategy,
)
def test_strong_consistency_boost_postgresql(
    data_structure,
    read_write_ratio,
    query_complexity,
    scale_gb,
    latency_ms,
    team_expertise,
):
    """Property 5b: Strong consistency boosts PostgreSQL score.
    
    Validates: Requirements 3.4
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
    
    candidates = ["PostgreSQL", "DynamoDB", "Redis"]
    scores = ScoringEngine.score_databases(constraint, candidates)
    
    # PostgreSQL should score higher than DynamoDB for strong consistency
    assert scores["PostgreSQL"] > scores["DynamoDB"], \
        "PostgreSQL should score higher for strong consistency"


@given(
    data_structure=data_structure_strategy,
    read_write_ratio=read_write_ratio_strategy,
    consistency_level=consistency_strategy,
    query_complexity=complexity_strategy,
    latency_ms=latency_strategy,
    team_expertise=expertise_strategy,
)
def test_large_scale_boost_dynamodb(
    data_structure,
    read_write_ratio,
    consistency_level,
    query_complexity,
    latency_ms,
    team_expertise,
):
    """Property 5c: Large scale (>100GB) boosts DynamoDB score.
    
    Validates: Requirements 3.5
    """
    constraint = Constraint(
        data_structure=data_structure,
        read_write_ratio=read_write_ratio,
        consistency_level=consistency_level,
        query_complexity=query_complexity,
        scale_gb=500.0,  # Large scale
        latency_ms=latency_ms,
        team_expertise=team_expertise,
    )
    
    candidates = ["PostgreSQL", "DynamoDB", "Redis"]
    scores = ScoringEngine.score_databases(constraint, candidates)
    
    # DynamoDB should score higher than PostgreSQL for large scale
    assert scores["DynamoDB"] > scores["PostgreSQL"], \
        "DynamoDB should score higher for large scale (>100GB)"
