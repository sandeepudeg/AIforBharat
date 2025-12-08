"""AWS configuration and credential management for Bedrock RAG Retrieval System"""

import boto3
import os
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError


class AWSConfig:
    """Manages AWS client initialization and configuration"""

    def __init__(self, region: Optional[str] = None, profile: Optional[str] = None):
        """
        Initialize AWS configuration.

        Args:
            region: AWS region (defaults to environment variable or us-east-1)
            profile: AWS profile name (defaults to default profile)
        """
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.profile = profile or os.getenv("AWS_PROFILE")
        self._account_id: Optional[str] = None
        self._clients: Dict[str, Any] = {}

    def get_region(self) -> str:
        """Get the configured AWS region"""
        return self.region

    def get_account_id(self) -> str:
        """
        Get the AWS account ID.

        Returns:
            AWS account ID as a string

        Raises:
            ValueError: If account ID cannot be detected
        """
        if self._account_id:
            return self._account_id

        try:
            sts_client = self.get_client("sts")
            response = sts_client.get_caller_identity()
            self._account_id = response["Account"]
            return self._account_id
        except (ClientError, NoCredentialsError) as e:
            raise ValueError(f"Failed to detect AWS account ID: {str(e)}")

    def get_client(self, service_name: str) -> Any:
        """
        Get or create a boto3 client for the specified service.

        Args:
            service_name: Name of the AWS service (e.g., 'bedrock', 's3', 'iam')

        Returns:
            Boto3 client for the service

        Raises:
            ValueError: If client creation fails
        """
        cache_key = f"{service_name}_{self.region}"

        if cache_key in self._clients:
            return self._clients[cache_key]

        try:
            session_kwargs = {"region_name": self.region}
            if self.profile:
                session_kwargs["profile_name"] = self.profile

            session = boto3.Session(**session_kwargs)
            client = session.client(service_name, region_name=self.region)
            self._clients[cache_key] = client
            return client
        except (ClientError, NoCredentialsError) as e:
            raise ValueError(f"Failed to create {service_name} client: {str(e)}")

    def validate_credentials(self) -> bool:
        """
        Validate that AWS credentials are available and valid.

        Returns:
            True if credentials are valid

        Raises:
            ValueError: If credentials are invalid or unavailable
        """
        try:
            sts_client = self.get_client("sts")
            sts_client.get_caller_identity()
            return True
        except (ClientError, NoCredentialsError) as e:
            raise ValueError(f"AWS credentials validation failed: {str(e)}")

    def validate_bedrock_access(self) -> bool:
        """
        Validate that Bedrock service is accessible.

        Returns:
            True if Bedrock is accessible

        Raises:
            ValueError: If Bedrock is not accessible
        """
        try:
            bedrock_client = self.get_client("bedrock")
            bedrock_client.list_foundation_models()
            return True
        except ClientError as e:
            raise ValueError(f"Bedrock access validation failed: {str(e)}")

    def validate_s3_access(self) -> bool:
        """
        Validate that S3 service is accessible.

        Returns:
            True if S3 is accessible

        Raises:
            ValueError: If S3 is not accessible
        """
        try:
            s3_client = self.get_client("s3")
            s3_client.list_buckets()
            return True
        except ClientError as e:
            raise ValueError(f"S3 access validation failed: {str(e)}")

    def validate_opensearch_access(self) -> bool:
        """
        Validate that OpenSearch Serverless is accessible.

        Returns:
            True if OpenSearch Serverless is accessible

        Raises:
            ValueError: If OpenSearch Serverless is not accessible
        """
        try:
            opensearch_client = self.get_client("opensearchserverless")
            opensearch_client.list_collections()
            return True
        except ClientError as e:
            raise ValueError(f"OpenSearch Serverless access validation failed: {str(e)}")

    def validate_iam_access(self) -> bool:
        """
        Validate that IAM service is accessible.

        Returns:
            True if IAM is accessible

        Raises:
            ValueError: If IAM is not accessible
        """
        try:
            iam_client = self.get_client("iam")
            iam_client.get_user()
            return True
        except ClientError as e:
            raise ValueError(f"IAM access validation failed: {str(e)}")

    def validate_all_services(self) -> Dict[str, bool]:
        """
        Validate access to all required AWS services.

        Returns:
            Dictionary with service names as keys and validation results as values
        """
        results = {}
        services = [
            ("credentials", self.validate_credentials),
            ("bedrock", self.validate_bedrock_access),
            ("s3", self.validate_s3_access),
            ("opensearch", self.validate_opensearch_access),
            ("iam", self.validate_iam_access),
        ]

        for service_name, validator in services:
            try:
                results[service_name] = validator()
            except ValueError as e:
                results[service_name] = False

        return results

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current AWS configuration.

        Returns:
            Dictionary with configuration details
        """
        try:
            account_id = self.get_account_id()
        except ValueError:
            account_id = "Unknown"

        return {
            "region": self.region,
            "account_id": account_id,
            "profile": self.profile or "default",
        }
