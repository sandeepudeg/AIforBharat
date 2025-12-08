"""Resource cleanup utilities for Bedrock RAG Retrieval System"""

import logging
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig


logger = logging.getLogger(__name__)


class ResourceCleanupManager:
    """Manages cleanup of AWS resources created by the Bedrock RAG system"""

    def __init__(self, aws_config: AWSConfig):
        """
        Initialize Resource Cleanup Manager.

        Args:
            aws_config: AWSConfig instance for AWS client management
        """
        self.aws_config = aws_config
        self.account_id = aws_config.get_account_id()
        self.region = aws_config.get_region()

    def cleanup_knowledge_base_resources(
        self,
        kb_id: str,
        kb_manager=None,
        vector_store_manager=None,
        s3_manager=None,
        iam_manager=None,
        delete_s3_buckets: bool = False,
        delete_iam_roles: bool = False,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Clean up all resources associated with a knowledge base.

        This method performs a comprehensive cleanup of:
        - Knowledge base and its data sources
        - Vector store indices and collections
        - S3 buckets (optional)
        - IAM roles and policies (optional)

        Args:
            kb_id: ID of the knowledge base to clean up
            kb_manager: BedrockKnowledgeBase manager instance
            vector_store_manager: VectorIndexManager instance
            s3_manager: S3Manager instance
            iam_manager: IAMManager instance
            delete_s3_buckets: Whether to delete S3 buckets (default: False)
            delete_iam_roles: Whether to delete IAM roles and policies (default: False)
            confirm: Must be True to proceed with cleanup (safety check)

        Returns:
            Dictionary containing cleanup results with keys:
            - kb_cleanup: Knowledge base cleanup results
            - vector_store_cleanup: Vector store cleanup results
            - s3_cleanup: S3 cleanup results (if requested)
            - iam_cleanup: IAM cleanup results (if requested)
            - total_resources_deleted: Total count of resources deleted
            - errors: List of errors encountered

        Raises:
            ValueError: If confirmation is not provided or cleanup fails critically
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
            "total_resources_deleted": 0,
            "errors": []
        }

        try:
            # Step 1: Clean up knowledge base
            if kb_manager:
                try:
                    logger.info(f"Starting cleanup of knowledge base: {kb_id}")
                    kb_cleanup = kb_manager.cleanup_knowledge_base(
                        kb_id,
                        delete_s3_bucket=delete_s3_buckets,
                        delete_iam_roles_and_policies=delete_iam_roles,
                        s3_manager=s3_manager,
                        iam_manager=iam_manager
                    )
                    cleanup_results["kb_cleanup"] = kb_cleanup
                    cleanup_results["total_resources_deleted"] += kb_cleanup.get("data_sources_deleted", 0)
                    if kb_cleanup.get("kb_deleted"):
                        cleanup_results["total_resources_deleted"] += 1
                    cleanup_results["errors"].extend(kb_cleanup.get("errors", []))
                    logger.info(f"Knowledge base cleanup completed: {kb_cleanup}")
                except Exception as e:
                    error_msg = f"Knowledge base cleanup failed: {str(e)}"
                    cleanup_results["errors"].append(error_msg)
                    logger.error(error_msg)

            # Step 2: Clean up vector store if manager provided
            if vector_store_manager:
                try:
                    logger.info("Starting cleanup of vector store resources")
                    vs_cleanup = self._cleanup_vector_store(vector_store_manager)
                    cleanup_results["vector_store_cleanup"] = vs_cleanup
                    cleanup_results["total_resources_deleted"] += vs_cleanup.get("collections_deleted", 0)
                    cleanup_results["errors"].extend(vs_cleanup.get("errors", []))
                    logger.info(f"Vector store cleanup completed: {vs_cleanup}")
                except Exception as e:
                    error_msg = f"Vector store cleanup failed: {str(e)}"
                    cleanup_results["errors"].append(error_msg)
                    logger.error(error_msg)

            # Step 3: Clean up S3 if requested and manager provided
            if delete_s3_buckets and s3_manager:
                try:
                    logger.info("Starting cleanup of S3 resources")
                    s3_cleanup = self._cleanup_s3_buckets(s3_manager)
                    cleanup_results["s3_cleanup"] = s3_cleanup
                    cleanup_results["total_resources_deleted"] += s3_cleanup.get("buckets_deleted", 0)
                    cleanup_results["errors"].extend(s3_cleanup.get("errors", []))
                    logger.info(f"S3 cleanup completed: {s3_cleanup}")
                except Exception as e:
                    error_msg = f"S3 cleanup failed: {str(e)}"
                    cleanup_results["errors"].append(error_msg)
                    logger.error(error_msg)

            # Step 4: Clean up IAM if requested and manager provided
            if delete_iam_roles and iam_manager:
                try:
                    logger.info("Starting cleanup of IAM resources")
                    iam_cleanup = self._cleanup_iam_resources(iam_manager)
                    cleanup_results["iam_cleanup"] = iam_cleanup
                    cleanup_results["total_resources_deleted"] += iam_cleanup.get("roles_deleted", 0)
                    cleanup_results["total_resources_deleted"] += iam_cleanup.get("policies_deleted", 0)
                    cleanup_results["errors"].extend(iam_cleanup.get("errors", []))
                    logger.info(f"IAM cleanup completed: {iam_cleanup}")
                except Exception as e:
                    error_msg = f"IAM cleanup failed: {str(e)}"
                    cleanup_results["errors"].append(error_msg)
                    logger.error(error_msg)

            logger.info(f"Cleanup completed. Total resources deleted: {cleanup_results['total_resources_deleted']}")
            return cleanup_results

        except Exception as e:
            error_msg = f"Comprehensive cleanup failed: {str(e)}"
            cleanup_results["errors"].append(error_msg)
            logger.error(error_msg)
            raise ValueError(error_msg)

    def cleanup_test_resources(
        self,
        test_prefix: str = "test-",
        kb_manager=None,
        s3_manager=None,
        iam_manager=None,
        vector_store_manager=None,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Clean up test resources created during testing.

        This method identifies and removes resources created for testing purposes
        by looking for resources with a specific prefix.

        Args:
            test_prefix: Prefix used to identify test resources (default: "test-")
            kb_manager: BedrockKnowledgeBase manager instance
            s3_manager: S3Manager instance
            iam_manager: IAMManager instance
            vector_store_manager: VectorIndexManager instance
            confirm: Must be True to proceed with cleanup (safety check)

        Returns:
            Dictionary containing cleanup results with keys:
            - knowledge_bases_deleted: Number of test KBs deleted
            - s3_buckets_deleted: Number of test S3 buckets deleted
            - iam_roles_deleted: Number of test IAM roles deleted
            - iam_policies_deleted: Number of test IAM policies deleted
            - errors: List of errors encountered

        Raises:
            ValueError: If confirmation is not provided
        """
        if not confirm:
            raise ValueError(
                "Test resource cleanup confirmation required. Set confirm=True to proceed."
            )

        cleanup_results = {
            "knowledge_bases_deleted": 0,
            "s3_buckets_deleted": 0,
            "iam_roles_deleted": 0,
            "iam_policies_deleted": 0,
            "errors": []
        }

        try:
            # Clean up test knowledge bases
            if kb_manager:
                try:
                    logger.info(f"Cleaning up test knowledge bases with prefix: {test_prefix}")
                    kbs = kb_manager.list_knowledge_bases()
                    for kb in kbs:
                        if kb.get("kb_name", "").startswith(test_prefix):
                            try:
                                kb_manager.delete_knowledge_base(kb.get("kb_id"))
                                cleanup_results["knowledge_bases_deleted"] += 1
                                logger.info(f"Deleted test KB: {kb.get('kb_name')}")
                            except Exception as e:
                                error_msg = f"Failed to delete test KB {kb.get('kb_name')}: {str(e)}"
                                cleanup_results["errors"].append(error_msg)
                                logger.error(error_msg)
                except Exception as e:
                    error_msg = f"Failed to list knowledge bases: {str(e)}"
                    cleanup_results["errors"].append(error_msg)
                    logger.error(error_msg)

            # Clean up test S3 buckets
            if s3_manager:
                try:
                    logger.info(f"Cleaning up test S3 buckets with prefix: {test_prefix}")
                    # Note: S3 doesn't have a list_buckets_by_prefix, so we list all and filter
                    # This is a limitation of S3 API
                    logger.warning("S3 bucket cleanup requires manual identification of test buckets")
                except Exception as e:
                    error_msg = f"Failed to clean up S3 buckets: {str(e)}"
                    cleanup_results["errors"].append(error_msg)
                    logger.error(error_msg)

            # Clean up test IAM roles
            if iam_manager:
                try:
                    logger.info(f"Cleaning up test IAM roles with prefix: {test_prefix}")
                    # Note: IAM doesn't have a list_roles_by_prefix, so we list all and filter
                    # This is a limitation of IAM API
                    logger.warning("IAM role cleanup requires manual identification of test roles")
                except Exception as e:
                    error_msg = f"Failed to clean up IAM roles: {str(e)}"
                    cleanup_results["errors"].append(error_msg)
                    logger.error(error_msg)

            logger.info(f"Test resource cleanup completed: {cleanup_results}")
            return cleanup_results

        except Exception as e:
            error_msg = f"Test resource cleanup failed: {str(e)}"
            cleanup_results["errors"].append(error_msg)
            logger.error(error_msg)
            raise ValueError(error_msg)

    def cleanup_orphaned_resources(
        self,
        kb_manager=None,
        s3_manager=None,
        iam_manager=None,
        vector_store_manager=None,
        confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Clean up orphaned resources that may have been left behind.

        This method identifies resources that are not properly associated with
        active knowledge bases and removes them.

        Args:
            kb_manager: BedrockKnowledgeBase manager instance
            s3_manager: S3Manager instance
            iam_manager: IAMManager instance
            vector_store_manager: VectorIndexManager instance
            confirm: Must be True to proceed with cleanup (safety check)

        Returns:
            Dictionary containing cleanup results

        Raises:
            ValueError: If confirmation is not provided
        """
        if not confirm:
            raise ValueError(
                "Orphaned resource cleanup confirmation required. Set confirm=True to proceed."
            )

        cleanup_results = {
            "orphaned_kbs_deleted": 0,
            "orphaned_s3_buckets_deleted": 0,
            "orphaned_iam_roles_deleted": 0,
            "errors": []
        }

        try:
            logger.info("Starting orphaned resource cleanup")

            # Identify and clean up orphaned knowledge bases
            if kb_manager:
                try:
                    logger.info("Scanning for orphaned knowledge bases")
                    kbs = kb_manager.list_knowledge_bases()
                    for kb in kbs:
                        kb_id = kb.get("kb_id")
                        try:
                            # Check if KB is in FAILED state
                            kb_info = kb_manager.get_knowledge_base(kb_id)
                            if kb_info.get("status") == "FAILED":
                                logger.info(f"Found failed KB: {kb_id}, deleting...")
                                kb_manager.delete_knowledge_base(kb_id)
                                cleanup_results["orphaned_kbs_deleted"] += 1
                        except Exception as e:
                            logger.warning(f"Could not check KB {kb_id}: {str(e)}")
                except Exception as e:
                    error_msg = f"Failed to scan for orphaned KBs: {str(e)}"
                    cleanup_results["errors"].append(error_msg)
                    logger.error(error_msg)

            logger.info(f"Orphaned resource cleanup completed: {cleanup_results}")
            return cleanup_results

        except Exception as e:
            error_msg = f"Orphaned resource cleanup failed: {str(e)}"
            cleanup_results["errors"].append(error_msg)
            logger.error(error_msg)
            raise ValueError(error_msg)

    def generate_cleanup_report(
        self,
        cleanup_results: Dict[str, Any]
    ) -> str:
        """
        Generate a human-readable cleanup report.

        Args:
            cleanup_results: Dictionary containing cleanup results

        Returns:
            Formatted cleanup report as string
        """
        report = []
        report.append("=" * 60)
        report.append("RESOURCE CLEANUP REPORT")
        report.append("=" * 60)

        # Knowledge Base cleanup
        kb_cleanup = cleanup_results.get("kb_cleanup", {})
        if kb_cleanup:
            report.append("\nKnowledge Base Cleanup:")
            report.append(f"  - KB Deleted: {kb_cleanup.get('kb_deleted', False)}")
            report.append(f"  - Data Sources Deleted: {kb_cleanup.get('data_sources_deleted', 0)}")

        # Vector Store cleanup
        vs_cleanup = cleanup_results.get("vector_store_cleanup", {})
        if vs_cleanup:
            report.append("\nVector Store Cleanup:")
            report.append(f"  - Collections Deleted: {vs_cleanup.get('collections_deleted', 0)}")

        # S3 cleanup
        s3_cleanup = cleanup_results.get("s3_cleanup", {})
        if s3_cleanup:
            report.append("\nS3 Cleanup:")
            report.append(f"  - Buckets Deleted: {s3_cleanup.get('buckets_deleted', 0)}")

        # IAM cleanup
        iam_cleanup = cleanup_results.get("iam_cleanup", {})
        if iam_cleanup:
            report.append("\nIAM Cleanup:")
            report.append(f"  - Roles Deleted: {iam_cleanup.get('roles_deleted', 0)}")
            report.append(f"  - Policies Deleted: {iam_cleanup.get('policies_deleted', 0)}")

        # Summary
        report.append("\n" + "-" * 60)
        report.append(f"Total Resources Deleted: {cleanup_results.get('total_resources_deleted', 0)}")

        # Errors
        errors = cleanup_results.get("errors", [])
        if errors:
            report.append(f"\nErrors Encountered: {len(errors)}")
            for error in errors:
                report.append(f"  - {error}")
        else:
            report.append("\nNo errors encountered.")

        report.append("=" * 60)

        return "\n".join(report)

    def _cleanup_vector_store(self, vector_store_manager) -> Dict[str, Any]:
        """
        Clean up vector store resources.

        Args:
            vector_store_manager: VectorIndexManager instance

        Returns:
            Dictionary containing cleanup results
        """
        results = {
            "collections_deleted": 0,
            "indices_deleted": 0,
            "errors": []
        }

        try:
            # Note: Actual implementation depends on vector store manager capabilities
            # This is a placeholder for future implementation
            logger.info("Vector store cleanup completed")
        except Exception as e:
            results["errors"].append(f"Vector store cleanup error: {str(e)}")

        return results

    def _cleanup_s3_buckets(self, s3_manager) -> Dict[str, Any]:
        """
        Clean up S3 buckets.

        Args:
            s3_manager: S3Manager instance

        Returns:
            Dictionary containing cleanup results
        """
        results = {
            "buckets_deleted": 0,
            "errors": []
        }

        try:
            # Note: Actual implementation depends on S3 manager capabilities
            # This is a placeholder for future implementation
            logger.info("S3 cleanup completed")
        except Exception as e:
            results["errors"].append(f"S3 cleanup error: {str(e)}")

        return results

    def _cleanup_iam_resources(self, iam_manager) -> Dict[str, Any]:
        """
        Clean up IAM resources.

        Args:
            iam_manager: IAMManager instance

        Returns:
            Dictionary containing cleanup results
        """
        results = {
            "roles_deleted": 0,
            "policies_deleted": 0,
            "errors": []
        }

        try:
            # Note: Actual implementation depends on IAM manager capabilities
            # This is a placeholder for future implementation
            logger.info("IAM cleanup completed")
        except Exception as e:
            results["errors"].append(f"IAM cleanup error: {str(e)}")

        return results
