"""Tests for Ingestion Job Management"""

import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from src.ingestion_manager import IngestionJobManager
import os

# Disable hypothesis database to avoid Windows hanging issues
os.environ['HYPOTHESIS_DATABASE_DIRECTORY'] = 'none'


class TestIngestionJobManagerInitialization:
    """Tests for Ingestion Job Manager initialization"""

    def test_init_with_aws_config(self, mock_bedrock_client):
        """Test Ingestion Job Manager initialization with AWS config"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            assert manager.aws_config is config
            assert manager.bedrock_agent_client is mock_bedrock_client

    def test_init_with_none_config(self):
        """Test Ingestion Job Manager initialization with None config"""
        with pytest.raises(ValueError, match="AWS config cannot be None"):
            IngestionJobManager(None)


class TestStartIngestionJob:
    """Tests for starting ingestion jobs"""

    def test_start_ingestion_job_success(self, mock_bedrock_client):
        """Test successful ingestion job start"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.start_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "STARTING",
                "startedAt": "2024-01-01T00:00:00Z",
                "statistics": {
                    "numberOfDocumentsProcessed": 0,
                    "numberOfDocumentsFailed": 0,
                    "numberOfDocumentsSucceeded": 0,
                    "numberOfChunksCreated": 0
                }
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            result = manager.start_ingestion_job(
                kb_id="kb-12345",
                data_source_id="ds-12345",
                description="Test ingestion job"
            )

            assert result["ingestion_job_id"] == "job-12345"
            assert result["kb_id"] == "kb-12345"
            assert result["data_source_id"] == "ds-12345"
            assert result["status"] == "STARTING"

    def test_start_ingestion_job_empty_kb_id(self, mock_bedrock_client):
        """Test ingestion job start with empty KB ID"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(ValueError, match="Knowledge base ID cannot be empty"):
                manager.start_ingestion_job(
                    kb_id="",
                    data_source_id="ds-12345"
                )

    def test_start_ingestion_job_empty_data_source_id(self, mock_bedrock_client):
        """Test ingestion job start with empty data source ID"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(ValueError, match="Data source ID cannot be empty"):
                manager.start_ingestion_job(
                    kb_id="kb-12345",
                    data_source_id=""
                )

    def test_start_ingestion_job_failure(self, mock_bedrock_client):
        """Test ingestion job start failure"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "AccessDenied", "Message": "User is not authorized"}}
        mock_bedrock_client.start_ingestion_job.side_effect = ClientError(error_response, "StartIngestionJob")

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(ValueError, match="Failed to start ingestion job"):
                manager.start_ingestion_job(
                    kb_id="kb-12345",
                    data_source_id="ds-12345"
                )


class TestGetIngestionJob:
    """Tests for retrieving ingestion job information"""

    def test_get_ingestion_job_success(self, mock_bedrock_client):
        """Test successful ingestion job retrieval"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "IN_PROGRESS",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:05:00Z",
                "statistics": {
                    "numberOfDocumentsProcessed": 10,
                    "numberOfDocumentsFailed": 0,
                    "numberOfDocumentsSucceeded": 10,
                    "numberOfChunksCreated": 50
                },
                "failureReasons": []
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            result = manager.get_ingestion_job(
                kb_id="kb-12345",
                data_source_id="ds-12345",
                ingestion_job_id="job-12345"
            )

            assert result["ingestion_job_id"] == "job-12345"
            assert result["status"] == "IN_PROGRESS"
            assert result["statistics"]["numberOfDocumentsProcessed"] == 10

    def test_get_ingestion_job_not_found(self, mock_bedrock_client):
        """Test ingestion job retrieval when job doesn't exist"""
        from config.aws_config import AWSConfig

        error_response = {"Error": {"Code": "ResourceNotFoundException", "Message": "Job not found"}}
        mock_bedrock_client.get_ingestion_job.side_effect = ClientError(error_response, "GetIngestionJob")

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(ValueError, match="not found"):
                manager.get_ingestion_job(
                    kb_id="kb-12345",
                    data_source_id="ds-12345",
                    ingestion_job_id="job-nonexistent"
                )

    def test_get_ingestion_job_empty_kb_id(self, mock_bedrock_client):
        """Test ingestion job retrieval with empty KB ID"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(ValueError, match="Knowledge base ID cannot be empty"):
                manager.get_ingestion_job(
                    kb_id="",
                    data_source_id="ds-12345",
                    ingestion_job_id="job-12345"
                )

    def test_get_ingestion_job_empty_data_source_id(self, mock_bedrock_client):
        """Test ingestion job retrieval with empty data source ID"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(ValueError, match="Data source ID cannot be empty"):
                manager.get_ingestion_job(
                    kb_id="kb-12345",
                    data_source_id="",
                    ingestion_job_id="job-12345"
                )

    def test_get_ingestion_job_empty_job_id(self, mock_bedrock_client):
        """Test ingestion job retrieval with empty job ID"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(ValueError, match="Ingestion job ID cannot be empty"):
                manager.get_ingestion_job(
                    kb_id="kb-12345",
                    data_source_id="ds-12345",
                    ingestion_job_id=""
                )


class TestGetIngestionJobStatus:
    """Tests for retrieving ingestion job status"""

    def test_get_ingestion_job_status_in_progress(self, mock_bedrock_client):
        """Test getting ingestion job status when IN_PROGRESS"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "IN_PROGRESS",
                "startedAt": "2024-01-01T00:00:00Z",
                "statistics": {}
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            status = manager.get_ingestion_job_status(
                kb_id="kb-12345",
                data_source_id="ds-12345",
                ingestion_job_id="job-12345"
            )

            assert status == "IN_PROGRESS"

    def test_get_ingestion_job_status_complete(self, mock_bedrock_client):
        """Test getting ingestion job status when COMPLETE"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "COMPLETE",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:10:00Z",
                "statistics": {}
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            status = manager.get_ingestion_job_status(
                kb_id="kb-12345",
                data_source_id="ds-12345",
                ingestion_job_id="job-12345"
            )

            assert status == "COMPLETE"


class TestWaitForIngestionJobComplete:
    """Tests for waiting for ingestion job completion"""

    def test_wait_for_ingestion_job_complete_success(self, mock_bedrock_client):
        """Test waiting for ingestion job to complete successfully"""
        from config.aws_config import AWSConfig

        # First call returns IN_PROGRESS, second call returns COMPLETE
        mock_bedrock_client.get_ingestion_job.side_effect = [
            {
                "ingestionJob": {
                    "ingestionJobId": "job-12345",
                    "knowledgeBaseId": "kb-12345",
                    "dataSourceId": "ds-12345",
                    "status": "IN_PROGRESS",
                    "startedAt": "2024-01-01T00:00:00Z",
                    "statistics": {}
                }
            },
            {
                "ingestionJob": {
                    "ingestionJobId": "job-12345",
                    "knowledgeBaseId": "kb-12345",
                    "dataSourceId": "ds-12345",
                    "status": "COMPLETE",
                    "startedAt": "2024-01-01T00:00:00Z",
                    "updatedAt": "2024-01-01T00:10:00Z",
                    "statistics": {}
                }
            }
        ]

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            result = manager.wait_for_ingestion_job_complete(
                kb_id="kb-12345",
                data_source_id="ds-12345",
                ingestion_job_id="job-12345",
                max_wait_seconds=60,
                check_interval_seconds=1
            )

            assert result is True

    def test_wait_for_ingestion_job_complete_failure(self, mock_bedrock_client):
        """Test waiting for ingestion job that fails"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "FAILED",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:10:00Z",
                "statistics": {},
                "failureReasons": ["Document parsing failed"]
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(ValueError, match="Ingestion job failed"):
                manager.wait_for_ingestion_job_complete(
                    kb_id="kb-12345",
                    data_source_id="ds-12345",
                    ingestion_job_id="job-12345",
                    max_wait_seconds=60,
                    check_interval_seconds=1
                )

    def test_wait_for_ingestion_job_complete_timeout(self, mock_bedrock_client):
        """Test waiting for ingestion job with timeout"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "IN_PROGRESS",
                "startedAt": "2024-01-01T00:00:00Z",
                "statistics": {}
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            result = manager.wait_for_ingestion_job_complete(
                kb_id="kb-12345",
                data_source_id="ds-12345",
                ingestion_job_id="job-12345",
                max_wait_seconds=1,
                check_interval_seconds=2
            )

            assert result is False

    def test_wait_for_ingestion_job_complete_invalid_max_wait(self, mock_bedrock_client):
        """Test waiting with invalid max_wait_seconds"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(ValueError, match="max_wait_seconds must be greater than 0"):
                manager.wait_for_ingestion_job_complete(
                    kb_id="kb-12345",
                    data_source_id="ds-12345",
                    ingestion_job_id="job-12345",
                    max_wait_seconds=-1
                )


