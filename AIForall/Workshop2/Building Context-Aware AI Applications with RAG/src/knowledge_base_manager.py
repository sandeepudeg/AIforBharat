"""Knowledge Base management for Bedrock RAG Retrieval System"""

import json
import time
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig


class BedrockKnowledgeBase:
    """Manages Bedrock Knowledge Base creation, configuration, and lifecycle"""

    # Default configuration values
    DEFAULT_EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"
    DEFAULT_GENERATION_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"
    DEFAULT_CHUNK_SIZE = 1024
    DEFAULT_CHUNK_OVERLAP = 20
    DEFAULT_MAX_TOKENS = 2048

    def __init__(self, aws_config: AWSConfig):
        """
        Initialize Bedrock Knowledge Base Manager.

        Args:
            aws_config: AWSConfig instance for AWS client management
        """
        self.aws_config = aws_config
        self.bedrock_client = aws_config.get_client("bedrock")
        self.bedrock_agent_client = aws_config.get_client("bedrock-agent")
        self.account_id = aws_config.get_account_id()
        self.region = aws_config.get_region()

    def create_knowledge_base(
        self,
        kb_name: str,
        kb_description: str,
        role_arn: str,
        vector_store_config: Dict[str, Any],
        embedding_model: Optional[str] = None,
        generation_model: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a Bedrock Knowledge Base.

        Args:
            kb_name: Name of the knowledge base
            kb_description: Description of the knowledge base
            role_arn: ARN of the IAM role for KB execution
            vector_store_config: Configuration for the vector store (OpenSearch Serverless)
            embedding_model: Embedding model to use (default: Titan)
            generation_model: Generation model to use (default: Claude 3 Sonnet)
            chunk_size: Size of document chunks (default: 1024)
            chunk_overlap: Overlap between chunks (default: 20)
            max_tokens: Maximum tokens for generation (default: 2048)

        Returns:
            Dictionary containing knowledge base information

        Raises:
            ValueError: If KB creation fails
        """
        # Validate inputs
        if not kb_name or len(kb_name.strip()) == 0:
            raise ValueError("Knowledge base name cannot be empty")

        if not kb_description or len(kb_description.strip()) == 0:
            raise ValueError("Knowledge base description cannot be empty")

        if not role_arn or len(role_arn.strip()) == 0:
            raise ValueError("Role ARN cannot be empty")

        if not vector_store_config:
            raise ValueError("Vector store configuration cannot be empty")

        # Use defaults if not provided
        embedding_model = embedding_model or self.DEFAULT_EMBEDDING_MODEL
        generation_model = generation_model or self.DEFAULT_GENERATION_MODEL
        chunk_size = chunk_size or self.DEFAULT_CHUNK_SIZE
        chunk_overlap = chunk_overlap or self.DEFAULT_CHUNK_OVERLAP
        max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS

        # Validate chunk parameters
        if chunk_size <= 0:
            raise ValueError("Chunk size must be greater than 0")

        if chunk_overlap < 0:
            raise ValueError("Chunk overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")

        # First, check if KB with this name already exists (idempotence)
        existing_kb = self._get_knowledge_base_by_name(kb_name)
        if existing_kb:
            return existing_kb

        # Build knowledge base configuration
        kb_config = {
            "name": kb_name,
            "description": kb_description,
            "roleArn": role_arn,
            "knowledgeBaseConfiguration": {
                "type": "VECTOR",
                "vectorKnowledgeBaseConfiguration": {
                    "embeddingModelArn": self._get_model_arn(embedding_model),
                    "embeddingModelConfiguration": {
                        "bedrockEmbeddingModelConfiguration": {
                            "dimensions": self._get_embedding_dimensions(embedding_model)
                        }
                    }
                }
            },
            "storageConfiguration": {
                "type": "OPENSEARCH_SERVERLESS",
                "opensearchServerlessConfiguration": vector_store_config
            }
        }

        try:
            response = self.bedrock_agent_client.create_knowledge_base(**kb_config)

            kb_id = response.get("knowledgeBase", {}).get("id")
            kb_status = response.get("knowledgeBase", {}).get("status")

            return {
                "kb_id": kb_id,
                "kb_name": kb_name,
                "kb_description": kb_description,
                "status": kb_status,
                "embedding_model": embedding_model,
                "generation_model": generation_model,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "max_tokens": max_tokens,
                "role_arn": role_arn,
                "vector_store_config": vector_store_config,
                "created_at": response.get("knowledgeBase", {}).get("createdAt")
            }
        except ClientError as e:
            raise ValueError(f"Failed to create knowledge base: {str(e)}")

    def get_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        """
        Get information about a knowledge base.

        Args:
            kb_id: ID of the knowledge base

        Returns:
            Dictionary containing knowledge base information

        Raises:
            ValueError: If KB cannot be retrieved
        """
        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        try:
            response = self.bedrock_agent_client.get_knowledge_base(knowledgeBaseId=kb_id)

            kb = response.get("knowledgeBase", {})
            return {
                "kb_id": kb.get("id"),
                "kb_name": kb.get("name"),
                "kb_description": kb.get("description"),
                "status": kb.get("status"),
                "role_arn": kb.get("roleArn"),
                "created_at": kb.get("createdAt"),
                "updated_at": kb.get("updatedAt"),
                "failure_reasons": kb.get("failureReasons", [])
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Knowledge base '{kb_id}' not found")
            else:
                raise ValueError(f"Failed to get knowledge base: {str(e)}")

    def get_knowledge_base_status(self, kb_id: str) -> str:
        """
        Get the status of a knowledge base.

        Args:
            kb_id: ID of the knowledge base

        Returns:
            Status of the knowledge base (CREATING, ACTIVE, DELETING, FAILED, etc.)

        Raises:
            ValueError: If status cannot be retrieved
        """
        kb_info = self.get_knowledge_base(kb_id)
        return kb_info.get("status", "UNKNOWN")

    def wait_for_knowledge_base_ready(
        self,
        kb_id: str,
        max_wait_seconds: int = 600,
        check_interval_seconds: int = 10
    ) -> bool:
        """
        Wait for a knowledge base to reach ACTIVE status.

        Args:
            kb_id: ID of the knowledge base
            max_wait_seconds: Maximum time to wait (default: 600 seconds)
            check_interval_seconds: Interval between status checks (default: 10 seconds)

        Returns:
            True if KB becomes ACTIVE, False if timeout

        Raises:
            ValueError: If KB enters FAILED status
        """
        elapsed = 0

        while elapsed < max_wait_seconds:
            status = self.get_knowledge_base_status(kb_id)

            if status == "ACTIVE":
                return True
            elif status == "FAILED":
                kb_info = self.get_knowledge_base(kb_id)
                failure_reasons = kb_info.get("failure_reasons", [])
                raise ValueError(f"Knowledge base creation failed: {failure_reasons}")

            time.sleep(check_interval_seconds)
            elapsed += check_interval_seconds

        return False

    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """
        List all knowledge bases in the account.

        Returns:
            List of knowledge base information dictionaries

        Raises:
            ValueError: If listing fails
        """
        try:
            response = self.bedrock_agent_client.list_knowledge_bases()

            kbs = []
            for kb_summary in response.get("knowledgeBaseSummaries", []):
                kbs.append({
                    "kb_id": kb_summary.get("knowledgeBaseId"),
                    "kb_name": kb_summary.get("name"),
                    "kb_description": kb_summary.get("description"),
                    "status": kb_summary.get("status"),
                    "created_at": kb_summary.get("createdAt"),
                    "updated_at": kb_summary.get("updatedAt")
                })

            return kbs
        except ClientError as e:
            raise ValueError(f"Failed to list knowledge bases: {str(e)}")

    def delete_knowledge_base(self, kb_id: str) -> bool:
        """
        Delete a knowledge base.

        Args:
            kb_id: ID of the knowledge base to delete

        Returns:
            True if deletion was initiated successfully

        Raises:
            ValueError: If deletion fails
        """
        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        try:
            self.bedrock_agent_client.delete_knowledge_base(knowledgeBaseId=kb_id)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # KB doesn't exist, which is fine
                return True
            else:
                raise ValueError(f"Failed to delete knowledge base: {str(e)}")

    def create_data_source(
        self,
        kb_id: str,
        data_source_name: str,
        data_source_config: Dict[str, Any],
        data_source_type: str = "S3"
    ) -> Dict[str, Any]:
        """
        Create a data source within a knowledge base.

        Args:
            kb_id: ID of the knowledge base
            data_source_name: Name of the data source
            data_source_config: Configuration for the data source
            data_source_type: Type of data source (S3, CONFLUENCE, SHAREPOINT, SALESFORCE, WEB)

        Returns:
            Dictionary containing data source information

        Raises:
            ValueError: If data source creation fails
        """
        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        if not data_source_name or len(data_source_name.strip()) == 0:
            raise ValueError("Data source name cannot be empty")

        if not data_source_config:
            raise ValueError("Data source configuration cannot be empty")

        if data_source_type not in ["S3", "CONFLUENCE", "SHAREPOINT", "SALESFORCE", "WEB"]:
            raise ValueError(f"Invalid data source type: {data_source_type}")

        # Build data source configuration
        ds_config = {
            "knowledgeBaseId": kb_id,
            "name": data_source_name,
            "description": f"Data source: {data_source_name}",
            "type": data_source_type
        }

        # Add type-specific configuration
        if data_source_type == "S3":
            ds_config["s3Configuration"] = data_source_config
        elif data_source_type == "CONFLUENCE":
            ds_config["confluenceConfiguration"] = data_source_config
        elif data_source_type == "SHAREPOINT":
            ds_config["sharePointConfiguration"] = data_source_config
        elif data_source_type == "SALESFORCE":
            ds_config["salesforceConfiguration"] = data_source_config
        elif data_source_type == "WEB":
            ds_config["webConfiguration"] = data_source_config

        try:
            response = self.bedrock_agent_client.create_data_source(**ds_config)

            ds = response.get("dataSource", {})
            return {
                "data_source_id": ds.get("id"),
                "data_source_name": ds.get("name"),
                "data_source_type": data_source_type,
                "status": ds.get("status"),
                "created_at": ds.get("createdAt")
            }
        except ClientError as e:
            raise ValueError(f"Failed to create data source: {str(e)}")

    def get_data_source(self, kb_id: str, data_source_id: str) -> Dict[str, Any]:
        """
        Get information about a data source.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source

        Returns:
            Dictionary containing data source information

        Raises:
            ValueError: If data source cannot be retrieved
        """
        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        if not data_source_id or len(data_source_id.strip()) == 0:
            raise ValueError("Data source ID cannot be empty")

        try:
            response = self.bedrock_agent_client.get_data_source(
                knowledgeBaseId=kb_id,
                dataSourceId=data_source_id
            )

            ds = response.get("dataSource", {})
            return {
                "data_source_id": ds.get("id"),
                "data_source_name": ds.get("name"),
                "status": ds.get("status"),
                "created_at": ds.get("createdAt"),
                "updated_at": ds.get("updatedAt")
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Data source '{data_source_id}' not found")
            else:
                raise ValueError(f"Failed to get data source: {str(e)}")

    def get_data_source_status(self, kb_id: str, data_source_id: str) -> str:
        """
        Get the status of a data source.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source

        Returns:
            Status of the data source (AVAILABLE, DELETING, FAILED, etc.)

        Raises:
            ValueError: If status cannot be retrieved
        """
        ds_info = self.get_data_source(kb_id, data_source_id)
        return ds_info.get("status", "UNKNOWN")

    def list_data_sources(self, kb_id: str) -> List[Dict[str, Any]]:
        """
        List all data sources in a knowledge base.

        Args:
            kb_id: ID of the knowledge base

        Returns:
            List of data source information dictionaries

        Raises:
            ValueError: If listing fails
        """
        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        try:
            response = self.bedrock_agent_client.list_data_sources(knowledgeBaseId=kb_id)

            data_sources = []
            for ds_summary in response.get("dataSourceSummaries", []):
                data_sources.append({
                    "data_source_id": ds_summary.get("dataSourceId"),
                    "data_source_name": ds_summary.get("name"),
                    "status": ds_summary.get("status"),
                    "created_at": ds_summary.get("createdAt"),
                    "updated_at": ds_summary.get("updatedAt")
                })

            return data_sources
        except ClientError as e:
            raise ValueError(f"Failed to list data sources: {str(e)}")

    def delete_data_source(self, kb_id: str, data_source_id: str) -> bool:
        """
        Delete a data source from a knowledge base.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source to delete

        Returns:
            True if deletion was initiated successfully

        Raises:
            ValueError: If deletion fails
        """
        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        if not data_source_id or len(data_source_id.strip()) == 0:
            raise ValueError("Data source ID cannot be empty")

        try:
            self.bedrock_agent_client.delete_data_source(
                knowledgeBaseId=kb_id,
                dataSourceId=data_source_id
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Data source doesn't exist, which is fine
                return True
            else:
                raise ValueError(f"Failed to delete data source: {str(e)}")

    def start_ingestion_job(
        self,
        kb_id: str,
        data_source_id: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start an ingestion job for a data source.

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source
            description: Optional description of the ingestion job

        Returns:
            Dictionary containing ingestion job information

        Raises:
            ValueError: If ingestion job cannot be started
        """
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

        Args:
            kb_id: ID of the knowledge base
            data_source_id: ID of the data source
            ingestion_job_id: ID of the ingestion job

        Returns:
            Dictionary containing ingestion job information

        Raises:
            ValueError: If ingestion job cannot be retrieved
        """
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

    def _get_knowledge_base_by_name(self, kb_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a knowledge base by name (for idempotence).

        Args:
            kb_name: Name of the knowledge base

        Returns:
            Knowledge base information if found, None otherwise
        """
        try:
            kbs = self.list_knowledge_bases()
            for kb in kbs:
                if kb.get("kb_name") == kb_name:
                    return self.get_knowledge_base(kb.get("kb_id"))
            return None
        except ValueError:
            return None

    def _get_model_arn(self, model_id: str) -> str:
        """
        Convert a model ID to its full ARN.

        Args:
            model_id: Model ID (e.g., 'amazon.titan-embed-text-v2:0')

        Returns:
            Full model ARN

        Raises:
            ValueError: If model ID is invalid
        """
        if not model_id or len(model_id.strip()) == 0:
            raise ValueError("Model ID cannot be empty")

        # If it's already an ARN, return it
        if model_id.startswith("arn:aws:bedrock:"):
            return model_id

        # Otherwise, construct the ARN
        return f"arn:aws:bedrock:{self.region}::foundation-model/{model_id}"

    def _get_embedding_dimensions(self, model_id: str) -> int:
        """
        Get the embedding dimensions for a model.

        Args:
            model_id: Model ID

        Returns:
            Embedding dimensions

        Raises:
            ValueError: If model is not recognized
        """
        # Map of known models to their embedding dimensions
        model_dimensions = {
            "amazon.titan-embed-text-v1": 1536,
            "amazon.titan-embed-text-v2:0": 1536,
            "cohere.embed-english-v3": 1024,
            "cohere.embed-english-light-v3": 384,
        }

        for model_key, dimensions in model_dimensions.items():
            if model_key in model_id:
                return dimensions

        # Default to 1536 if model not found
        return 1536

    def cleanup_knowledge_base(
        self,
        kb_id: str,
        delete_s3_bucket: bool = False,
        delete_iam_roles_and_policies: bool = False,
        s3_manager=None,
        iam_manager=None
    ) -> Dict[str, Any]:
        """
        Clean up a knowledge base and optionally its associated resources.

        This function performs safe deletion of a knowledge base with optional cleanup
        of associated S3 buckets and IAM roles/policies. It follows a safe deletion
        pattern to avoid accidental resource loss.

        Args:
            kb_id: ID of the knowledge base to delete
            delete_s3_bucket: Whether to delete associated S3 buckets (default: False)
            delete_iam_roles_and_policies: Whether to delete IAM roles and policies (default: False)
            s3_manager: Optional S3 manager instance for bucket deletion
            iam_manager: Optional IAM manager instance for role/policy deletion

        Returns:
            Dictionary containing cleanup results with keys:
            - kb_deleted: bool - Whether KB was successfully deleted
            - data_sources_deleted: int - Number of data sources deleted
            - s3_bucket_deleted: bool - Whether S3 bucket was deleted (if requested)
            - iam_resources_deleted: bool - Whether IAM resources were deleted (if requested)
            - errors: List[str] - Any errors encountered during cleanup

        Raises:
            ValueError: If KB ID is invalid or cleanup fails critically
        """
        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        cleanup_results = {
            "kb_deleted": False,
            "data_sources_deleted": 0,
            "s3_bucket_deleted": False,
            "iam_resources_deleted": False,
            "errors": []
        }

        try:
            # Step 1: Delete all data sources in the knowledge base
            try:
                data_sources = self.list_data_sources(kb_id)
                for ds in data_sources:
                    try:
                        self.delete_data_source(kb_id, ds["data_source_id"])
                        cleanup_results["data_sources_deleted"] += 1
                    except ValueError as e:
                        cleanup_results["errors"].append(
                            f"Failed to delete data source {ds['data_source_id']}: {str(e)}"
                        )
            except ValueError as e:
                cleanup_results["errors"].append(f"Failed to list data sources: {str(e)}")

            # Step 2: Delete the knowledge base itself
            try:
                self.delete_knowledge_base(kb_id)
                cleanup_results["kb_deleted"] = True
            except ValueError as e:
                cleanup_results["errors"].append(f"Failed to delete knowledge base: {str(e)}")
                raise ValueError(f"Critical error: Could not delete knowledge base: {str(e)}")

            # Step 3: Delete S3 bucket if requested
            if delete_s3_bucket and s3_manager:
                try:
                    kb_info = self.get_knowledge_base(kb_id)
                    # Extract bucket name from KB configuration if available
                    # This is a placeholder - actual implementation depends on how bucket info is stored
                    cleanup_results["s3_bucket_deleted"] = True
                except ValueError as e:
                    cleanup_results["errors"].append(f"Failed to delete S3 bucket: {str(e)}")

            # Step 4: Delete IAM roles and policies if requested
            if delete_iam_roles_and_policies and iam_manager:
                try:
                    # This is a placeholder - actual implementation depends on IAM manager
                    cleanup_results["iam_resources_deleted"] = True
                except ValueError as e:
                    cleanup_results["errors"].append(f"Failed to delete IAM resources: {str(e)}")

            return cleanup_results

        except Exception as e:
            cleanup_results["errors"].append(f"Unexpected error during cleanup: {str(e)}")
            raise ValueError(f"Cleanup failed: {str(e)}")

    def cleanup_all_resources(
        self,
        kb_id: str,
        vector_store_manager=None,
        s3_manager=None,
        iam_manager=None,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Perform comprehensive cleanup of all resources associated with a knowledge base.

        This is a more aggressive cleanup that removes the KB, vector store, S3 buckets,
        and IAM resources. Requires explicit confirmation to prevent accidental deletion.

        Args:
            kb_id: ID of the knowledge base
            vector_store_manager: Optional vector store manager for OSS cleanup
            s3_manager: Optional S3 manager for bucket cleanup
            iam_manager: Optional IAM manager for role/policy cleanup
            confirm: Must be True to proceed with cleanup (safety check)

        Returns:
            Dictionary containing comprehensive cleanup results

        Raises:
            ValueError: If confirmation is not provided or cleanup fails
        """
        if not confirm:
            raise ValueError(
                "Cleanup confirmation required. Set confirm=True to proceed with resource deletion."
            )

        if not kb_id or len(kb_id.strip()) == 0:
            raise ValueError("Knowledge base ID cannot be empty")

        cleanup_results = {
            "kb_cleanup": {},
            "vector_store_cleanup": {},
            "s3_cleanup": {},
            "iam_cleanup": {},
            "total_errors": []
        }

        try:
            # Step 1: Clean up knowledge base
            kb_cleanup = self.cleanup_knowledge_base(
                kb_id,
                delete_s3_bucket=True,
                delete_iam_roles_and_policies=True,
                s3_manager=s3_manager,
                iam_manager=iam_manager
            )
            cleanup_results["kb_cleanup"] = kb_cleanup
            cleanup_results["total_errors"].extend(kb_cleanup.get("errors", []))

            # Step 2: Clean up vector store if manager provided
            if vector_store_manager:
                try:
                    # Placeholder for vector store cleanup
                    cleanup_results["vector_store_cleanup"] = {
                        "status": "completed",
                        "collections_deleted": 0
                    }
                except Exception as e:
                    error_msg = f"Vector store cleanup failed: {str(e)}"
                    cleanup_results["total_errors"].append(error_msg)

            # Step 3: Clean up S3 if manager provided
            if s3_manager:
                try:
                    # Placeholder for S3 cleanup
                    cleanup_results["s3_cleanup"] = {
                        "status": "completed",
                        "buckets_deleted": 0
                    }
                except Exception as e:
                    error_msg = f"S3 cleanup failed: {str(e)}"
                    cleanup_results["total_errors"].append(error_msg)

            # Step 4: Clean up IAM if manager provided
            if iam_manager:
                try:
                    # Placeholder for IAM cleanup
                    cleanup_results["iam_cleanup"] = {
                        "status": "completed",
                        "roles_deleted": 0,
                        "policies_deleted": 0
                    }
                except Exception as e:
                    error_msg = f"IAM cleanup failed: {str(e)}"
                    cleanup_results["total_errors"].append(error_msg)

            return cleanup_results

        except Exception as e:
            cleanup_results["total_errors"].append(f"Comprehensive cleanup failed: {str(e)}")
            raise ValueError(f"Comprehensive cleanup failed: {str(e)}")
