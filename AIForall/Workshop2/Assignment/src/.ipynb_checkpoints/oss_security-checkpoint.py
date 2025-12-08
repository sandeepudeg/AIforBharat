# """OpenSearch Serverless security policy management for Bedrock RAG Retrieval System"""

# import json
# from typing import Dict, Any, List
# from botocore.exceptions import ClientError
# from config.aws_config import AWSConfig


# class OSSSecurityManager:
#     """Manages OpenSearch Serverless security policies (encryption, network, data access)"""

#     def __init__(self, aws_config: AWSConfig):
#         """
#         Initialize OSS Security Manager.

#         Args:
#             aws_config: AWSConfig instance for AWS client management
#         """
#         self.aws_config = aws_config
#         self.oss_client = aws_config.get_client("opensearchserverless")
#         self.account_id = aws_config.get_account_id()
#         self.region = aws_config.get_region()

#     # --------------------------------------------------------------------- #
#     # ENCRYPTION POLICY
#     # --------------------------------------------------------------------- #
#     def create_encryption_policy(
#         self,
#         policy_name: str,
#         description: str = "Encryption policy for OpenSearch Serverless",
#     ) -> Dict[str, Any]:
#         """
#         Create encryption policy for OpenSearch Serverless collection.

#         Args:
#             policy_name: Name of the encryption policy
#             description: Description of the policy

#         Returns:
#             Dictionary containing policy information

#         Raises:
#             ValueError: If policy creation fails
#         """
#         # Use AWS-owned key for all collections
#         policy_document = {
#             "Rules": [
#                 {
#                     "Resource": ["collection/*"],
#                     "ResourceType": "collection",
#                 }
#             ],
#             "AWSOwnedKey": True,
#         }

#         try:
#             response = self.oss_client.create_security_policy(
#                 name=policy_name,
#                 policy=json.dumps(policy_document),
#                 type="encryption",
#                 description=description,
#             )
#             detail = response["securityPolicyDetail"]
#             return {
#                 "policy_name": detail["name"],
#                 "policy_version": detail.get("policyVersion", detail.get("version")),
#                 "created_date": detail["createdDate"],
#                 "policy_type": detail["type"],
#             }
#         except ClientError as e:
#             if e.response["Error"]["Code"] == "ConflictException":
#                 # Policy already exists, retrieve it
#                 try:
#                     policy = self.oss_client.get_security_policy(
#                         name=policy_name,
#                         type="encryption",
#                     )
#                     detail = policy["securityPolicyDetail"]
#                     return {
#                         "policy_name": detail["name"],
#                         "policy_version": detail.get(
#                             "policyVersion", detail.get("version")
#                         ),
#                         "created_date": detail["createdDate"],
#                         "policy_type": detail["type"],
#                     }
#                 except ClientError as get_error:
#                     raise ValueError(
#                         f"Failed to retrieve existing encryption policy: {str(get_error)}"
#                     )
#             else:
#                 raise ValueError(f"Failed to create encryption policy: {str(e)}")

#     # --------------------------------------------------------------------- #
#     # NETWORK POLICY
#     # --------------------------------------------------------------------- #
#         def create_network_policy(
#         self,
#         policy_name: str,
#         collection_names: List[str],
#         allow_public_access: bool = False,
#         description: str = "Network policy for OpenSearch Serverless",
#     ) -> Dict[str, Any]:
#         """
#         Create network policy for OpenSearch Serverless collection.
#         """
#         rules = []
#         for collection_name in collection_names:
#             rules.append(
#                 {
#                     "Resource": [f"collection/{collection_name}"],
#                     "ResourceType": "collection",
#                 }
#             )

#         # Network policy MUST be a JSON array
#         if allow_public_access:
#             # Public access for the collections
#             policy_document = [
#                 {
#                     "Description": description,
#                     "Rules": rules,
#                     "AllowFromPublic": True,
#                 }
#             ]
#         else:
#             # Private access only, allow from Amazon Bedrock
#             policy_document = [
#                 {
#                     "Description": description,
#                     "Rules": rules,
#                     "AllowFromPublic": False,
#                     "SourceServices": ["bedrock.amazonaws.com"],
#                 }
#             ]