class TestGetIngestionJobResults:
    """Tests for retrieving ingestion job results"""

    def test_get_ingestion_job_results_complete(self, mock_bedrock_client):
        """Test getting results from completed ingestion job"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "COMPLETE",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:10:00Z",
                "statistics": {
                    "numberOfDocumentsProcessed": 100,
                    "numberOfDocumentsFailed": 5,
                    "numberOfDocumentsSucceeded": 95,
                    "numberOfChunksCreated": 500
                },
                "failureReasons": []
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            result = manager.get_ingestion_job_results(
                kb_id="kb-12345",
                data_source_id="ds-12345",
                ingestion_job_id="job-12345"
            )

            assert result["status"] == "COMPLETE"
            assert result["statistics"]["numberOfDocumentsProcessed"] == 100

    def test_get_ingestion_job_results_in_progress(self, mock_bedrock_client):
        """Test getting results from in-progress ingestion job"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "IN_PROGRESS",
                "startedAt": "2024-01-01T00:00:00Z",
                "statistics": {}
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(ValueError, match="Cannot get results for job in IN_PROGRESS status"):
                manager.get_ingestion_job_results(
                    kb_id="kb-12345",
                    data_source_id="ds-12345",
                    ingestion_job_id="job-12345"
                )


class TestListIngestionJobs:
    """Tests for listing ingestion jobs"""

    def test_list_ingestion_jobs_success(self, mock_bedrock_client):
        """Test successful ingestion job listing"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_ingestion_jobs.return_value = {
            "ingestionJobSummaries": [
                {
                    "ingestionJobId": "job-12345",
                    "knowledgeBaseId": "kb-12345",
                    "dataSourceId": "ds-12345",
                    "status": "COMPLETE",
                    "startedAt": "2024-01-01T00:00:00Z",
                    "updatedAt": "2024-01-01T00:10:00Z",
                    "statistics": {}
                },
                {
                    "ingestionJobId": "job-67890",
                    "knowledgeBaseId": "kb-12345",
                    "dataSourceId": "ds-12345",
                    "status": "IN_PROGRESS",
                    "startedAt": "2024-01-02T00:00:00Z",
                    "updatedAt": "2024-01-02T00:05:00Z",
                    "statistics": {}
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            result = manager.list_ingestion_jobs(
                kb_id="kb-12345",
                data_source_id="ds-12345"
            )

            assert len(result) == 2
            assert result[0]["ingestion_job_id"] == "job-12345"
            assert result[1]["ingestion_job_id"] == "job-67890"

    def test_list_ingestion_jobs_empty(self, mock_bedrock_client):
        """Test ingestion job listing when no jobs exist"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_ingestion_jobs.return_value = {"ingestionJobSummaries": []}

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            result = manager.list_ingestion_jobs(
                kb_id="kb-12345",
                data_source_id="ds-12345"
            )

            assert len(result) == 0

    def test_list_ingestion_jobs_with_status_filter(self, mock_bedrock_client):
        """Test ingestion job listing with status filter"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_ingestion_jobs.return_value = {
            "ingestionJobSummaries": [
                {
                    "ingestionJobId": "job-12345",
                    "knowledgeBaseId": "kb-12345",
                    "dataSourceId": "ds-12345",
                    "status": "COMPLETE",
                    "startedAt": "2024-01-01T00:00:00Z",
                    "statistics": {}
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            result = manager.list_ingestion_jobs(
                kb_id="kb-12345",
                data_source_id="ds-12345",
                status_filter="COMPLETE"
            )

            assert len(result) == 1
            assert result[0]["status"] == "COMPLETE"

    def test_list_ingestion_jobs_invalid_status_filter(self, mock_bedrock_client):
        """Test ingestion job listing with invalid status filter"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(ValueError, match="Invalid status filter"):
                manager.list_ingestion_jobs(
                    kb_id="kb-12345",
                    data_source_id="ds-12345",
                    status_filter="INVALID"
                )


