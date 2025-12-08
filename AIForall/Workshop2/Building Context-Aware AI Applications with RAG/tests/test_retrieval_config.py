"""Tests for Retrieval Configuration Management"""

import pytest
import json
import tempfile
from pathlib import Path
from src.retrieval_config import (
    RetrievalType,
    SimilarityMetric,
    VectorSearchConfig,
    KeywordSearchConfig,
    HybridSearchConfig,
    MetadataFilterConfig,
    RetrievalConfiguration,
    RetrievalConfigurationManager
)
import os

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestVectorSearchConfig:
    """Tests for VectorSearchConfig"""

    def test_default_config(self):
        """Test default vector search configuration"""
        config = VectorSearchConfig()
        assert config.enabled is True
        assert config.vector_field_name == "embedding"
        assert config.vector_dimension == 1536
        assert config.similarity_metric == SimilarityMetric.COSINE

    def test_custom_config(self):
        """Test custom vector search configuration"""
        config = VectorSearchConfig(
            vector_dimension=768,
            similarity_metric=SimilarityMetric.EUCLIDEAN,
            k=10
        )
        assert config.vector_dimension == 768
        assert config.similarity_metric == SimilarityMetric.EUCLIDEAN
        assert config.k == 10

    def test_validation_invalid_dimension(self):
        """Test validation with invalid vector dimension"""
        config = VectorSearchConfig(vector_dimension=512)
        with pytest.raises(ValueError, match="Invalid vector dimension"):
            config.validate()

    def test_validation_invalid_k(self):
        """Test validation with invalid k"""
        config = VectorSearchConfig(k=0)
        with pytest.raises(ValueError, match="k must be greater than 0"):
            config.validate()

    def test_to_dict(self):
        """Test converting to dictionary"""
        config = VectorSearchConfig()
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict["vector_dimension"] == 1536
        assert config_dict["similarity_metric"] == "cosine"

    def test_from_dict(self):
        """Test creating from dictionary"""
        data = {
            "enabled": True,
            "vector_dimension": 768,
            "similarity_metric": "euclidean",
            "k": 10
        }
        config = VectorSearchConfig.from_dict(data)
        assert config.vector_dimension == 768
        assert config.similarity_metric == SimilarityMetric.EUCLIDEAN


class TestKeywordSearchConfig:
    """Tests for KeywordSearchConfig"""

    def test_default_config(self):
        """Test default keyword search configuration"""
        config = KeywordSearchConfig()
        assert config.enabled is True
        assert config.fuzziness == "AUTO"
        assert config.boost == 1.0

    def test_validation_invalid_fuzziness(self):
        """Test validation with invalid fuzziness"""
        config = KeywordSearchConfig(fuzziness="INVALID")
        with pytest.raises(ValueError, match="Invalid fuzziness"):
            config.validate()

    def test_validation_invalid_boost(self):
        """Test validation with invalid boost"""
        config = KeywordSearchConfig(boost=0)
        with pytest.raises(ValueError, match="boost must be greater than 0"):
            config.validate()


class TestHybridSearchConfig:
    """Tests for HybridSearchConfig"""

    def test_default_config(self):
        """Test default hybrid search configuration"""
        config = HybridSearchConfig()
        assert config.enabled is True
        assert config.vector_weight == 0.5
        assert config.text_weight == 0.5

    def test_validation_invalid_weights(self):
        """Test validation with invalid weights"""
        config = HybridSearchConfig(vector_weight=1.5)
        with pytest.raises(ValueError, match="vector_weight must be between"):
            config.validate()

    def test_validation_zero_weights(self):
        """Test validation with zero weights"""
        config = HybridSearchConfig(vector_weight=0.0, text_weight=0.0)
        with pytest.raises(ValueError, match="At least one weight must be greater than 0"):
            config.validate()


class TestMetadataFilterConfig:
    """Tests for MetadataFilterConfig"""

    def test_default_config(self):
        """Test default metadata filter configuration"""
        config = MetadataFilterConfig()
        assert config.enabled is True
        assert config.filters == {}

    def test_add_filter(self):
        """Test adding a filter"""
        config = MetadataFilterConfig()
        config.add_filter("source", "s3")
        assert config.filters["source"] == "s3"

    def test_remove_filter(self):
        """Test removing a filter"""
        config = MetadataFilterConfig()
        config.add_filter("source", "s3")
        config.remove_filter("source")
        assert "source" not in config.filters

    def test_clear_filters(self):
        """Test clearing all filters"""
        config = MetadataFilterConfig()
        config.add_filter("source", "s3")
        config.add_filter("author", "test")
        config.clear_filters()
        assert config.filters == {}


class TestRetrievalConfiguration:
    """Tests for RetrievalConfiguration"""

    def test_default_config(self):
        """Test default retrieval configuration"""
        config = RetrievalConfiguration()
        assert config.retrieval_type == RetrievalType.SEMANTIC
        assert config.min_relevance_score == 0.0
        assert config.max_results == 5

    def test_validation_success(self):
        """Test successful validation"""
        config = RetrievalConfiguration()
        assert config.validate() is True

    def test_to_dict(self):
        """Test converting to dictionary"""
        config = RetrievalConfiguration()
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict["retrieval_type"] == "semantic"
        assert config_dict["max_results"] == 5

    def test_to_json(self):
        """Test converting to JSON"""
        config = RetrievalConfiguration()
        json_str = config.to_json()
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["retrieval_type"] == "semantic"

    def test_from_dict(self):
        """Test creating from dictionary"""
        data = {
            "retrieval_type": "hybrid",
            "max_results": 10,
            "min_relevance_score": 0.5
        }
        config = RetrievalConfiguration.from_dict(data)
        assert config.retrieval_type == RetrievalType.HYBRID
        assert config.max_results == 10
        assert config.min_relevance_score == 0.5

    def test_from_json(self):
        """Test creating from JSON"""
        json_str = '{"retrieval_type": "keyword", "max_results": 20}'
        config = RetrievalConfiguration.from_json(json_str)
        assert config.retrieval_type == RetrievalType.KEYWORD
        assert config.max_results == 20


