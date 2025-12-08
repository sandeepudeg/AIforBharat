"""Retrieval configuration management for Bedrock RAG Retrieval System"""

import json
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, asdict, field
from pathlib import Path
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig


class RetrievalType(Enum):
    """Enumeration of retrieval types"""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"


class SimilarityMetric(Enum):
    """Enumeration of similarity metrics for vector search"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    INNERPRODUCT = "innerproduct"


@dataclass
class VectorSearchConfig:
    """Configuration for vector search"""
    enabled: bool = True
    vector_field_name: str = "embedding"
    vector_dimension: int = 1536
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    k: int = 5
    ef_construction: int = 256
    m: int = 16

    def validate(self) -> bool:
        """
        Validate vector search configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if self.vector_dimension not in [384, 768, 1024, 1536, 3072]:
            raise ValueError(
                f"Invalid vector dimension {self.vector_dimension}. "
                "Supported dimensions: 384, 768, 1024, 1536, 3072"
            )

        if self.k <= 0:
            raise ValueError("k must be greater than 0")

        if self.ef_construction <= 0:
            raise ValueError("ef_construction must be greater than 0")

        if self.m <= 0:
            raise ValueError("m must be greater than 0")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["similarity_metric"] = self.similarity_metric.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorSearchConfig":
        """Create from dictionary"""
        if "similarity_metric" in data and isinstance(data["similarity_metric"], str):
            data["similarity_metric"] = SimilarityMetric(data["similarity_metric"])
        return cls(**data)