#         try:
#             response = self.oss_client.create_security_policy(
#                 name=policy_name,
#                 policy=json.dumps(policy_document),
#                 type="network",
#                 description=description,
#             )
#             detail = response["securityPolicyDetail"]
#             return {
#                 "policy_name": detail["name"],
#                 "policy_version": detail.get("policyVersion", detail.get("version")),
#                 "created_date": detail["createdDate"],
#                 "policy_type": detail["type"],
#                 "public_access_enabled": allow_public_access,
#             }
#         except ClientError as e:
#             if e.response["Error"]["Code"] == "ConflictException":
#                 # Policy already exists, retrieve it
#                 try:
#                     policy = self.oss_client.get_security_policy(
#                         name=policy_name,
#                         type="network",
#                     )
#                     detail = policy["securityPolicyDetail"]
#                     return {
#                         "policy_name": detail["name"],
#                         "policy_version": detail.get(
#                             "policyVersion", detail.get("version")
#                         ),
#                         "created_date": detail["createdDate"],
#                         "policy_type": detail["type"],
#                         "public_access_enabled": allow_public_access,
#                     }
#                 except ClientError as get_error:
#                     raise ValueError(
#                         f"Failed to retrieve existing network policy: {str(get_error)}"
#                     )
#             else:
#                 raise ValueError(f"Failed to create network policy: {str(e)}")


#     # --------------------------------------------------------------------- #
#     # DATA ACCESS POLICY
#     # --------------------------------------------------------------------- #
#         def create_data_access_policy(
#         self,
#         policy_name: str,
#         collection_names: List[str],
#         principal_arns: List[str],
#         description: str = "Data access policy for OpenSearch Serverless",
#     ) -> Dict[str, Any]:
#         """
#         Create data access policy for OpenSearch Serverless collection.
#         """
#         # Index resources for all collections
#         index_resources = [
#             f"index/{collection_name}/*" for collection_name in collection_names
#         ]

#         policy_document = [
#             {
#                 "Description": description,
#                 "Rules": [
#                     {
#                         "Resource": index_resources,
#                         "Permission": [
#                             "aoss:DescribeIndex",
#                             "aoss:ReadDocument",
#                             "aoss:WriteDocument",
#                         ],
#                         "ResourceType": "index",
#                     }
#                 ],
#                 "Principal": principal_arns,
#             }
#         ]

#         try:
#             response = self.oss_client.create_access_policy(
#                 name=policy_name,
#                 policy=json.dumps(policy_document),
#                 type="data",
#                 description=description,
#             )
#             detail = response["accessPolicyDetail"]
#             return {
#                 "policy_name": detail["name"],
#                 "policy_version": detail.get("policyVersion", detail.get("version")),
#                 "created_date": detail["createdDate"],
#                 "policy_type": detail["type"],
#                 "principals_count": len(principal_arns),
#             }
#         except ClientError as e:
#             if e.response["Error"]["Code"] == "ConflictException":
#                 # Policy already exists, retrieve it
#                 try:
#                     policy = self.oss_client.get_access_policy(
#                         name=policy_name,
#                         type="data",
#                     )
#                     detail = policy["accessPolicyDetail"]
#                     return {
#                         "policy_name": detail["name"],
#                         "policy_version": detail.get(
#                             "policyVersion", detail.get("version")
#                         ),
#                         "created_date": detail["createdDate"],
#                         "policy_type": detail["type"],
#                         "principals_count": len(principal_arns),
#                     }
#                 except ClientError as get_error:
#                     raise ValueError(
#                         f"Failed to retrieve existing data access policy: {str(get_error)}"
#                     )
#             else:
#                 raise ValueError(f"Failed to create data access policy: {str(e)}")


#         def update_data_access_policy(
#         self,
#         policy_name: str,
#         collection_names: List[str],
#         principal_arns: List[str],
#         policy_version: str,
#     ) -> Dict[str, Any]:
#         """
#         Update an existing data access policy.
#         """
#         index_resources = [
#             f"index/{collection_name}/*" for collection_name in collection_names
#         ]

#         policy_document = [
#             {
#                 "Description": f"Updated {policy_name}",
#                 "Rules": [
#                     {
#                         "Resource": index_resources,
#                         "Permission": [
#                             "aoss:DescribeIndex",
#                             "aoss:ReadDocument",
#                             "aoss:WriteDocument",
#                         ],
#                         "ResourceType": "index",
#                     }
#                 ],
#                 "Principal": principal_arns,
#             }
#         ]

