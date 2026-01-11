"""Disqualification engine for database selection."""

from typing import List, Dict, Tuple
from src.models import Constraint


class DisqualificationEngine:
    """Applies hard rules to eliminate unsuitable databases."""

    # Available databases
    DATABASES = ["PostgreSQL", "DynamoDB", "Redis"]

    @staticmethod
    def disqualify(constraint: Constraint) -> Tuple[List[str], Dict[str, str]]:
        """Apply disqualification rules to eliminate unsuitable databases.
        
        Args:
            constraint: User constraints
            
        Returns:
            Tuple of (remaining_databases, disqualified_reasons)
        """
        remaining = set(DisqualificationEngine.DATABASES)
        disqualified = {}
        
        # Rule 1: Joins required → Disqualify DynamoDB
        if DisqualificationEngine._requires_joins(constraint):
            if "DynamoDB" in remaining:
                remaining.remove("DynamoDB")
                disqualified["DynamoDB"] = "Cannot perform joins efficiently. Your primary use case requires relational queries."
        
        # Rule 2: Strong consistency → Disqualify DynamoDB
        if DisqualificationEngine._requires_strong_consistency(constraint):
            if "DynamoDB" in remaining:
                remaining.remove("DynamoDB")
                disqualified["DynamoDB"] = "Limited ACID support. You require strong consistency."
        
        # Rule 3: Persistence critical → Disqualify Redis
        if DisqualificationEngine._requires_persistence(constraint):
            if "Redis" in remaining:
                remaining.remove("Redis")
                disqualified["Redis"] = "Not suitable for persistent relational data. Designed for caching, not primary storage."
        
        # Rule 4: Scale > 10GB → Disqualify Redis
        if DisqualificationEngine._exceeds_redis_scale_limit(constraint):
            if "Redis" in remaining:
                remaining.remove("Redis")
                disqualified["Redis"] = "In-memory storage. Your data scale exceeds memory constraints."
        
        # Rule 5: Latency < 1ms → Disqualify PostgreSQL
        if DisqualificationEngine._requires_ultra_low_latency(constraint):
            if "PostgreSQL" in remaining:
                remaining.remove("PostgreSQL")
                disqualified["PostgreSQL"] = "Cannot achieve sub-1ms latency. Requires network round-trip."
        
        return list(remaining), disqualified

    @staticmethod
    def _requires_joins(constraint: Constraint) -> bool:
        """Check if joins are required.
        
        Joins are required when:
        - Data structure is Relational AND
        - Query complexity is Complex
        """
        return (
            constraint.data_structure == "Relational" and
            constraint.query_complexity == "Complex"
        )

    @staticmethod
    def _requires_strong_consistency(constraint: Constraint) -> bool:
        """Check if strong consistency is required."""
        return constraint.consistency_level == "Strong"

    @staticmethod
    def _requires_persistence(constraint: Constraint) -> bool:
        """Check if data persistence is critical."""
        return constraint.requires_persistence

    @staticmethod
    def _exceeds_redis_scale_limit(constraint: Constraint) -> bool:
        """Check if data scale exceeds Redis practical limit (10GB)."""
        return constraint.scale_gb > 10

    @staticmethod
    def _requires_ultra_low_latency(constraint: Constraint) -> bool:
        """Check if latency requirement is < 1ms."""
        return constraint.latency_ms < 1
