"""Ingestion job management for Bedrock RAG Retrieval System"""

import time
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig
from src.error_handler import (
    ErrorHandler,
    IngestionSummary,
    ErrorSeverity,
    MalformedDocumentError,
    IngestionError,
    APIError
)


class IngestionJobManager:
    """Manages ingestion jobs for document processing in Bedrock Knowledge Bases"""

    # Default configuration values
    DEFAULT_MAX_WAIT_SECONDS = 3600  # 1 hour
    DEFAULT_CHECK_INTERVAL_SECONDS = 10

    def __init__(self, aws_config: AWSConfig, error_handler: Optional[ErrorHandler] = None):
        """
        Initialize Ingestion Job Manager.

        Args:
            aws_config: AWSConfig instance for AWS client management
            error_handler: Optional ErrorHandler instance for error management

        Raises:
            ValueError: If AWS config is invalid
        """
        if not aws_config:
            raise ValueError("AWS config cannot be None")

        self.aws_config = aws_config
        self.bedrock_agent_client = aws_config.get_client("bedrock-agent")
        self.error_handler = error_handler or ErrorHandler()

    def start_ingestion_job(
        self,
        kb_id: str,
        data_source_id: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start an ingestion job for a data source.

        This method initiates the ingestion process for documents in a data source,
        which will be processed and added to the knowledge base's vector store.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source to ingest from
            description: Optional description of the ingestion job

        Returns:
            Dictionary containing ingestion job information with keys:
            - ingestion_job_id: str - Unique identifier for the job
            - kb_id: str - Knowledge base ID
            - data_source_id: str - Data source ID
            - status: str - Current job status (STARTING, IN_PROGRESS, COMPLETE, FAILED)
            - started_at: str - ISO timestamp when job started
            - statistics: dict - Job statistics (documents_processed, documents_failed, etc.)

        Raises:
            ValueError: If parameters are invalid or job cannot be started
        """
        # Validate inputs
        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        if not data_source_id or len(data_source_id.strip()) == 0:
            raise ValueError("Data source ID cannot be empty")

        try:
            response = self.bedrock_agent_client.start_ingestion_job(
                knowledgeBaseId=kb_id,
                dataSourceId=data_source_id,
                description=description or f"Ingestion job for {data_source_id}"
            )

            job = response.get("ingestionJob", {})
            return {
                "ingestion_job_id": job.get("ingestionJobId"),
                "kb_id": job.get("knowledgeBaseId"),
                "data_source_id": job.get("dataSourceId"),
                "status": job.get("status"),
                "started_at": job.get("startedAt"),
                "statistics": job.get("statistics", {})
            }
        except ClientError as e:
            raise ValueError(f"Failed to start ingestion job: {str(e)}")

    def get_ingestion_job(
        self,
        kb_id: str,
        data_source_id: str,
        ingestion_job_id: str
    ) -> Dict[str, Any]:
        """
        Get information about an ingestion job.

        This method retrieves the current status and details of an ingestion job,
        including statistics about documents processed and any failures.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source
            ingestion_job_id: ID of the ingestion job

        Returns:
            Dictionary containing ingestion job information with keys:
            - ingestion_job_id: str - Job identifier
            - kb_id: str - Knowledge base ID
            - data_source_id: str - Data source ID
            - status: str - Current job status
            - started_at: str - ISO timestamp when job started
            - updated_at: str - ISO timestamp of last update
            - statistics: dict - Job statistics
            - failure_reasons: List[str] - Any failure reasons if job failed

        Raises:
            ValueError: If parameters are invalid or job cannot be retrieved
        """
        # Validate inputs
        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        if not data_source_id or len(data_source_id.strip()) == 0:
            raise ValueError("Data source ID cannot be empty")

        if not ingestion_job_id or len(ingestion_job_id.strip()) == 0:
            raise ValueError("Ingestion job ID cannot be empty")

        try:
            response = self.bedrock_agent_client.get_ingestion_job(
                knowledgeBaseId=kb_id,
                dataSourceId=data_source_id,
                ingestionJobId=ingestion_job_id
            )

            job = response.get("ingestionJob", {})
            return {
                "ingestion_job_id": job.get("ingestionJobId"),
                "kb_id": job.get("knowledgeBaseId"),
                "data_source_id": job.get("dataSourceId"),
                "status": job.get("status"),
                "started_at": job.get("startedAt"),
                "updated_at": job.get("updatedAt"),
                "statistics": job.get("statistics", {}),
                "failure_reasons": job.get("failureReasons", [])
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Ingestion job '{ingestion_job_id}' not found")
            else:
                raise ValueError(f"Failed to get ingestion job: {str(e)}")

    def get_ingestion_job_status(
        self,
        kb_id: str,
        data_source_id: str,
        ingestion_job_id: str
    ) -> str:
        """
        Get the status of an ingestion job.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source
            ingestion_job_id: ID of the ingestion job

        Returns:
            Status of the ingestion job (STARTING, IN_PROGRESS, COMPLETE, FAILED)

        Raises:
            ValueError: If status cannot be retrieved
        """
        job_info = self.get_ingestion_job(kb_id, data_source_id, ingestion_job_id)
        return job_info.get("status", "UNKNOWN")

    def wait_for_ingestion_job_complete(
        self,
        kb_id: str,
        data_source_id: str,
        ingestion_job_id: str,
        max_wait_seconds: Optional[int] = None,
        check_interval_seconds: Optional[int] = None
    ) -> bool:
        """
        Wait for an ingestion job to complete.

        This method polls the ingestion job status until it reaches a terminal state
        (COMPLETE or FAILED) or the timeout is exceeded.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source
            ingestion_job_id: ID of the ingestion job
            max_wait_seconds: Maximum time to wait (default: 3600 seconds)
            check_interval_seconds: Interval between status checks (default: 10 seconds)

        Returns:
            True if job completes successfully, False if timeout

        Raises:
            ValueError: If job enters FAILED status or parameters are invalid
        """
        max_wait_seconds = max_wait_seconds or self.DEFAULT_MAX_WAIT_SECONDS
        check_interval_seconds = check_interval_seconds or self.DEFAULT_CHECK_INTERVAL_SECONDS

        if max_wait_seconds <= 0:
            raise ValueError("max_wait_seconds must be greater than 0")

        if check_interval_seconds <= 0:
            raise ValueError("check_interval_seconds must be greater than 0")

        elapsed = 0

        while elapsed < max_wait_seconds:
            status = self.get_ingestion_job_status(kb_id, data_source_id, ingestion_job_id)

            if status == "COMPLETE":
                return True
            elif status == "FAILED":
                job_info = self.get_ingestion_job(kb_id, data_source_id, ingestion_job_id)
                failure_reasons = job_info.get("failure_reasons", [])
                raise ValueError(f"Ingestion job failed: {failure_reasons}")

            time.sleep(check_interval_seconds)
            elapsed += check_interval_seconds

        return False

    def get_ingestion_job_results(
        self,
        kb_id: str,
        data_source_id: str,
        ingestion_job_id: str
    ) -> Dict[str, Any]:
        """
        Get the results of a completed ingestion job.

        This method retrieves detailed results from an ingestion job, including
        statistics about documents processed, failed, and any error details.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source
            ingestion_job_id: ID of the ingestion job

        Returns:
            Dictionary containing ingestion job results with keys:
            - ingestion_job_id: str - Job identifier
            - status: str - Final job status
            - statistics: dict - Job statistics including:
              - documents_processed: int - Total documents processed
              - documents_failed: int - Documents that failed to ingest
              - documents_succeeded: int - Documents successfully ingested
              - chunks_created: int - Total chunks created
            - failure_reasons: List[str] - Any failure reasons
            - started_at: str - ISO timestamp when job started
            - updated_at: str - ISO timestamp of completion

        Raises:
            ValueError: If job cannot be retrieved or is not complete
        """
        job_info = self.get_ingestion_job(kb_id, data_source_id, ingestion_job_id)

        status = job_info.get("status")
        if status not in ["COMPLETE", "FAILED"]:
            raise ValueError(
                f"Cannot get results for job in {status} status. "
                "Job must be in COMPLETE or FAILED status."
            )

        return {
            "ingestion_job_id": job_info.get("ingestion_job_id"),
            "status": status,
            "statistics": job_info.get("statistics", {}),
            "failure_reasons": job_info.get("failure_reasons", []),
            "started_at": job_info.get("started_at"),
            "updated_at": job_info.get("updated_at")
        }

    def list_ingestion_jobs(
        self,
        kb_id: str,
        data_source_id: str,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List ingestion jobs for a data source.

        This method retrieves a list of all ingestion jobs for a specific data source,
        optionally filtered by status.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source
            status_filter: Optional status to filter by (STARTING, IN_PROGRESS, COMPLETE, FAILED)

        Returns:
            List of ingestion job information dictionaries

        Raises:
            ValueError: If parameters are invalid or listing fails
        """
        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        if not data_source_id or len(data_source_id.strip()) == 0:
            raise ValueError("Data source ID cannot be empty")

        if status_filter and status_filter not in ["STARTING", "IN_PROGRESS", "COMPLETE", "FAILED"]:
            raise ValueError(f"Invalid status filter: {status_filter}")

        try:
            response = self.bedrock_agent_client.list_ingestion_jobs(
                knowledgeBaseId=kb_id,
                dataSourceId=data_source_id,
                filters=[
                    {
                        "attribute": "STATUS",
                        "operator": "EQ",
                        "value": status_filter
                    }
                ] if status_filter else []
            )

            jobs = []
            for job_summary in response.get("ingestionJobSummaries", []):
                jobs.append({
                    "ingestion_job_id": job_summary.get("ingestionJobId"),
                    "kb_id": job_summary.get("knowledgeBaseId"),
                    "data_source_id": job_summary.get("dataSourceId"),
                    "status": job_summary.get("status"),
                    "started_at": job_summary.get("startedAt"),
                    "updated_at": job_summary.get("updatedAt"),
                    "statistics": job_summary.get("statistics", {})
                })

            return jobs
        except ClientError as e:
            raise ValueError(f"Failed to list ingestion jobs: {str(e)}")

    def get_latest_ingestion_job(
        self,
        kb_id: str,
        data_source_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent ingestion job for a data source.

        This method retrieves the latest ingestion job, which is useful for
        checking the status of the most recent ingestion attempt.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source

        Returns:
            Dictionary containing the latest ingestion job information, or None if no jobs exist

        Raises:
            ValueError: If parameters are invalid or retrieval fails
        """
        try:
            jobs = self.list_ingestion_jobs(kb_id, data_source_id)

            if not jobs:
                return None

            # Sort by started_at timestamp (most recent first)
            sorted_jobs = sorted(
                jobs,
                key=lambda x: x.get("started_at", ""),
                reverse=True
            )

            return sorted_jobs[0]
        except ValueError:
            raise

    def get_ingestion_job_statistics(
        self,
        kb_id: str,
        data_source_id: str,
        ingestion_job_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed statistics for an ingestion job.

        This method extracts and returns the statistics from an ingestion job,
        providing insights into the ingestion process.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source
            ingestion_job_id: ID of the ingestion job

        Returns:
            Dictionary containing ingestion statistics with keys:
            - documents_processed: int - Total documents processed
            - documents_failed: int - Documents that failed
            - documents_succeeded: int - Documents successfully ingested
            - chunks_created: int - Total chunks created
            - ingestion_duration_seconds: int - Time taken for ingestion

        Raises:
            ValueError: If job cannot be retrieved
        """
        job_info = self.get_ingestion_job(kb_id, data_source_id, ingestion_job_id)
        statistics = job_info.get("statistics", {})

        return {
            "documents_processed": statistics.get("numberOfDocumentsProcessed", 0),
            "documents_failed": statistics.get("numberOfDocumentsFailed", 0),
            "documents_succeeded": statistics.get("numberOfDocumentsSucceeded", 0),
            "chunks_created": statistics.get("numberOfChunksCreated", 0),
            "ingestion_duration_seconds": statistics.get("ingestionDurationSeconds", 0)
        }

    def generate_ingestion_summary(
        self,
        kb_id: str,
        data_source_id: str,
        ingestion_job_id: str
    ) -> IngestionSummary:
        """
        Generate a comprehensive ingestion summary report.

        This method retrieves ingestion job results and creates a detailed summary
        including statistics, error information, and success/failure rates.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source
            ingestion_job_id: ID of the ingestion job

        Returns:
            IngestionSummary object containing detailed ingestion results

        Raises:
            ValueError: If job cannot be retrieved
        """
        job_info = self.get_ingestion_job(kb_id, data_source_id, ingestion_job_id)
        statistics = job_info.get("statistics", {})
        failure_reasons = job_info.get("failure_reasons", [])

        summary = IngestionSummary()
        summary.total_documents = statistics.get("numberOfDocumentsProcessed", 0)
        summary.successful_documents = statistics.get("numberOfDocumentsSucceeded", 0)
        summary.failed_documents = statistics.get("numberOfDocumentsFailed", 0)

        # Add failure reasons as errors to the summary
        for reason in failure_reasons:
            summary.add_error(
                error_type="IngestionFailure",
                message=reason,
                severity=ErrorSeverity.ERROR,
                context={"ingestion_job_id": ingestion_job_id}
            )

        return summary

    def handle_malformed_document(
        self,
        document_id: str,
        error_message: str,
        document_content: Optional[str] = None
    ) -> None:
        """
        Handle a malformed document during ingestion.

        This method logs the malformed document error and continues processing.
        The document is skipped and not added to the knowledge base.

        Args:
            document_id: ID of the malformed document
            error_message: Description of what's wrong with the document
            document_content: Optional content of the document for debugging

        Raises:
            MalformedDocumentError: Always raised to signal document skip
        """
        self.error_handler.handle_malformed_document(
            document_id=document_id,
            error_message=error_message,
            document_content=document_content
        )
        raise MalformedDocumentError(
            f"Document {document_id} is malformed: {error_message}"
        )

    def handle_ingestion_error(
        self,
        document_id: str,
        error_message: str,
        error_type: str = "IngestionError"
    ) -> None:
        """
        Handle an ingestion error for a document.

        This method logs the ingestion error and continues processing.
        The document is skipped and not added to the knowledge base.

        Args:
            document_id: ID of the document that failed ingestion
            error_message: Description of the ingestion error
            error_type: Type of ingestion error

        Raises:
            IngestionError: Always raised to signal document skip
        """
        self.error_handler.handle_ingestion_error(
            document_id=document_id,
            error_message=error_message,
            error_type=error_type
        )
        raise IngestionError(
            f"Failed to ingest document {document_id}: {error_message}"
        )

    def handle_api_error(
        self,
        operation: str,
        error_message: str,
        error_code: Optional[str] = None,
        is_retryable: bool = False
    ) -> None:
        """
        Handle an API error during ingestion operations.

        This method logs the API error with context about whether it's retryable.

        Args:
            operation: Name of the operation that failed
            error_message: Description of the API error
            error_code: Optional error code from the API
            is_retryable: Whether the error is retryable

        Raises:
            APIError: Always raised to signal operation failure
        """
        self.error_handler.handle_api_error(
            operation=operation,
            error_message=error_message,
            error_code=error_code,
            is_retryable=is_retryable
        )
        raise APIError(
            f"API error during {operation}: {error_message}"
        )

    def get_error_logs(self) -> List[Dict[str, Any]]:
        """
        Get all error logs from the error handler.

        Returns:
            List of error log dictionaries
        """
        return [log.to_dict() for log in self.error_handler.get_error_logs()]

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all errors encountered.

        Returns:
            Dictionary containing error summary statistics
        """
        return self.error_handler.get_error_summary()

    def clear_error_logs(self) -> None:
        """Clear all error logs from the error handler"""
        self.error_handler.clear_error_logs()