#         try:
#             response = self.oss_client.update_access_policy(
#                 name=policy_name,
#                 policy=json.dumps(policy_document),
#                 type="data",
#                 policyVersion=policy_version,
#             )
#             detail = response["accessPolicyDetail"]
#             return {
#                 "policy_name": detail["name"],
#                 "policy_version": detail.get("policyVersion", detail.get("version")),
#                 "created_date": detail["createdDate"],
#                 "policy_type": detail["type"],
#                 "principals_count": len(principal_arns),
#             }
#         except ClientError as e:
#             raise ValueError(f"Failed to update data access policy: {str(e)}")

#     # --------------------------------------------------------------------- #
#     # GETTERS
#     # --------------------------------------------------------------------- #
#     def get_encryption_policy(self, policy_name: str) -> Dict[str, Any]:
#         """
#         Get encryption policy details.
#         """
#         try:
#             policy = self.oss_client.get_security_policy(
#                 name=policy_name,
#                 type="encryption",
#             )
#             detail = policy["securityPolicyDetail"]
#             return {
#                 "policy_name": detail["name"],
#                 "policy_version": detail.get("policyVersion", detail.get("version")),
#                 "created_date": detail["createdDate"],
#                 "policy_type": detail["type"],
#                 "policy": json.loads(detail["policy"]),
#             }
#         except ClientError as e:
#             raise ValueError(f"Failed to get encryption policy: {str(e)}")

#     def get_network_policy(self, policy_name: str) -> Dict[str, Any]:
#         """
#         Get network policy details.
#         """
#         try:
#             policy = self.oss_client.get_security_policy(
#                 name=policy_name,
#                 type="network",
#             )
#             detail = policy["securityPolicyDetail"]
#             return {
#                 "policy_name": detail["name"],
#                 "policy_version": detail.get("policyVersion", detail.get("version")),
#                 "created_date": detail["createdDate"],
#                 "policy_type": detail["type"],
#                 "policy": json.loads(detail["policy"]),
#             }
#         except ClientError as e:
#             raise ValueError(f"Failed to get network policy: {str(e)}")

#     def get_data_access_policy(self, policy_name: str) -> Dict[str, Any]:
#         """
#         Get data access policy details.
#         """
#         try:
#             policy = self.oss_client.get_access_policy(
#                 name=policy_name,
#                 type="data",
#             )
#             detail = policy["accessPolicyDetail"]
#             return {
#                 "policy_name": detail["name"],
#                 "policy_version": detail.get("policyVersion", detail.get("version")),
#                 "created_date": detail["createdDate"],
#                 "policy_type": detail["type"],
#                 "policy": json.loads(detail["policy"]),
#             }
#         except ClientError as e:
#             raise ValueError(f"Failed to get data access policy: {str(e)}")

#     # --------------------------------------------------------------------- #
#     # DELETE
#     # --------------------------------------------------------------------- #
#     def delete_encryption_policy(self, policy_name: str) -> bool:
#         """
#         Delete an encryption policy.
#         """
#         try:
#             self.oss_client.delete_security_policy(
#                 name=policy_name,
#                 type="encryption",
#             )
#             return True
#         except ClientError as e:
#             if e.response["Error"]["Code"] == "ResourceNotFoundException":
#                 return True
#             else:
#                 raise ValueError(f"Failed to delete encryption policy: {str(e)}")

#     def delete_network_policy(self, policy_name: str) -> bool:
#         """
#         Delete a network policy.
#         """
#         try:
#             self.oss_client.delete_security_policy(
#                 name=policy_name,
#                 type="network",
#             )
#             return True
#         except ClientError as e:
#             if e.response["Error"]["Code"] == "ResourceNotFoundException":
#                 return True
#             else:
#                 raise ValueError(f"Failed to delete network policy: {str(e)}")

#     def delete_data_access_policy(self, policy_name: str) -> bool:
#         """
#         Delete a data access policy.
#         """
#         try:
#             self.oss_client.delete_access_policy(
#                 name=policy_name,
#                 type="data",
#             )
#             return True
#         except ClientError as e:
#             if e.response["Error"]["Code"] == "ResourceNotFoundException":
#                 return True
#             else:
#                 raise ValueError(f"Failed to delete data access policy: {str(e)}")