@dataclass
class KeywordSearchConfig:
    """Configuration for keyword search"""
    enabled: bool = True
    fuzziness: str = "AUTO"
    boost: float = 1.0
    max_results: int = 5

    def validate(self) -> bool:
        """
        Validate keyword search configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if self.fuzziness not in ["AUTO", "0", "1", "2"]:
            raise ValueError(
                f"Invalid fuzziness {self.fuzziness}. "
                "Supported values: AUTO, 0, 1, 2"
            )

        if self.boost <= 0:
            raise ValueError("boost must be greater than 0")

        if self.max_results <= 0:
            raise ValueError("max_results must be greater than 0")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeywordSearchConfig":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class HybridSearchConfig:
    """Configuration for hybrid search"""
    enabled: bool = True
    vector_weight: float = 0.5
    text_weight: float = 0.5
    max_results: int = 5

    def validate(self) -> bool:
        """
        Validate hybrid search configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if self.vector_weight < 0.0 or self.vector_weight > 1.0:
            raise ValueError("vector_weight must be between 0.0 and 1.0")

        if self.text_weight < 0.0 or self.text_weight > 1.0:
            raise ValueError("text_weight must be between 0.0 and 1.0")

        if self.max_results <= 0:
            raise ValueError("max_results must be greater than 0")

        # Normalize weights
        total_weight = self.vector_weight + self.text_weight
        if total_weight == 0:
            raise ValueError("At least one weight must be greater than 0")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HybridSearchConfig":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class MetadataFilterConfig:
    """Configuration for metadata filtering"""
    enabled: bool = True
    filters: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        """
        Validate metadata filter configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if not isinstance(self.filters, dict):
            raise ValueError("filters must be a dictionary")

        return True

    def add_filter(self, key: str, value: Any) -> None:
        """Add a metadata filter"""
        self.filters[key] = value

    def remove_filter(self, key: str) -> None:
        """Remove a metadata filter"""
        if key in self.filters:
            del self.filters[key]

    def clear_filters(self) -> None:
        """Clear all metadata filters"""
        self.filters.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetadataFilterConfig":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class RetrievalConfiguration:
    """Complete retrieval configuration"""
    retrieval_type: RetrievalType = RetrievalType.SEMANTIC
    vector_search: VectorSearchConfig = field(default_factory=VectorSearchConfig)
    keyword_search: KeywordSearchConfig = field(default_factory=KeywordSearchConfig)
    hybrid_search: HybridSearchConfig = field(default_factory=HybridSearchConfig)
    metadata_filters: MetadataFilterConfig = field(default_factory=MetadataFilterConfig)
    min_relevance_score: float = 0.0
    max_results: int = 5
    timeout_seconds: int = 30

    def validate(self) -> bool:
        """
        Validate complete retrieval configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        self.vector_search.validate()
        self.keyword_search.validate()
        self.hybrid_search.validate()
        self.metadata_filters.validate()

        if self.min_relevance_score < 0.0 or self.min_relevance_score > 1.0:
            raise ValueError("min_relevance_score must be between 0.0 and 1.0")

        if self.max_results <= 0:
            raise ValueError("max_results must be greater than 0")

        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "retrieval_type": self.retrieval_type.value,
            "vector_search": self.vector_search.to_dict(),
            "keyword_search": self.keyword_search.to_dict(),
            "hybrid_search": self.hybrid_search.to_dict(),
            "metadata_filters": self.metadata_filters.to_dict(),
            "min_relevance_score": self.min_relevance_score,
            "max_results": self.max_results,
            "timeout_seconds": self.timeout_seconds
        }

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RetrievalConfiguration":
        """Create from dictionary"""
        if "retrieval_type" in data and isinstance(data["retrieval_type"], str):
            data["retrieval_type"] = RetrievalType(data["retrieval_type"])

        if "vector_search" in data:
            data["vector_search"] = VectorSearchConfig.from_dict(data["vector_search"])

        if "keyword_search" in data:
            data["keyword_search"] = KeywordSearchConfig.from_dict(data["keyword_search"])

        if "hybrid_search" in data:
            data["hybrid_search"] = HybridSearchConfig.from_dict(data["hybrid_search"])

        if "metadata_filters" in data:
            data["metadata_filters"] = MetadataFilterConfig.from_dict(data["metadata_filters"])

        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "RetrievalConfiguration":
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class RetrievalConfigurationManager:
    """Manages retrieval configurations"""

    def __init__(self, aws_config: Optional[AWSConfig] = None):
        """
        Initialize Retrieval Configuration Manager.

        Args:
            aws_config: Optional AWSConfig instance for AWS operations
        """
        self.aws_config = aws_config
        self.configurations: Dict[str, RetrievalConfiguration] = {}
        self.default_config = RetrievalConfiguration()

    def create_configuration(
        self,
        name: str,
        retrieval_type: RetrievalType = RetrievalType.SEMANTIC,
        **kwargs
    ) -> RetrievalConfiguration:
        """
        Create a new retrieval configuration.

        Args:
            name: Name of the configuration
            retrieval_type: Type of retrieval
            **kwargs: Additional configuration parameters

        Returns:
            Created RetrievalConfiguration

        Raises:
            ValueError: If configuration already exists or is invalid
        """
        if name in self.configurations:
            raise ValueError(f"Configuration '{name}' already exists")

        config = RetrievalConfiguration(retrieval_type=retrieval_type)

        # Apply additional parameters
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        config.validate()
        self.configurations[name] = config

        return config

    def get_configuration(self, name: str) -> RetrievalConfiguration:
        """
        Get a retrieval configuration by name.

        Args:
            name: Name of the configuration

        Returns:
            RetrievalConfiguration

        Raises:
            ValueError: If configuration not found
        """
        if name not in self.configurations:
            raise ValueError(f"Configuration '{name}' not found")

        return self.configurations[name]

    def update_configuration(
        self,
        name: str,
        **kwargs
    ) -> RetrievalConfiguration:
        """
        Update an existing retrieval configuration.

        Args:
            name: Name of the configuration
            **kwargs: Parameters to update

        Returns:
            Updated RetrievalConfiguration

        Raises:
            ValueError: If configuration not found or update is invalid
        """
        if name not in self.configurations:
            raise ValueError(f"Configuration '{name}' not found")

        config = self.configurations[name]

        # Update parameters
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        config.validate()
        return config

    def delete_configuration(self, name: str) -> bool:
        """
        Delete a retrieval configuration.

        Args:
            name: Name of the configuration

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If configuration not found
        """
        if name not in self.configurations:
            raise ValueError(f"Configuration '{name}' not found")

        del self.configurations[name]
        return True

    def list_configurations(self) -> List[str]:
        """
        List all configuration names.

        Returns:
            List of configuration names
        """
        return list(self.configurations.keys())

    def get_all_configurations(self) -> Dict[str, RetrievalConfiguration]:
        """
        Get all configurations.

        Returns:
            Dictionary of all configurations
        """
        return self.configurations.copy()

    def save_configuration_to_file(
        self,
        name: str,
        file_path: str
    ) -> bool:
        """
        Save a configuration to a JSON file.

        Args:
            name: Name of the configuration
            file_path: Path to save the configuration

        Returns:
            True if saved successfully

        Raises:
            ValueError: If configuration not found
        """
        if name not in self.configurations:
            raise ValueError(f"Configuration '{name}' not found")

        config = self.configurations[name]
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(config.to_json())

        return True

    def load_configuration_from_file(
        self,
        name: str,
        file_path: str
    ) -> RetrievalConfiguration:
        """
        Load a configuration from a JSON file.

        Args:
            name: Name to assign to the loaded configuration
            file_path: Path to load the configuration from

        Returns:
            Loaded RetrievalConfiguration

        Raises:
            ValueError: If file cannot be read or configuration is invalid
        """
        try:
            file_path = Path(file_path)
            with open(file_path, 'r') as f:
                json_str = f.read()

            config = RetrievalConfiguration.from_json(json_str)
            config.validate()
            self.configurations[name] = config

            return config
        except FileNotFoundError:
            raise ValueError(f"Configuration file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {str(e)}")

    def export_configuration(self, name: str) -> str:
        """
        Export a configuration as JSON string.

        Args:
            name: Name of the configuration

        Returns:
            JSON string representation

        Raises:
            ValueError: If configuration not found
        """
        if name not in self.configurations:
            raise ValueError(f"Configuration '{name}' not found")

        return self.configurations[name].to_json()

    def import_configuration(self, name: str, json_str: str) -> RetrievalConfiguration:
        """
        Import a configuration from JSON string.

        Args:
            name: Name to assign to the imported configuration
            json_str: JSON string representation

        Returns:
            Imported RetrievalConfiguration

        Raises:
            ValueError: If JSON is invalid or configuration already exists
        """
        if name in self.configurations:
            raise ValueError(f"Configuration '{name}' already exists")

        try:
            config = RetrievalConfiguration.from_json(json_str)
            config.validate()
            self.configurations[name] = config
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")

    def get_default_configuration(self) -> RetrievalConfiguration:
        """
        Get the default retrieval configuration.

        Returns:
            Default RetrievalConfiguration
        """
        return self.default_config

    def set_default_configuration(self, name: str) -> bool:
        """
        Set a configuration as the default.

        Args:
            name: Name of the configuration

        Returns:
            True if set successfully

        Raises:
            ValueError: If configuration not found
        """
        if name not in self.configurations:
            raise ValueError(f"Configuration '{name}' not found")

        self.default_config = self.configurations[name]
        return True

    def clone_configuration(self, source_name: str, target_name: str) -> RetrievalConfiguration:
        """
        Clone an existing configuration.

        Args:
            source_name: Name of the source configuration
            target_name: Name for the cloned configuration

        Returns:
            Cloned RetrievalConfiguration

        Raises:
            ValueError: If source not found or target already exists
        """
        if source_name not in self.configurations:
            raise ValueError(f"Source configuration '{source_name}' not found")

        if target_name in self.configurations:
            raise ValueError(f"Target configuration '{target_name}' already exists")

        source_config = self.configurations[source_name]
        cloned_config = RetrievalConfiguration.from_dict(source_config.to_dict())
        self.configurations[target_name] = cloned_config

        return cloned_config

    def validate_all_configurations(self) -> Dict[str, bool]:
        """
        Validate all configurations.

        Returns:
            Dictionary with configuration names as keys and validation results as values
        """
        results = {}
        for name, config in self.configurations.items():
            try:
                config.validate()
                results[name] = True
            except ValueError:
                results[name] = False

        return results