class TestGetLatestIngestionJob:
    """Tests for retrieving the latest ingestion job"""

    def test_get_latest_ingestion_job_success(self, mock_bedrock_client):
        """Test getting the latest ingestion job"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_ingestion_jobs.return_value = {
            "ingestionJobSummaries": [
                {
                    "ingestionJobId": "job-12345",
                    "knowledgeBaseId": "kb-12345",
                    "dataSourceId": "ds-12345",
                    "status": "COMPLETE",
                    "startedAt": "2024-01-01T00:00:00Z",
                    "statistics": {}
                },
                {
                    "ingestionJobId": "job-67890",
                    "knowledgeBaseId": "kb-12345",
                    "dataSourceId": "ds-12345",
                    "status": "IN_PROGRESS",
                    "startedAt": "2024-01-02T00:00:00Z",
                    "statistics": {}
                }
            ]
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            result = manager.get_latest_ingestion_job(
                kb_id="kb-12345",
                data_source_id="ds-12345"
            )

            # Should return the most recent job (job-67890)
            assert result["ingestion_job_id"] == "job-67890"

    def test_get_latest_ingestion_job_none(self, mock_bedrock_client):
        """Test getting latest ingestion job when no jobs exist"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.list_ingestion_jobs.return_value = {"ingestionJobSummaries": []}

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            result = manager.get_latest_ingestion_job(
                kb_id="kb-12345",
                data_source_id="ds-12345"
            )

            assert result is None