#     # --------------------------------------------------------------------- #
#     # LIST
#     # --------------------------------------------------------------------- #
#     def list_security_policies(self, policy_type: str = "encryption") -> List[Dict[str, Any]]:
#         """
#         List all security policies of a given type.

#         Args:
#             policy_type: Type of policy to list ("encryption" or "network")

#         Returns:
#             List of policy information dictionaries
#         """
#         try:
#             response = self.oss_client.list_security_policies(type=policy_type)
#             policies: List[Dict[str, Any]] = []
#             for policy in response.get("securityPolicySummaries", []):
#                 policies.append(
#                     {
#                         "policy_name": policy["name"],
#                         "policy_version": policy.get("policyVersion", policy.get("version")),
#                         "created_date": policy["createdDate"],
#                         "policy_type": policy["type"],
#                     }
#                 )
#             return policies
#         except ClientError as e:
#             raise ValueError(f"Failed to list security policies: {str(e)}")

#     def list_access_policies(self) -> List[Dict[str, Any]]:
#         """
#         List all data access policies.
#         """
#         try:
#             response = self.oss_client.list_access_policies(type="data")
#             policies: List[Dict[str, Any]] = []
#             for policy in response.get("accessPolicySummaries", []):
#                 policies.append(
#                     {
#                         "policy_name": policy["name"],
#                         "policy_version": policy.get("policyVersion", policy.get("version")),
#                         "created_date": policy["createdDate"],
#                         "policy_type": policy["type"],
#                     }
#                 )
#             return policies
#         except ClientError as e:
#             raise ValueError(f"Failed to list access policies: {str(e)}")

#     # --------------------------------------------------------------------- #
#     # VALIDATION
#     # --------------------------------------------------------------------- #
#     def validate_policy_consistency(
#         self,
#         encryption_policy_name: str,
#         network_policy_name: str,
#         data_access_policy_name: str,
#     ) -> Dict[str, bool]:
#         """
#         Validate that all three security policies are properly configured.
#         """
#         results: Dict[str, bool] = {}

#         try:
#             self.get_encryption_policy(encryption_policy_name)
#             results["encryption_policy_valid"] = True
#         except ValueError:
#             results["encryption_policy_valid"] = False

#         try:
#             self.get_network_policy(network_policy_name)
#             results["network_policy_valid"] = True
#         except ValueError:
#             results["network_policy_valid"] = False

#         try:
#             self.get_data_access_policy(data_access_policy_name)
#             results["data_access_policy_valid"] = True
#         except ValueError:
#             results["data_access_policy_valid"] = False

#         return results
import json
from typing import Dict, Any, List
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig


class OSSSecurityManager:
    # Manages OpenSearch Serverless security policies (encryption, network, data access)

    def __init__(self, aws_config: AWSConfig):
        self.aws_config = aws_config
        self.oss_client = aws_config.get_client("opensearchserverless")
        self.account_id = aws_config.get_account_id()
        self.region = aws_config.get_region()

    # ---------------- Encryption policy ----------------
    def create_encryption_policy(
        self,
        policy_name: str,
        description: str = "Encryption policy for OpenSearch Serverless",
    ) -> Dict[str, Any]:
        policy_document = {
            "Rules": [
                {"Resource": ["collection/*"], "ResourceType": "collection"}
            ],
            "AWSOwnedKey": True,
        }

        try:
            response = self.oss_client.create_security_policy(
                name=policy_name,
                policy=json.dumps(policy_document),
                type="encryption",
                description=description,
            )
            detail = response["securityPolicyDetail"]
            return {
                "policy_name": detail["name"],
                "policy_version": detail.get("policyVersion", detail.get("version")),
                "created_date": detail["createdDate"],
                "policy_type": detail["type"],
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                policy = self.oss_client.get_security_policy(
                    name=policy_name,
                    type="encryption",
                )
                detail = policy["securityPolicyDetail"]
                return {
                    "policy_name": detail["name"],
                    "policy_version": detail.get(
                        "policyVersion", detail.get("version")
                    ),
                    "created_date": detail["createdDate"],
                    "policy_type": detail["type"],
                }
            raise

    # ---------------- Network policy ----------------
    def create_network_policy(
        self,
        policy_name: str,
        collection_names: List[str],
        allow_public_access: bool = False,
        description: str = "Network policy for OpenSearch Serverless",
    ) -> Dict[str, Any]:
        rules = [
            {"Resource": [f"collection/{name}"], "ResourceType": "collection"}
            for name in collection_names
        ]

        if allow_public_access:
            policy_document = [
                {"Description": description, "Rules": rules, "AllowFromPublic": True}
            ]
        else:
            policy_document = [
                {
                    "Description": description,
                    "Rules": rules,
                    "AllowFromPublic": False,
                    "SourceServices": ["bedrock.amazonaws.com"],
                }
            ]

        try:
            response = self.oss_client.create_security_policy(
                name=policy_name,
                policy=json.dumps(policy_document),
                type="network",
                description=description,
            )
            detail = response["securityPolicyDetail"]
            return {
                "policy_name": detail["name"],
                "policy_version": detail.get("policyVersion", detail.get("version")),
                "created_date": detail["createdDate"],
                "policy_type": detail["type"],
                "public_access_enabled": allow_public_access,
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                policy = self.oss_client.get_security_policy(
                    name=policy_name,
                    type="network",
                )
                detail = policy["securityPolicyDetail"]
                return {
                    "policy_name": detail["name"],
                    "policy_version": detail.get(
                        "policyVersion", detail.get("version")
                    ),
                    "created_date": detail["createdDate"],
                    "policy_type": detail["type"],
                    "public_access_enabled": allow_public_access,
                }
            raise

    # ---------------- Data access policy ----------------
    def create_data_access_policy(
        self,
        policy_name: str,
        collection_names: List[str],
        principal_arns: List[str],
        description: str = "Data access policy for OpenSearch Serverless",
    ) -> Dict[str, Any]:
        index_resources = [f"index/{name}/*" for name in collection_names]

        policy_document = [
            {
                "Description": description,
                "Rules": [
                    {
                        "Resource": index_resources,
                        "Permission": [
                            "aoss:DescribeIndex",
                            "aoss:ReadDocument",
                            "aoss:WriteDocument",
                        ],
                        "ResourceType": "index",
                    }
                ],
                "Principal": principal_arns,
            }
        ]

        try:
            response = self.oss_client.create_access_policy(
                name=policy_name,
                policy=json.dumps(policy_document),
                type="data",
                description=description,
            )
            detail = response["accessPolicyDetail"]
            return {
                "policy_name": detail["name"],
                "policy_version": detail.get("policyVersion", detail.get("version")),
                "created_date": detail["createdDate"],
                "policy_type": detail["type"],
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConflictException":
                policy = self.oss_client.get_access_policy(
                    name=policy_name,
                    type="data",
                )
                detail = policy["accessPolicyDetail"]
                return {
                    "policy_name": detail["name"],
                    "policy_version": detail.get(
                        "policyVersion", detail.get("version")
                    ),
                    "created_date": detail["createdDate"],
                    "policy_type": detail["type"],
                }
            raise

    # ---------------- Getters ----------------
    def get_encryption_policy(self, policy_name: str) -> Dict[str, Any]:
        policy = self.oss_client.get_security_policy(
            name=policy_name,
            type="encryption",
        )
        detail = policy["securityPolicyDetail"]
        return {
            "policy_name": detail["name"],
            "policy_version": detail.get("policyVersion", detail.get("version")),
            "created_date": detail["createdDate"],
            "policy_type": detail["type"],
            "policy": json.loads(detail["policy"]),
        }

    def get_network_policy(self, policy_name: str) -> Dict[str, Any]:
        policy = self.oss_client.get_security_policy(
            name=policy_name,
            type="network",
        )
        detail = policy["securityPolicyDetail"]
        return {
            "policy_name": detail["name"],
            "policy_version": detail.get("policyVersion", detail.get("version")),
            "created_date": detail["createdDate"],
            "policy_type": detail["type"],
            "policy": json.loads(detail["policy"]),
        }

    def get_data_access_policy(self, policy_name: str) -> Dict[str, Any]:
        policy = self.oss_client.get_access_policy(
            name=policy_name,
            type="data",
        )
        detail = policy["accessPolicyDetail"]
        return {
            "policy_name": detail["name"],
            "policy_version": detail.get("policyVersion", detail.get("version")),
            "created_date": detail["createdDate"],
            "policy_type": detail["type"],
            "policy": json.loads(detail["policy"]),
        }