class TestRetrievalConfigurationManager:
    """Tests for RetrievalConfigurationManager"""

    def test_init(self):
        """Test manager initialization"""
        manager = RetrievalConfigurationManager()
        assert manager.configurations == {}
        assert manager.default_config is not None

    def test_create_configuration(self):
        """Test creating a configuration"""
        manager = RetrievalConfigurationManager()
        config = manager.create_configuration(
            "test-config",
            retrieval_type=RetrievalType.SEMANTIC
        )
        assert config is not None
        assert "test-config" in manager.configurations

    def test_create_duplicate_configuration(self):
        """Test creating duplicate configuration"""
        manager = RetrievalConfigurationManager()
        manager.create_configuration("test-config")
        with pytest.raises(ValueError, match="already exists"):
            manager.create_configuration("test-config")

    def test_get_configuration(self):
        """Test getting a configuration"""
        manager = RetrievalConfigurationManager()
        manager.create_configuration("test-config")
        config = manager.get_configuration("test-config")
        assert config is not None

    def test_get_nonexistent_configuration(self):
        """Test getting nonexistent configuration"""
        manager = RetrievalConfigurationManager()
        with pytest.raises(ValueError, match="not found"):
            manager.get_configuration("nonexistent")

    def test_update_configuration(self):
        """Test updating a configuration"""
        manager = RetrievalConfigurationManager()
        manager.create_configuration("test-config")
        updated = manager.update_configuration("test-config", max_results=10)
        assert updated.max_results == 10

    def test_delete_configuration(self):
        """Test deleting a configuration"""
        manager = RetrievalConfigurationManager()
        manager.create_configuration("test-config")
        result = manager.delete_configuration("test-config")
        assert result is True
        assert "test-config" not in manager.configurations

    def test_list_configurations(self):
        """Test listing configurations"""
        manager = RetrievalConfigurationManager()
        manager.create_configuration("config-1")
        manager.create_configuration("config-2")
        configs = manager.list_configurations()
        assert len(configs) == 2
        assert "config-1" in configs
        assert "config-2" in configs

    def test_get_all_configurations(self):
        """Test getting all configurations"""
        manager = RetrievalConfigurationManager()
        manager.create_configuration("config-1")
        manager.create_configuration("config-2")
        all_configs = manager.get_all_configurations()
        assert len(all_configs) == 2

    def test_save_and_load_configuration(self):
        """Test saving and loading configuration"""
        manager = RetrievalConfigurationManager()
        manager.create_configuration("test-config", max_results=15)

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "config.json"
            manager.save_configuration_to_file("test-config", str(file_path))
            assert file_path.exists()

            manager2 = RetrievalConfigurationManager()
            loaded = manager2.load_configuration_from_file("loaded-config", str(file_path))
            assert loaded.max_results == 15

    def test_export_configuration(self):
        """Test exporting configuration"""
        manager = RetrievalConfigurationManager()
        manager.create_configuration("test-config")
        json_str = manager.export_configuration("test-config")
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["retrieval_type"] == "semantic"

    def test_import_configuration(self):
        """Test importing configuration"""
        manager = RetrievalConfigurationManager()
        json_str = '{"retrieval_type": "keyword", "max_results": 20}'
        config = manager.import_configuration("imported", json_str)
        assert config.retrieval_type == RetrievalType.KEYWORD
        assert config.max_results == 20

    def test_get_default_configuration(self):
        """Test getting default configuration"""
        manager = RetrievalConfigurationManager()
        default = manager.get_default_configuration()
        assert default is not None

    def test_set_default_configuration(self):
        """Test setting default configuration"""
        manager = RetrievalConfigurationManager()
        manager.create_configuration("test-config", max_results=25)
        manager.set_default_configuration("test-config")
        assert manager.default_config.max_results == 25

    def test_clone_configuration(self):
        """Test cloning configuration"""
        manager = RetrievalConfigurationManager()
        manager.create_configuration("source", max_results=15)
        cloned = manager.clone_configuration("source", "cloned")
        assert cloned.max_results == 15
        assert "cloned" in manager.configurations

    def test_validate_all_configurations(self):
        """Test validating all configurations"""
        manager = RetrievalConfigurationManager()
        manager.create_configuration("config-1")
        manager.create_configuration("config-2")
        results = manager.validate_all_configurations()
        assert len(results) == 2
        assert all(results.values())

    @pytest.mark.parametrize("max_results,retrieval_type", [
        (5, RetrievalType.SEMANTIC),
        (10, RetrievalType.KEYWORD),
        (15, RetrievalType.HYBRID)
    ])
    def test_create_multiple_configurations(self, max_results, retrieval_type):
        """Test creating multiple configurations"""
        manager = RetrievalConfigurationManager()
        config = manager.create_configuration(
            f"config-{max_results}",
            retrieval_type=retrieval_type,
            max_results=max_results
        )
        assert config.max_results == max_results
        assert config.retrieval_type == retrieval_type