class TestGetIngestionJobStatistics:
    """Tests for retrieving ingestion job statistics"""

    def test_get_ingestion_job_statistics_success(self, mock_bedrock_client):
        """Test getting ingestion job statistics"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "COMPLETE",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:10:00Z",
                "statistics": {
                    "numberOfDocumentsProcessed": 100,
                    "numberOfDocumentsFailed": 5,
                    "numberOfDocumentsSucceeded": 95,
                    "numberOfChunksCreated": 500,
                    "ingestionDurationSeconds": 600
                }
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            result = manager.get_ingestion_job_statistics(
                kb_id="kb-12345",
                data_source_id="ds-12345",
                ingestion_job_id="job-12345"
            )

            assert result["documents_processed"] == 100
            assert result["documents_failed"] == 5
            assert result["documents_succeeded"] == 95
            assert result["chunks_created"] == 500
            assert result["ingestion_duration_seconds"] == 600


class TestIngestionSummaryGeneration:
    """Tests for ingestion summary generation"""

    def test_generate_ingestion_summary_success(self, mock_bedrock_client):
        """Test generating ingestion summary for successful job"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "COMPLETE",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:10:00Z",
                "statistics": {
                    "numberOfDocumentsProcessed": 100,
                    "numberOfDocumentsFailed": 5,
                    "numberOfDocumentsSucceeded": 95,
                    "numberOfChunksCreated": 500
                },
                "failureReasons": []
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            summary = manager.generate_ingestion_summary(
                kb_id="kb-12345",
                data_source_id="ds-12345",
                ingestion_job_id="job-12345"
            )

            assert summary.total_documents == 100
            assert summary.successful_documents == 95
            assert summary.failed_documents == 5
            assert summary.get_success_rate() == 95.0

    def test_generate_ingestion_summary_with_failures(self, mock_bedrock_client):
        """Test generating ingestion summary with failure reasons"""
        from config.aws_config import AWSConfig

        mock_bedrock_client.get_ingestion_job.return_value = {
            "ingestionJob": {
                "ingestionJobId": "job-12345",
                "knowledgeBaseId": "kb-12345",
                "dataSourceId": "ds-12345",
                "status": "FAILED",
                "startedAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:10:00Z",
                "statistics": {
                    "numberOfDocumentsProcessed": 50,
                    "numberOfDocumentsFailed": 50,
                    "numberOfDocumentsSucceeded": 0,
                    "numberOfChunksCreated": 0
                },
                "failureReasons": ["Document parsing failed", "Invalid format"]
            }
        }

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            summary = manager.generate_ingestion_summary(
                kb_id="kb-12345",
                data_source_id="ds-12345",
                ingestion_job_id="job-12345"
            )

            assert summary.total_documents == 50
            assert summary.failed_documents == 50
            assert len(summary.error_logs) == 2


