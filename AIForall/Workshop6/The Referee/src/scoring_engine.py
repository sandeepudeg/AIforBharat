"""Scoring engine for database selection."""

from typing import Dict, List
from src.models import Constraint


class ScoringEngine:
    """Calculates weighted scores for database options."""

    # Base weights for scoring components
    BASE_WEIGHTS = {
        "data_structure_match": 0.30,
        "consistency_match": 0.25,
        "query_flexibility": 0.20,
        "cost_score": 0.15,
        "latency_score": 0.10,
    }

    # Database profiles
    DATABASE_PROFILES = {
        "PostgreSQL": {
            "data_structure_support": {
                "Relational": 1.0,
                "JSON": 0.7,
                "Key-Value": 0.3,
            },
            "consistency_capability": "Strong",
            "query_flexibility": 1.0,  # Full SQL
            "base_cost": 0.6,
            "latency_profile": {"typical": 5.0, "best": 1.0, "worst": 100.0},
            "scaling_capability": "Vertical",
            "persistence": True,
            "max_scale_gb": 1000.0,
        },
        "DynamoDB": {
            "data_structure_support": {
                "Relational": 0.0,
                "JSON": 0.8,
                "Key-Value": 1.0,
            },
            "consistency_capability": "Eventual",
            "query_flexibility": 0.3,  # Key-value only
            "base_cost": 0.4,
            "latency_profile": {"typical": 3.0, "best": 1.0, "worst": 50.0},
            "scaling_capability": "Horizontal",
            "persistence": True,
            "max_scale_gb": 10000.0,
        },
        "Redis": {
            "data_structure_support": {
                "Relational": 0.0,
                "JSON": 0.5,
                "Key-Value": 1.0,
            },
            "consistency_capability": "Eventual",
            "query_flexibility": 0.2,  # Very limited
            "base_cost": 0.3,
            "latency_profile": {"typical": 0.5, "best": 0.1, "worst": 10.0},
            "scaling_capability": "Limited",
            "persistence": False,
            "max_scale_gb": 10.0,
        },
    }

    @staticmethod
    def score_databases(
        constraint: Constraint,
        candidates: List[str],
    ) -> Dict[str, float]:
        """Calculate scores for candidate databases.
        
        Args:
            constraint: User constraints
            candidates: List of database names to score
            
        Returns:
            Dictionary of {database_name: score}
        """
        scores = {}
        
        for db in candidates:
            if db not in ScoringEngine.DATABASE_PROFILES:
                continue
            
            # Calculate component scores
            data_structure_score = ScoringEngine.calculate_data_structure_match(db, constraint)
            consistency_score = ScoringEngine.calculate_consistency_match(db, constraint)
            query_score = ScoringEngine.calculate_query_flexibility(db, constraint)
            cost_score = ScoringEngine.calculate_cost_score(db, constraint)
            latency_score = ScoringEngine.calculate_latency_score(db, constraint)
            
            # Calculate base score
            base_score = (
                data_structure_score * ScoringEngine.BASE_WEIGHTS["data_structure_match"] +
                consistency_score * ScoringEngine.BASE_WEIGHTS["consistency_match"] +
                query_score * ScoringEngine.BASE_WEIGHTS["query_flexibility"] +
                cost_score * ScoringEngine.BASE_WEIGHTS["cost_score"] +
                latency_score * ScoringEngine.BASE_WEIGHTS["latency_score"]
            )
            
            # Apply adjustments
            adjusted_score = ScoringEngine.apply_adjustments(base_score, constraint, db)
            
            # Normalize to 0-10 scale
            final_score = ScoringEngine.normalize_score(adjusted_score)
            
            scores[db] = final_score
        
        return scores

    @staticmethod
    def calculate_data_structure_match(db: str, constraint: Constraint) -> float:
        """Calculate data structure match score (0-1)."""
        profile = ScoringEngine.DATABASE_PROFILES[db]
        return profile["data_structure_support"].get(constraint.data_structure, 0.0)

    @staticmethod
    def calculate_consistency_match(db: str, constraint: Constraint) -> float:
        """Calculate consistency match score (0-1)."""
        profile = ScoringEngine.DATABASE_PROFILES[db]
        
        if constraint.consistency_level == "Strong":
            return 1.0 if profile["consistency_capability"] == "Strong" else 0.0
        else:  # Eventual
            return 1.0  # All databases support eventual consistency

    @staticmethod
    def calculate_query_flexibility(db: str, constraint: Constraint) -> float:
        """Calculate query flexibility score (0-1)."""
        profile = ScoringEngine.DATABASE_PROFILES[db]
        return profile["query_flexibility"]

    @staticmethod
    def calculate_cost_score(db: str, constraint: Constraint) -> float:
        """Calculate cost score (0-1).
        
        Lower base cost = higher score.
        Adjusted by read/write ratio and scale.
        """
        profile = ScoringEngine.DATABASE_PROFILES[db]
        base_cost = profile["base_cost"]
        
        # Normalize: lower cost = higher score
        # Invert the cost (1 - cost) to make lower cost higher score
        cost_score = 1.0 - base_cost
        
        # Adjust for scale: larger scale favors horizontal scaling
        if constraint.scale_gb > 100:
            if profile["scaling_capability"] == "Horizontal":
                cost_score *= 1.2
            elif profile["scaling_capability"] == "Vertical":
                cost_score *= 0.8
        
        return min(1.0, cost_score)

    @staticmethod
    def calculate_latency_score(db: str, constraint: Constraint) -> float:
        """Calculate latency score (0-1).
        
        Based on how well the database meets latency requirements.
        """
        profile = ScoringEngine.DATABASE_PROFILES[db]
        typical_latency = profile["latency_profile"]["typical"]
        
        # Score based on latency requirement
        if constraint.latency_ms < 1:
            # Ultra-low latency requirement
            return 1.0 if typical_latency < 1 else 0.5
        elif constraint.latency_ms < 5:
            # Low latency requirement
            return 1.0 if typical_latency < 5 else 0.7
        elif constraint.latency_ms < 10:
            # Medium latency requirement
            return 1.0 if typical_latency < 10 else 0.8
        else:
            # High latency tolerance
            return 1.0

    @staticmethod
    def apply_adjustments(base_score: float, constraint: Constraint, db: str) -> float:
        """Apply adjustment multipliers based on constraints."""
        adjusted_score = base_score
        
        # Adjustment 1: If joins are required, boost query flexibility
        if constraint.data_structure == "Relational" and constraint.query_complexity == "Complex":
            profile = ScoringEngine.DATABASE_PROFILES[db]
            if profile["query_flexibility"] > 0.5:  # Good query support
                adjusted_score *= 1.3
            else:
                adjusted_score *= 0.5  # Penalize poor query support
        
        # Adjustment 2: If strong consistency required, boost consistency score
        if constraint.consistency_level == "Strong":
            profile = ScoringEngine.DATABASE_PROFILES[db]
            if profile["consistency_capability"] == "Strong":
                adjusted_score *= 1.2
        
        # Adjustment 3: If large scale, boost horizontal scaling capability
        if constraint.scale_gb > 100:
            profile = ScoringEngine.DATABASE_PROFILES[db]
            if profile["scaling_capability"] == "Horizontal":
                adjusted_score *= 1.15
            elif profile["scaling_capability"] == "Limited":
                adjusted_score *= 0.7
        
        return adjusted_score

    @staticmethod
    def normalize_score(score: float) -> float:
        """Normalize score to 0-10 scale.
        
        Input score is in 0-1 range (from weighted sum of component scores).
        Output should be in 0-10 range.
        """
        # Scale from 0-1 range to 0-10 range
        scaled = score * 10.0
        # Clamp to ensure it stays within 0-10
        clamped = max(0.0, min(10.0, scaled))
        return round(clamped, 1)
