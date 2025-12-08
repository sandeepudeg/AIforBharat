"""Health checks and status monitoring for Bedrock RAG Retrieval System"""

import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig


class ComponentStatus(Enum):
    """Status of system components"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class HealthCheckResult:
    """Result of a health check for a component"""

    def __init__(
        self,
        component_name: str,
        status: ComponentStatus,
        message: str = "",
        response_time_ms: Optional[float] = None,
        timestamp: Optional[datetime] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize health check result.

        Args:
            component_name: Name of the component being checked
            status: Status of the component
            message: Optional message describing the status
            response_time_ms: Optional response time in milliseconds
            timestamp: Optional timestamp of the check (defaults to now)
            details: Optional additional details about the component
        """
        self.component_name = component_name
        self.status = status
        self.message = message
        self.response_time_ms = response_time_ms
        self.timestamp = timestamp or datetime.utcnow()
        self.details = details or {}

    def is_healthy(self) -> bool:
        """Check if component is healthy"""
        return self.status == ComponentStatus.HEALTHY

    def is_degraded(self) -> bool:
        """Check if component is degraded"""
        return self.status == ComponentStatus.DEGRADED

    def is_unhealthy(self) -> bool:
        """Check if component is unhealthy"""
        return self.status == ComponentStatus.UNHEALTHY

    def to_dict(self) -> Dict[str, Any]:
        """Convert health check result to dictionary"""
        return {
            "component_name": self.component_name,
            "status": self.status.value,
            "message": self.message,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


class SystemHealthStatus:
    """Overall system health status"""

    def __init__(self):
        """Initialize system health status"""
        self.component_results: List[HealthCheckResult] = []
        self.check_timestamp: Optional[datetime] = None

    def add_result(self, result: HealthCheckResult) -> None:
        """
        Add a component health check result.

        Args:
            result: HealthCheckResult to add
        """
        self.component_results.append(result)

    def get_overall_status(self) -> ComponentStatus:
        """
        Get overall system status based on component statuses.

        Returns:
            Overall system status (HEALTHY, DEGRADED, or UNHEALTHY)
        """
        if not self.component_results:
            return ComponentStatus.UNKNOWN

        # If any component is unhealthy, system is unhealthy
        if any(r.is_unhealthy() for r in self.component_results):
            return ComponentStatus.UNHEALTHY

        # If any component is degraded, system is degraded
        if any(r.is_degraded() for r in self.component_results):
            return ComponentStatus.DEGRADED

        # If all components are healthy, system is healthy
        if all(r.is_healthy() for r in self.component_results):
            return ComponentStatus.HEALTHY

        return ComponentStatus.UNKNOWN

    def get_healthy_components(self) -> List[HealthCheckResult]:
        """Get all healthy components"""
        return [r for r in self.component_results if r.is_healthy()]

    def get_degraded_components(self) -> List[HealthCheckResult]:
        """Get all degraded components"""
        return [r for r in self.component_results if r.is_degraded()]

    def get_unhealthy_components(self) -> List[HealthCheckResult]:
        """Get all unhealthy components"""
        return [r for r in self.component_results if r.is_unhealthy()]

    def to_dict(self) -> Dict[str, Any]:
        """Convert system health status to dictionary"""
        return {
            "overall_status": self.get_overall_status().value,
            "check_timestamp": self.check_timestamp.isoformat() if self.check_timestamp else None,
            "total_components": len(self.component_results),
            "healthy_components": len(self.get_healthy_components()),
            "degraded_components": len(self.get_degraded_components()),
            "unhealthy_components": len(self.get_unhealthy_components()),
            "components": [r.to_dict() for r in self.component_results]
        }


class HealthCheckManager:
    """Manages health checks for all system components"""

    def __init__(self, aws_config: AWSConfig):
        """
        Initialize Health Check Manager.

        Args:
            aws_config: AWSConfig instance for AWS client management
        """
        self.aws_config = aws_config
        self.bedrock_agent_client = aws_config.get_client("bedrock-agent")
        self.opensearch_client = aws_config.get_client("opensearchserverless")
        self.s3_client = aws_config.get_client("s3")
        self.region = aws_config.get_region()

    def check_knowledge_base_availability(
        self,
        kb_id: str,
        timeout_seconds: int = 5
    ) -> HealthCheckResult:
        """
        Check if a knowledge base is available and responsive.

        Args:
            kb_id: ID of the knowledge base to check
            timeout_seconds: Timeout for the check in seconds

        Returns:
            HealthCheckResult indicating KB availability

        Raises:
            ValueError: If KB ID is invalid
        """
        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        start_time = time.time()

        try:
            response = self.bedrock_agent_client.get_knowledge_base(
                knowledgeBaseId=kb_id
            )

            response_time_ms = (time.time() - start_time) * 1000

            kb = response.get("knowledgeBase", {})
            kb_status = kb.get("status", "UNKNOWN")

            if kb_status == "ACTIVE":
                return HealthCheckResult(
                    component_name=f"KnowledgeBase-{kb_id}",
                    status=ComponentStatus.HEALTHY,
                    message=f"Knowledge base is active and responsive",
                    response_time_ms=response_time_ms,
                    details={
                        "kb_id": kb_id,
                        "kb_status": kb_status,
                        "kb_name": kb.get("name"),
                        "created_at": kb.get("createdAt")
                    }
                )
            elif kb_status in ["CREATING", "UPDATING", "DELETING"]:
                return HealthCheckResult(
                    component_name=f"KnowledgeBase-{kb_id}",
                    status=ComponentStatus.DEGRADED,
                    message=f"Knowledge base is {kb_status.lower()}",
                    response_time_ms=response_time_ms,
                    details={
                        "kb_id": kb_id,
                        "kb_status": kb_status,
                        "kb_name": kb.get("name")
                    }
                )
            else:
                failure_reasons = kb.get("failureReasons", [])
                return HealthCheckResult(
                    component_name=f"KnowledgeBase-{kb_id}",
                    status=ComponentStatus.UNHEALTHY,
                    message=f"Knowledge base is {kb_status.lower()}",
                    response_time_ms=response_time_ms,
                    details={
                        "kb_id": kb_id,
                        "kb_status": kb_status,
                        "failure_reasons": failure_reasons
                    }
                )

        except ClientError as e:
            response_time_ms = (time.time() - start_time) * 1000
            error_code = e.response.get("Error", {}).get("Code", "Unknown")

            if error_code == "ResourceNotFoundException":
                return HealthCheckResult(
                    component_name=f"KnowledgeBase-{kb_id}",
                    status=ComponentStatus.UNHEALTHY,
                    message=f"Knowledge base not found",
                    response_time_ms=response_time_ms,
                    details={"error_code": error_code}
                )
            elif error_code in ["ThrottlingException", "ServiceUnavailableException"]:
                return HealthCheckResult(
                    component_name=f"KnowledgeBase-{kb_id}",
                    status=ComponentStatus.DEGRADED,
                    message=f"Knowledge base service is temporarily unavailable",
                    response_time_ms=response_time_ms,
                    details={"error_code": error_code}
                )
            else:
                return HealthCheckResult(
                    component_name=f"KnowledgeBase-{kb_id}",
                    status=ComponentStatus.UNHEALTHY,
                    message=f"Failed to check knowledge base: {str(e)}",
                    response_time_ms=response_time_ms,
                    details={"error_code": error_code, "error_message": str(e)}
                )

    def check_opensearch_connectivity(
        self,
        collection_name: str,
        timeout_seconds: int = 5
    ) -> HealthCheckResult:
        """
        Check if OpenSearch Serverless collection is accessible.

        Args:
            collection_name: Name of the OpenSearch Serverless collection
            timeout_seconds: Timeout for the check in seconds

        Returns:
            HealthCheckResult indicating OSS connectivity

        Raises:
            ValueError: If collection name is invalid
        """
        if not collection_name or len(collection_name.strip()) == 0:
            raise ValueError("Collection name cannot be empty")

        start_time = time.time()

        try:
            # Try to get collection info
            response = self.opensearch_client.batch_get_collection(
                names=[collection_name]
            )

            response_time_ms = (time.time() - start_time) * 1000

            collection_summaries = response.get("collectionSummaries", [])

            if not collection_summaries:
                return HealthCheckResult(
                    component_name=f"OpenSearchServerless-{collection_name}",
                    status=ComponentStatus.UNHEALTHY,
                    message=f"Collection '{collection_name}' not found",
                    response_time_ms=response_time_ms,
                    details={"collection_name": collection_name}
                )

            collection = collection_summaries[0]
            collection_status = collection.get("status", "UNKNOWN")

            if collection_status == "ACTIVE":
                return HealthCheckResult(
                    component_name=f"OpenSearchServerless-{collection_name}",
                    status=ComponentStatus.HEALTHY,
                    message=f"OpenSearch Serverless collection is active",
                    response_time_ms=response_time_ms,
                    details={
                        "collection_name": collection_name,
                        "collection_status": collection_status,
                        "collection_arn": collection.get("arn"),
                        "created_at": collection.get("createdAtUtc")
                    }
                )
            elif collection_status in ["CREATING", "UPDATING", "DELETING"]:
                return HealthCheckResult(
                    component_name=f"OpenSearchServerless-{collection_name}",
                    status=ComponentStatus.DEGRADED,
                    message=f"OpenSearch Serverless collection is {collection_status.lower()}",
                    response_time_ms=response_time_ms,
                    details={
                        "collection_name": collection_name,
                        "collection_status": collection_status
                    }
                )
            else:
                return HealthCheckResult(
                    component_name=f"OpenSearchServerless-{collection_name}",
                    status=ComponentStatus.UNHEALTHY,
                    message=f"OpenSearch Serverless collection is {collection_status.lower()}",
                    response_time_ms=response_time_ms,
                    details={
                        "collection_name": collection_name,
                        "collection_status": collection_status
                    }
                )

        except ClientError as e:
            response_time_ms = (time.time() - start_time) * 1000
            error_code = e.response.get("Error", {}).get("Code", "Unknown")

            if error_code == "ResourceNotFoundException":
                return HealthCheckResult(
                    component_name=f"OpenSearchServerless-{collection_name}",
                    status=ComponentStatus.UNHEALTHY,
                    message=f"OpenSearch Serverless collection not found",
                    response_time_ms=response_time_ms,
                    details={"error_code": error_code}
                )
            elif error_code in ["ThrottlingException", "ServiceUnavailableException"]:
                return HealthCheckResult(
                    component_name=f"OpenSearchServerless-{collection_name}",
                    status=ComponentStatus.DEGRADED,
                    message=f"OpenSearch Serverless service is temporarily unavailable",
                    response_time_ms=response_time_ms,
                    details={"error_code": error_code}
                )
            else:
                return HealthCheckResult(
                    component_name=f"OpenSearchServerless-{collection_name}",
                    status=ComponentStatus.UNHEALTHY,
                    message=f"Failed to check OpenSearch Serverless: {str(e)}",
                    response_time_ms=response_time_ms,
                    details={"error_code": error_code, "error_message": str(e)}
                )

    def check_s3_bucket_accessibility(
        self,
        bucket_name: str,
        timeout_seconds: int = 5
    ) -> HealthCheckResult:
        """
        Check if S3 bucket is accessible.

        Args:
            bucket_name: Name of the S3 bucket
            timeout_seconds: Timeout for the check in seconds

        Returns:
            HealthCheckResult indicating S3 accessibility

        Raises:
            ValueError: If bucket name is invalid
        """
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("Bucket name cannot be empty")

        start_time = time.time()

        try:
            # Try to head the bucket
            self.s3_client.head_bucket(Bucket=bucket_name)

            response_time_ms = (time.time() - start_time) * 1000

            return HealthCheckResult(
                component_name=f"S3Bucket-{bucket_name}",
                status=ComponentStatus.HEALTHY,
                message=f"S3 bucket is accessible",
                response_time_ms=response_time_ms,
                details={
                    "bucket_name": bucket_name,
                    "region": self.region
                }
            )

        except ClientError as e:
            response_time_ms = (time.time() - start_time) * 1000
            error_code = e.response.get("Error", {}).get("Code", "Unknown")

            if error_code == "404":
                return HealthCheckResult(
                    component_name=f"S3Bucket-{bucket_name}",
                    status=ComponentStatus.UNHEALTHY,
                    message=f"S3 bucket not found",
                    response_time_ms=response_time_ms,
                    details={"error_code": error_code}
                )
            elif error_code == "403":
                return HealthCheckResult(
                    component_name=f"S3Bucket-{bucket_name}",
                    status=ComponentStatus.UNHEALTHY,
                    message=f"Access denied to S3 bucket",
                    response_time_ms=response_time_ms,
                    details={"error_code": error_code}
                )
            elif error_code in ["ThrottlingException", "ServiceUnavailableException"]:
                return HealthCheckResult(
                    component_name=f"S3Bucket-{bucket_name}",
                    status=ComponentStatus.DEGRADED,
                    message=f"S3 service is temporarily unavailable",
                    response_time_ms=response_time_ms,
                    details={"error_code": error_code}
                )
            else:
                return HealthCheckResult(
                    component_name=f"S3Bucket-{bucket_name}",
                    status=ComponentStatus.UNHEALTHY,
                    message=f"Failed to check S3 bucket: {str(e)}",
                    response_time_ms=response_time_ms,
                    details={"error_code": error_code, "error_message": str(e)}
                )

    def perform_system_health_check(
        self,
        kb_id: Optional[str] = None,
        collection_name: Optional[str] = None,
        bucket_name: Optional[str] = None
    ) -> SystemHealthStatus:
        """
        Perform a comprehensive system health check.

        Args:
            kb_id: Optional knowledge base ID to check
            collection_name: Optional OpenSearch collection name to check
            bucket_name: Optional S3 bucket name to check

        Returns:
            SystemHealthStatus containing all component health checks
        """
        system_status = SystemHealthStatus()
        system_status.check_timestamp = datetime.utcnow()

        # Check knowledge base if provided
        if kb_id:
            try:
                kb_result = self.check_knowledge_base_availability(kb_id)
                system_status.add_result(kb_result)
            except ValueError as e:
                system_status.add_result(HealthCheckResult(
                    component_name=f"KnowledgeBase-{kb_id}",
                    status=ComponentStatus.UNKNOWN,
                    message=f"Could not check knowledge base: {str(e)}"
                ))

        # Check OpenSearch if provided
        if collection_name:
            try:
                oss_result = self.check_opensearch_connectivity(collection_name)
                system_status.add_result(oss_result)
            except ValueError as e:
                system_status.add_result(HealthCheckResult(
                    component_name=f"OpenSearchServerless-{collection_name}",
                    status=ComponentStatus.UNKNOWN,
                    message=f"Could not check OpenSearch: {str(e)}"
                ))

        # Check S3 if provided
        if bucket_name:
            try:
                s3_result = self.check_s3_bucket_accessibility(bucket_name)
                system_status.add_result(s3_result)
            except ValueError as e:
                system_status.add_result(HealthCheckResult(
                    component_name=f"S3Bucket-{bucket_name}",
                    status=ComponentStatus.UNKNOWN,
                    message=f"Could not check S3 bucket: {str(e)}"
                ))

        return system_status