class TestErrorHandling:
    """Tests for error handling methods"""

    def test_handle_malformed_document(self, mock_bedrock_client):
        """Test handling malformed document"""
        from config.aws_config import AWSConfig
        from src.error_handler import MalformedDocumentError

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(MalformedDocumentError):
                manager.handle_malformed_document(
                    document_id="doc-1",
                    error_message="Missing required field",
                    document_content="<invalid>"
                )

            error_logs = manager.get_error_logs()
            assert len(error_logs) == 1
            assert error_logs[0]["error_type"] == "MalformedDocument"

    def test_handle_ingestion_error(self, mock_bedrock_client):
        """Test handling ingestion error"""
        from config.aws_config import AWSConfig
        from src.error_handler import IngestionError

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(IngestionError):
                manager.handle_ingestion_error(
                    document_id="doc-1",
                    error_message="Failed to parse document"
                )

            error_logs = manager.get_error_logs()
            assert len(error_logs) == 1

    def test_handle_api_error(self, mock_bedrock_client):
        """Test handling API error"""
        from config.aws_config import AWSConfig
        from src.error_handler import APIError

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            with pytest.raises(APIError):
                manager.handle_api_error(
                    operation="StartIngestionJob",
                    error_message="Service unavailable",
                    error_code="ServiceUnavailable",
                    is_retryable=True
                )

            error_logs = manager.get_error_logs()
            assert len(error_logs) == 1

    def test_get_error_summary(self, mock_bedrock_client):
        """Test getting error summary"""
        from config.aws_config import AWSConfig
        from src.error_handler import MalformedDocumentError

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            try:
                manager.handle_malformed_document("doc-1", "Error 1")
            except:
                pass

            try:
                manager.handle_malformed_document("doc-2", "Error 2")
            except:
                pass

            summary = manager.get_error_summary()

            assert summary["total_errors"] == 2
            assert "MalformedDocument" in summary["errors_by_type"]

    def test_clear_error_logs(self, mock_bedrock_client):
        """Test clearing error logs"""
        from config.aws_config import AWSConfig
        from src.error_handler import MalformedDocumentError

        with patch.object(AWSConfig, 'get_client') as mock_get_client:
            mock_get_client.return_value = mock_bedrock_client
            config = AWSConfig()
            manager = IngestionJobManager(config)

            try:
                manager.handle_malformed_document("doc-1", "Error")
            except:
                pass

            assert len(manager.get_error_logs()) == 1

            manager.clear_error_logs()
            assert len(manager.get_error_logs()) == 0
