"""OpenSearch Serverless security policy management for Bedrock RAG Retrieval System"""

import json
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig


class OSSSecurityManager:
    """Manages OpenSearch Serverless security policies (encryption, network, data access)"""

    def __init__(self, aws_config: AWSConfig):
        """
        Initialize OSS Security Manager.

        Args:
            aws_config: AWSConfig instance for AWS client management
        """
        self.aws_config = aws_config
        self.oss_client = aws_config.get_client("opensearchserverless")
        self.account_id = aws_config.get_account_id()
        self.region = aws_config.get_region()

    def create_encryption_policy(
        self,
        policy_name: str,
        description: str = "Encryption policy for OpenSearch Serverless"
    ) -> Dict[str, Any]:
        """
        Create encryption policy for OpenSearch Serverless collection.

        Args:
            policy_name: Name of the encryption policy
            description: Description of the policy

        Returns:
            Dictionary containing policy information

        Raises:
            ValueError: If policy creation fails
        """
        policy_document = {
            "Rules": [
                {
                    "Resource": ["collection/*"],
                    "ResourceType": "collection"
                }
            ],
            "AWSOwnedKeyPolicy": {}
        }

        try:
            response = self.oss_client.create_security_policy(
                name=policy_name,
                policy=json.dumps(policy_document),
                type="encryption",
                description=description
            )
            return {
                "policy_name": response["securityPolicyDetail"]["name"],
                "policy_version": response["securityPolicyDetail"]["version"],
                "created_date": response["securityPolicyDetail"]["createdDate"],
                "policy_type": response["securityPolicyDetail"]["type"]
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                # Policy already exists, retrieve it
                try:
                    policy = self.oss_client.get_security_policy(
                        name=policy_name,
                        type="encryption"
                    )
                    return {
                        "policy_name": policy["securityPolicyDetail"]["name"],
                        "policy_version": policy["securityPolicyDetail"]["version"],
                        "created_date": policy["securityPolicyDetail"]["createdDate"],
                        "policy_type": policy["securityPolicyDetail"]["type"]
                    }
                except ClientError as get_error:
                    raise ValueError(f"Failed to retrieve existing encryption policy: {str(get_error)}")
            else:
                raise ValueError(f"Failed to create encryption policy: {str(e)}")

    def create_network_policy(
        self,
        policy_name: str,
        collection_names: List[str],
        allow_public_access: bool = False,
        description: str = "Network policy for OpenSearch Serverless"
    ) -> Dict[str, Any]:
        """
        Create network policy for OpenSearch Serverless collection.

        Args:
            policy_name: Name of the network policy
            collection_names: List of collection names to apply policy to
            allow_public_access: Whether to allow public access (default: False for private)
            description: Description of the policy

        Returns:
            Dictionary containing policy information

        Raises:
            ValueError: If policy creation fails
        """
        rules = []
        for collection_name in collection_names:
            rules.append({
                "Resource": [f"collection/{collection_name}"],
                "ResourceType": "collection"
            })

        if allow_public_access:
            # Allow public access
            policy_document = {
                "Rules": rules,
                "PublicAccessOptions": {
                    "Enabled": True
                }
            }
        else:
            # Private access only (VPC endpoints)
            policy_document = {
                "Rules": rules,
                "PublicAccessOptions": {
                    "Enabled": False
                }
            }

        try:
            response = self.oss_client.create_security_policy(
                name=policy_name,
                policy=json.dumps(policy_document),
                type="network",
                description=description
            )
            return {
                "policy_name": response["securityPolicyDetail"]["name"],
                "policy_version": response["securityPolicyDetail"]["version"],
                "created_date": response["securityPolicyDetail"]["createdDate"],
                "policy_type": response["securityPolicyDetail"]["type"],
                "public_access_enabled": allow_public_access
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                # Policy already exists, retrieve it
                try:
                    policy = self.oss_client.get_security_policy(
                        name=policy_name,
                        type="network"
                    )
                    return {
                        "policy_name": policy["securityPolicyDetail"]["name"],
                        "policy_version": policy["securityPolicyDetail"]["version"],
                        "created_date": policy["securityPolicyDetail"]["createdDate"],
                        "policy_type": policy["securityPolicyDetail"]["type"],
                        "public_access_enabled": allow_public_access
                    }
                except ClientError as get_error:
                    raise ValueError(f"Failed to retrieve existing network policy: {str(get_error)}")
            else:
                raise ValueError(f"Failed to create network policy: {str(e)}")

    def create_data_access_policy(
        self,
        policy_name: str,
        collection_names: List[str],
        principal_arns: List[str],
        description: str = "Data access policy for OpenSearch Serverless"
    ) -> Dict[str, Any]:
        """
        Create data access policy for OpenSearch Serverless collection.

        Args:
            policy_name: Name of the data access policy
            collection_names: List of collection names to apply policy to
            principal_arns: List of principal ARNs (roles/users) to grant access
            description: Description of the policy

        Returns:
            Dictionary containing policy information

        Raises:
            ValueError: If policy creation fails
        """
        # Build resource list for collections
        resources = []
        for collection_name in collection_names:
            resources.append(f"collection/{collection_name}")

        # Build statements for data access
        statements = []
        for principal_arn in principal_arns:
            statements.append({
                "Rules": [
                    {
                        "Resource": resources,
                        "ResourceType": "collection"
                    },
                    {
                        "Resource": [f"index/{collection_name}/*" for collection_name in collection_names],
                        "ResourceType": "index"
                    }
                ],
                "Principal": [principal_arn],
                "Effect": "Allow"
            })

        policy_document = {
            "Rules": statements
        }

        try:
            response = self.oss_client.create_access_policy(
                name=policy_name,
                policy=json.dumps(policy_document),
                type="data",
                description=description
            )
            return {
                "policy_name": response["accessPolicyDetail"]["name"],
                "policy_version": response["accessPolicyDetail"]["version"],
                "created_date": response["accessPolicyDetail"]["createdDate"],
                "policy_type": response["accessPolicyDetail"]["type"],
                "principals_count": len(principal_arns)
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                # Policy already exists, retrieve it
                try:
                    policy = self.oss_client.get_access_policy(
                        name=policy_name,
                        type="data"
                    )
                    return {
                        "policy_name": policy["accessPolicyDetail"]["name"],
                        "policy_version": policy["accessPolicyDetail"]["version"],
                        "created_date": policy["accessPolicyDetail"]["createdDate"],
                        "policy_type": policy["accessPolicyDetail"]["type"],
                        "principals_count": len(principal_arns)
                    }
                except ClientError as get_error:
                    raise ValueError(f"Failed to retrieve existing data access policy: {str(get_error)}")
            else:
                raise ValueError(f"Failed to create data access policy: {str(e)}")

    def update_data_access_policy(
        self,
        policy_name: str,
        collection_names: List[str],
        principal_arns: List[str],
        policy_version: str
    ) -> Dict[str, Any]:
        """
        Update an existing data access policy.

        Args:
            policy_name: Name of the data access policy
            collection_names: List of collection names to apply policy to
            principal_arns: List of principal ARNs (roles/users) to grant access
            policy_version: Current version of the policy

        Returns:
            Dictionary containing updated policy information

        Raises:
            ValueError: If policy update fails
        """
        # Build resource list for collections
        resources = []
        for collection_name in collection_names:
            resources.append(f"collection/{collection_name}")

        # Build statements for data access
        statements = []
        for principal_arn in principal_arns:
            statements.append({
                "Rules": [
                    {
                        "Resource": resources,
                        "ResourceType": "collection"
                    },
                    {
                        "Resource": [f"index/{collection_name}/*" for collection_name in collection_names],
                        "ResourceType": "index"
                    }
                ],
                "Principal": [principal_arn],
                "Effect": "Allow"
            })

        policy_document = {
            "Rules": statements
        }

        try:
            response = self.oss_client.update_access_policy(
                name=policy_name,
                policy=json.dumps(policy_document),
                type="data",
                policyVersion=policy_version
            )
            return {
                "policy_name": response["accessPolicyDetail"]["name"],
                "policy_version": response["accessPolicyDetail"]["version"],
                "created_date": response["accessPolicyDetail"]["createdDate"],
                "policy_type": response["accessPolicyDetail"]["type"],
                "principals_count": len(principal_arns)
            }
        except ClientError as e:
            raise ValueError(f"Failed to update data access policy: {str(e)}")

    def get_encryption_policy(self, policy_name: str) -> Dict[str, Any]:
        """
        Get encryption policy details.

        Args:
            policy_name: Name of the encryption policy

        Returns:
            Dictionary containing policy information

        Raises:
            ValueError: If policy cannot be retrieved
        """
        try:
            policy = self.oss_client.get_security_policy(
                name=policy_name,
                type="encryption"
            )
            return {
                "policy_name": policy["securityPolicyDetail"]["name"],
                "policy_version": policy["securityPolicyDetail"]["version"],
                "created_date": policy["securityPolicyDetail"]["createdDate"],
                "policy_type": policy["securityPolicyDetail"]["type"],
                "policy": json.loads(policy["securityPolicyDetail"]["policy"])
            }
        except ClientError as e:
            raise ValueError(f"Failed to get encryption policy: {str(e)}")

    def get_network_policy(self, policy_name: str) -> Dict[str, Any]:
        """
        Get network policy details.

        Args:
            policy_name: Name of the network policy

        Returns:
            Dictionary containing policy information

        Raises:
            ValueError: If policy cannot be retrieved
        """
        try:
            policy = self.oss_client.get_security_policy(
                name=policy_name,
                type="network"
            )
            return {
                "policy_name": policy["securityPolicyDetail"]["name"],
                "policy_version": policy["securityPolicyDetail"]["version"],
                "created_date": policy["securityPolicyDetail"]["createdDate"],
                "policy_type": policy["securityPolicyDetail"]["type"],
                "policy": json.loads(policy["securityPolicyDetail"]["policy"])
            }
        except ClientError as e:
            raise ValueError(f"Failed to get network policy: {str(e)}")

    def get_data_access_policy(self, policy_name: str) -> Dict[str, Any]:
        """
        Get data access policy details.

        Args:
            policy_name: Name of the data access policy

        Returns:
            Dictionary containing policy information

        Raises:
            ValueError: If policy cannot be retrieved
        """
        try:
            policy = self.oss_client.get_access_policy(
                name=policy_name,
                type="data"
            )
            return {
                "policy_name": policy["accessPolicyDetail"]["name"],
                "policy_version": policy["accessPolicyDetail"]["version"],
                "created_date": policy["accessPolicyDetail"]["createdDate"],
                "policy_type": policy["accessPolicyDetail"]["type"],
                "policy": json.loads(policy["accessPolicyDetail"]["policy"])
            }
        except ClientError as e:
            raise ValueError(f"Failed to get data access policy: {str(e)}")

    def delete_encryption_policy(self, policy_name: str) -> bool:
        """
        Delete an encryption policy.

        Args:
            policy_name: Name of the encryption policy to delete

        Returns:
            True if policy was deleted successfully

        Raises:
            ValueError: If deletion fails
        """
        try:
            self.oss_client.delete_security_policy(
                name=policy_name,
                type="encryption"
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Policy doesn't exist, which is fine
                return True
            else:
                raise ValueError(f"Failed to delete encryption policy: {str(e)}")

    def delete_network_policy(self, policy_name: str) -> bool:
        """
        Delete a network policy.

        Args:
            policy_name: Name of the network policy to delete

        Returns:
            True if policy was deleted successfully

        Raises:
            ValueError: If deletion fails
        """
        try:
            self.oss_client.delete_security_policy(
                name=policy_name,
                type="network"
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Policy doesn't exist, which is fine
                return True
            else:
                raise ValueError(f"Failed to delete network policy: {str(e)}")

    def delete_data_access_policy(self, policy_name: str) -> bool:
        """
        Delete a data access policy.

        Args:
            policy_name: Name of the data access policy to delete

        Returns:
            True if policy was deleted successfully

        Raises:
            ValueError: If deletion fails
        """
        try:
            self.oss_client.delete_access_policy(
                name=policy_name,
                type="data"
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Policy doesn't exist, which is fine
                return True
            else:
                raise ValueError(f"Failed to delete data access policy: {str(e)}")

    def list_security_policies(self, policy_type: str = "encryption") -> List[Dict[str, Any]]:
        """
        List all security policies of a given type.

        Args:
            policy_type: Type of policy to list ("encryption" or "network")

        Returns:
            List of policy information dictionaries

        Raises:
            ValueError: If listing fails
        """
        try:
            response = self.oss_client.list_security_policies(type=policy_type)
            policies = []
            for policy in response.get("securityPolicySummaries", []):
                policies.append({
                    "policy_name": policy["name"],
                    "policy_version": policy["version"],
                    "created_date": policy["createdDate"],
                    "policy_type": policy["type"]
                })
            return policies
        except ClientError as e:
            raise ValueError(f"Failed to list security policies: {str(e)}")

    def list_access_policies(self) -> List[Dict[str, Any]]:
        """
        List all data access policies.

        Returns:
            List of access policy information dictionaries

        Raises:
            ValueError: If listing fails
        """
        try:
            response = self.oss_client.list_access_policies(type="data")
            policies = []
            for policy in response.get("accessPolicySummaries", []):
                policies.append({
                    "policy_name": policy["name"],
                    "policy_version": policy["version"],
                    "created_date": policy["createdDate"],
                    "policy_type": policy["type"]
                })
            return policies
        except ClientError as e:
            raise ValueError(f"Failed to list access policies: {str(e)}")

    def validate_policy_consistency(
        self,
        encryption_policy_name: str,
        network_policy_name: str,
        data_access_policy_name: str
    ) -> Dict[str, bool]:
        """
        Validate that all three security policies are properly configured.

        Args:
            encryption_policy_name: Name of the encryption policy
            network_policy_name: Name of the network policy
            data_access_policy_name: Name of the data access policy

        Returns:
            Dictionary with validation results for each policy

        Raises:
            ValueError: If validation fails
        """
        results = {}

        try:
            self.get_encryption_policy(encryption_policy_name)
            results["encryption_policy_valid"] = True
        except ValueError:
            results["encryption_policy_valid"] = False

        try:
            self.get_network_policy(network_policy_name)
            results["network_policy_valid"] = True
        except ValueError:
            results["network_policy_valid"] = False

        try:
            self.get_data_access_policy(data_access_policy_name)
            results["data_access_policy_valid"] = True
        except ValueError:
            results["data_access_policy_valid"] = False

        return results
