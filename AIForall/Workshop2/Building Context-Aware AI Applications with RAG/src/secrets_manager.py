"""Secrets Manager integration for credential storage and retrieval"""

import json
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig


class SecretsManager:
    """Manages credential storage and retrieval using AWS Secrets Manager"""

    def __init__(self, aws_config: AWSConfig):
        """
        Initialize Secrets Manager.

        Args:
            aws_config: AWSConfig instance for AWS client management
        """
        self.aws_config = aws_config
        self.secrets_client = aws_config.get_client("secretsmanager")

    def store_credential(
        self,
        secret_name: str,
        credential_data: Dict[str, Any],
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Store credentials in AWS Secrets Manager.

        Args:
            secret_name: Name of the secret to store
            credential_data: Dictionary containing credential information
            description: Optional description of the secret
            tags: Optional tags for the secret

        Returns:
            Dictionary containing secret metadata

        Raises:
            ValueError: If credential storage fails
        """
        try:
            # Prepare the secret value as JSON
            secret_value = json.dumps(credential_data)

            # Prepare kwargs for create_secret
            create_kwargs = {
                "Name": secret_name,
                "SecretString": secret_value
            }

            if description:
                create_kwargs["Description"] = description

            if tags:
                create_kwargs["Tags"] = [
                    {"Key": k, "Value": v} for k, v in tags.items()
                ]

            response = self.secrets_client.create_secret(**create_kwargs)

            return {
                "secret_name": response["Name"],
                "secret_arn": response["ARN"],
                "secret_id": response["Name"],
                "version_id": response.get("VersionId")
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceExistsException":
                # Secret already exists, update it instead
                try:
                    response = self.secrets_client.update_secret(
                        SecretId=secret_name,
                        SecretString=secret_value
                    )
                    return {
                        "secret_name": response["Name"],
                        "secret_arn": response["ARN"],
                        "secret_id": response["Name"],
                        "version_id": response.get("VersionId")
                    }
                except ClientError as update_error:
                    raise ValueError(f"Failed to update existing secret: {str(update_error)}")
            else:
                raise ValueError(f"Failed to store credential: {str(e)}")

    def retrieve_credential(
        self,
        secret_name: str,
        version_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve credentials from AWS Secrets Manager.

        Args:
            secret_name: Name of the secret to retrieve
            version_id: Optional specific version ID to retrieve

        Returns:
            Dictionary containing the credential data

        Raises:
            ValueError: If credential retrieval fails
        """
        try:
            kwargs = {"SecretId": secret_name}
            if version_id:
                kwargs["VersionId"] = version_id

            response = self.secrets_client.get_secret_value(**kwargs)

            # Parse the secret value
            if "SecretString" in response:
                secret_data = json.loads(response["SecretString"])
            elif "SecretBinary" in response:
                secret_data = response["SecretBinary"]
            else:
                raise ValueError("Secret value not found in response")

            return {
                "secret_name": response["Name"],
                "secret_arn": response["ARN"],
                "version_id": response.get("VersionId"),
                "credential_data": secret_data
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Secret '{secret_name}' not found")
            elif e.response["Error"]["Code"] == "InvalidRequestException":
                raise ValueError(f"Invalid request for secret '{secret_name}'")
            elif e.response["Error"]["Code"] == "InvalidParameterException":
                raise ValueError(f"Invalid parameter for secret '{secret_name}'")
            else:
                raise ValueError(f"Failed to retrieve credential: {str(e)}")

    def validate_credential(
        self,
        secret_name: str,
        required_fields: Optional[list] = None
    ) -> bool:
        """
        Validate that a credential exists and contains required fields.

        Args:
            secret_name: Name of the secret to validate
            required_fields: Optional list of required fields in the credential

        Returns:
            True if credential is valid

        Raises:
            ValueError: If credential validation fails
        """
        try:
            # Retrieve the credential
            result = self.retrieve_credential(secret_name)
            credential_data = result["credential_data"]

            # Check if it's a dictionary
            if not isinstance(credential_data, dict):
                raise ValueError("Credential data is not a dictionary")

            # Check for required fields if specified
            if required_fields:
                missing_fields = [field for field in required_fields if field not in credential_data]
                if missing_fields:
                    raise ValueError(f"Credential missing required fields: {missing_fields}")

            return True
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Credential validation failed: {str(e)}")

    def delete_credential(self, secret_name: str, force_delete: bool = False) -> bool:
        """
        Delete a credential from AWS Secrets Manager.

        Args:
            secret_name: Name of the secret to delete
            force_delete: If True, delete immediately; if False, schedule deletion

        Returns:
            True if credential was deleted successfully

        Raises:
            ValueError: If credential deletion fails
        """
        try:
            kwargs = {"SecretId": secret_name}
            if force_delete:
                kwargs["ForceDeleteWithoutRecovery"] = True
            else:
                # Default recovery window is 7 days
                kwargs["RecoveryWindowInDays"] = 7

            response = self.secrets_client.delete_secret(**kwargs)

            return {
                "secret_name": response["Name"],
                "secret_arn": response["ARN"],
                "deletion_date": response.get("DeletionDate")
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Secret '{secret_name}' not found")
            else:
                raise ValueError(f"Failed to delete credential: {str(e)}")

    def list_credentials(self, filters: Optional[Dict[str, str]] = None) -> list:
        """
        List all credentials in AWS Secrets Manager.

        Args:
            filters: Optional filters to apply (e.g., {"key": "bedrock-rag"})

        Returns:
            List of secret metadata

        Raises:
            ValueError: If listing fails
        """
        try:
            kwargs = {}
            if filters:
                # Build filter list
                filter_list = []
                for key, value in filters.items():
                    filter_list.append({
                        "Key": key,
                        "Values": [value]
                    })
                kwargs["Filters"] = filter_list

            response = self.secrets_client.list_secrets(**kwargs)

            secrets = []
            for secret in response.get("SecretList", []):
                secrets.append({
                    "secret_name": secret["Name"],
                    "secret_arn": secret["ARN"],
                    "description": secret.get("Description"),
                    "created_date": secret.get("CreatedDate").isoformat() if secret.get("CreatedDate") else None,
                    "last_updated_date": secret.get("LastChangedDate").isoformat() if secret.get("LastChangedDate") else None,
                    "tags": secret.get("Tags", [])
                })

            return secrets
        except ClientError as e:
            raise ValueError(f"Failed to list credentials: {str(e)}")

    def get_credential_metadata(self, secret_name: str) -> Dict[str, Any]:
        """
        Get metadata about a credential without retrieving the secret value.

        Args:
            secret_name: Name of the secret

        Returns:
            Dictionary containing secret metadata

        Raises:
            ValueError: If metadata retrieval fails
        """
        try:
            response = self.secrets_client.describe_secret(SecretId=secret_name)

            return {
                "secret_name": response["Name"],
                "secret_arn": response["ARN"],
                "description": response.get("Description"),
                "created_date": response.get("CreatedDate").isoformat() if response.get("CreatedDate") else None,
                "last_updated_date": response.get("LastChangedDate").isoformat() if response.get("LastChangedDate") else None,
                "last_accessed_date": response.get("LastAccessedDate").isoformat() if response.get("LastAccessedDate") else None,
                "tags": response.get("Tags", []),
                "rotation_enabled": response.get("RotationEnabled", False),
                "versions": response.get("VersionIdsToStages", {})
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Secret '{secret_name}' not found")
            else:
                raise ValueError(f"Failed to get credential metadata: {str(e)}")

    def rotate_credential(
        self,
        secret_name: str,
        new_credential_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Rotate a credential by creating a new version.

        Args:
            secret_name: Name of the secret to rotate
            new_credential_data: New credential data

        Returns:
            Dictionary containing rotation metadata

        Raises:
            ValueError: If rotation fails
        """
        try:
            secret_value = json.dumps(new_credential_data)

            response = self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=secret_value
            )

            return {
                "secret_name": response["Name"],
                "secret_arn": response["ARN"],
                "version_id": response.get("VersionId")
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Secret '{secret_name}' not found")
            else:
                raise ValueError(f"Failed to rotate credential: {str(e)}")

    def tag_credential(
        self,
        secret_name: str,
        tags: Dict[str, str]
    ) -> bool:
        """
        Add tags to a credential.

        Args:
            secret_name: Name of the secret
            tags: Dictionary of tags to add

        Returns:
            True if tagging was successful

        Raises:
            ValueError: If tagging fails
        """
        try:
            tag_list = [{"Key": k, "Value": v} for k, v in tags.items()]

            self.secrets_client.tag_resource(
                SecretId=secret_name,
                Tags=tag_list
            )

            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Secret '{secret_name}' not found")
            else:
                raise ValueError(f"Failed to tag credential: {str(e)}")

    def untag_credential(
        self,
        secret_name: str,
        tag_keys: list
    ) -> bool:
        """
        Remove tags from a credential.

        Args:
            secret_name: Name of the secret
            tag_keys: List of tag keys to remove

        Returns:
            True if untagging was successful

        Raises:
            ValueError: If untagging fails
        """
        try:
            self.secrets_client.untag_resource(
                SecretId=secret_name,
                TagKeys=tag_keys
            )

            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Secret '{secret_name}' not found")
            else:
                raise ValueError(f"Failed to untag credential: {str(e)}")
