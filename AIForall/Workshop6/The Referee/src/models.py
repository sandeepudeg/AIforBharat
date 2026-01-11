"""Data models for Database Referee."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class Constraint(BaseModel):
    """User constraints for database selection."""

    data_structure: str = Field(
        ...,
        description="Type of data structure",
        json_schema_extra={"enum": ["Relational", "JSON", "Key-Value"]}
    )
    read_write_ratio: int = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of read operations (0-100)"
    )
    consistency_level: str = Field(
        ...,
        description="Consistency requirement",
        json_schema_extra={"enum": ["Strong", "Eventual"]}
    )
    query_complexity: str = Field(
        ...,
        description="Complexity of queries",
        json_schema_extra={"enum": ["Simple", "Moderate", "Complex"]}
    )
    scale_gb: float = Field(
        ...,
        gt=0,
        description="Data scale in GB"
    )
    latency_ms: float = Field(
        ...,
        gt=0,
        description="Required latency in milliseconds"
    )
    team_expertise: str = Field(
        ...,
        description="Team expertise level",
        json_schema_extra={"enum": ["Low", "Medium", "High"]}
    )
    requires_persistence: bool = Field(
        default=True,
        description="Whether data persistence is critical"
    )

    @field_validator("data_structure")
    @classmethod
    def validate_data_structure(cls, v: str) -> str:
        """Validate data structure is one of allowed values."""
        allowed = ["Relational", "JSON", "Key-Value"]
        if v not in allowed:
            raise ValueError(f"data_structure must be one of {allowed}, got {v}")
        return v

    @field_validator("consistency_level")
    @classmethod
    def validate_consistency_level(cls, v: str) -> str:
        """Validate consistency level is one of allowed values."""
        allowed = ["Strong", "Eventual"]
        if v not in allowed:
            raise ValueError(f"consistency_level must be one of {allowed}, got {v}")
        return v

    @field_validator("query_complexity")
    @classmethod
    def validate_query_complexity(cls, v: str) -> str:
        """Validate query complexity is one of allowed values."""
        allowed = ["Simple", "Moderate", "Complex"]
        if v not in allowed:
            raise ValueError(f"query_complexity must be one of {allowed}, got {v}")
        return v

    @field_validator("team_expertise")
    @classmethod
    def validate_team_expertise(cls, v: str) -> str:
        """Validate team expertise is one of allowed values."""
        allowed = ["Low", "Medium", "High"]
        if v not in allowed:
            raise ValueError(f"team_expertise must be one of {allowed}, got {v}")
        return v


class DatabaseProfile(BaseModel):
    """Profile of a database option."""

    name: str
    data_structure_support: Dict[str, float]  # {structure: compatibility_score}
    consistency_capability: str  # "Strong" or "Eventual"
    query_flexibility: float  # 0-1 scale
    base_cost: float  # Relative cost score
    latency_profile: Dict[str, float]  # {scenario: latency_ms}
    scaling_capability: str  # "Vertical", "Horizontal", "Limited"
    persistence: bool
    max_scale_gb: float


class Report(BaseModel):
    """Final recommendation report."""

    winner: str
    score: float
    rationale: str
    pros: List[str]
    cons: List[str]
    disqualified: Dict[str, str]  # {db_name: reason}
    alternatives: Dict[str, Dict]  # {db_name: {pros, cons}}
    score_breakdown: Dict[str, float]
    comparison_table: Optional[Dict] = None


class ValidationError(BaseModel):
    """Validation error response."""

    field: str
    message: str
    valid_range: Optional[str] = None
