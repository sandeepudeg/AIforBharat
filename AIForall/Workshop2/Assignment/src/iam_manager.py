"""IAM role and policy management for Bedrock RAG Retrieval System"""

import json
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig


class IAMManager:
    """Manages IAM roles and policies for Bedrock RAG system"""

    def __init__(self, aws_config: AWSConfig):
        """
        Initialize IAM Manager.

        Args:
            aws_config: AWSConfig instance for AWS client management
        """
        self.aws_config = aws_config
        self.iam_client = aws_config.get_client("iam")
        self.account_id = aws_config.get_account_id()

    def create_knowledge_base_execution_role(
        self,
        role_name: str,
        description: str = "Execution role for Bedrock Knowledge Base"
    ) -> Dict[str, Any]:
        """
        Create IAM role for Knowledge Base execution.

        Args:
            role_name: Name of the IAM role to create
            description: Description of the role

        Returns:
            Dictionary containing role information

        Raises:
            ValueError: If role creation fails
        """
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        try:
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=description,
                MaxSessionDuration=3600
            )
            return {
                "role_name": response["Role"]["RoleName"],
                "role_arn": response["Role"]["Arn"],
                "role_id": response["Role"]["RoleId"]
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "EntityAlreadyExists":
                # Role already exists, retrieve it
                try:
                    role = self.iam_client.get_role(RoleName=role_name)
                    return {
                        "role_name": role["Role"]["RoleName"],
                        "role_arn": role["Role"]["Arn"],
                        "role_id": role["Role"]["RoleId"]
                    }
                except ClientError as get_error:
                    raise ValueError(f"Failed to retrieve existing role: {str(get_error)}")
            else:
                raise ValueError(f"Failed to create IAM role: {str(e)}")

    def create_foundation_model_policy(
        self,
        policy_name: str,
        models: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create policy for accessing foundation models.

        Args:
            policy_name: Name of the policy
            models: List of model ARNs to allow access to (None = all models)

        Returns:
            Dictionary containing policy information

        Raises:
            ValueError: If policy creation fails
        """
        if models is None:
            # Allow access to all foundation models
            model_resource = f"arn:aws:bedrock:{self.aws_config.get_region()}::foundation-model/*"
        else:
            model_resource = models

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    "Resource": model_resource
                }
            ]
        }

        try:
            response = self.iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document),
                Description="Policy for accessing Bedrock foundation models"
            )
            return {
                "policy_name": response["Policy"]["PolicyName"],
                "policy_arn": response["Policy"]["Arn"],
                "policy_id": response["Policy"]["PolicyId"]
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "EntityAlreadyExists":
                # Policy already exists, retrieve it
                try:
                    policy_arn = f"arn:aws:iam::{self.account_id}:policy/{policy_name}"
                    policy = self.iam_client.get_policy(PolicyArn=policy_arn)
                    return {
                        "policy_name": policy["Policy"]["PolicyName"],
                        "policy_arn": policy["Policy"]["Arn"],
                        "policy_id": policy["Policy"]["PolicyId"]
                    }
                except ClientError as get_error:
                    raise ValueError(f"Failed to retrieve existing policy: {str(get_error)}")
            else:
                raise ValueError(f"Failed to create foundation model policy: {str(e)}")

    def create_s3_bucket_policy(
        self,
        policy_name: str,
        bucket_names: List[str]
    ) -> Dict[str, Any]:
        """
        Create policy for S3 bucket access.

        Args:
            policy_name: Name of the policy
            bucket_names: List of S3 bucket names to allow access to

        Returns:
            Dictionary containing policy information

        Raises:
            ValueError: If policy creation fails
        """
        s3_resources = []
        for bucket_name in bucket_names:
            s3_resources.append(f"arn:aws:s3:::{bucket_name}")
            s3_resources.append(f"arn:aws:s3:::{bucket_name}/*")

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:GetObjectVersion",
                        "s3:ListBucket",
                        "s3:GetBucketVersioning"
                    ],
                    "Resource": s3_resources
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": [f"arn:aws:s3:::{bucket}/*" for bucket in bucket_names]
                }
            ]
        }

        try:
            response = self.iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document),
                Description="Policy for accessing S3 buckets for document storage"
            )
            return {
                "policy_name": response["Policy"]["PolicyName"],
                "policy_arn": response["Policy"]["Arn"],
                "policy_id": response["Policy"]["PolicyId"]
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "EntityAlreadyExists":
                # Policy already exists, retrieve it
                try:
                    policy_arn = f"arn:aws:iam::{self.account_id}:policy/{policy_name}"
                    policy = self.iam_client.get_policy(PolicyArn=policy_arn)
                    return {
                        "policy_name": policy["Policy"]["PolicyName"],
                        "policy_arn": policy["Policy"]["Arn"],
                        "policy_id": policy["Policy"]["PolicyId"]
                    }
                except ClientError as get_error:
                    raise ValueError(f"Failed to retrieve existing policy: {str(get_error)}")
            else:
                raise ValueError(f"Failed to create S3 bucket policy: {str(e)}")

    def create_cloudwatch_logging_policy(
        self,
        policy_name: str,
        log_group_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create policy for CloudWatch logging.

        Args:
            policy_name: Name of the policy
            log_group_name: CloudWatch log group name (None = all log groups)

        Returns:
            Dictionary containing policy information

        Raises:
            ValueError: If policy creation fails
        """
        if log_group_name:
            log_resource = f"arn:aws:logs:{self.aws_config.get_region()}:{self.account_id}:log-group:{log_group_name}:*"
        else:
            log_resource = f"arn:aws:logs:{self.aws_config.get_region()}:{self.account_id}:log-group:*"

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": log_resource
                }
            ]
        }

        try:
            response = self.iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document),
                Description="Policy for CloudWatch logging"
            )
            return {
                "policy_name": response["Policy"]["PolicyName"],
                "policy_arn": response["Policy"]["Arn"],
                "policy_id": response["Policy"]["PolicyId"]
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "EntityAlreadyExists":
                # Policy already exists, retrieve it
                try:
                    policy_arn = f"arn:aws:iam::{self.account_id}:policy/{policy_name}"
                    policy = self.iam_client.get_policy(PolicyArn=policy_arn)
                    return {
                        "policy_name": policy["Policy"]["PolicyName"],
                        "policy_arn": policy["Policy"]["Arn"],
                        "policy_id": policy["Policy"]["PolicyId"]
                    }
                except ClientError as get_error:
                    raise ValueError(f"Failed to retrieve existing policy: {str(get_error)}")
            else:
                raise ValueError(f"Failed to create CloudWatch logging policy: {str(e)}")

    def attach_policy_to_role(
        self,
        role_name: str,
        policy_arn: str
    ) -> bool:
        """
        Attach a policy to a role.

        Args:
            role_name: Name of the IAM role
            policy_arn: ARN of the policy to attach

        Returns:
            True if policy was attached successfully

        Raises:
            ValueError: If attachment fails
        """
        try:
            self.iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                raise ValueError(f"Role or policy does not exist: {str(e)}")
            elif e.response["Error"]["Code"] == "LimitExceeded":
                raise ValueError(f"Policy limit exceeded: {str(e)}")
            else:
                raise ValueError(f"Failed to attach policy to role: {str(e)}")

    def detach_policy_from_role(
        self,
        role_name: str,
        policy_arn: str
    ) -> bool:
        """
        Detach a policy from a role.

        Args:
            role_name: Name of the IAM role
            policy_arn: ARN of the policy to detach

        Returns:
            True if policy was detached successfully

        Raises:
            ValueError: If detachment fails
        """
        try:
            self.iam_client.detach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            return True
        except ClientError as e:
            raise ValueError(f"Failed to detach policy from role: {str(e)}")

    def delete_role(self, role_name: str) -> bool:
        """
        Delete an IAM role.

        Args:
            role_name: Name of the IAM role to delete

        Returns:
            True if role was deleted successfully

        Raises:
            ValueError: If deletion fails
        """
        try:
            # First, detach all policies from the role
            attached_policies = self.iam_client.list_attached_role_policies(
                RoleName=role_name
            )
            for policy in attached_policies["AttachedPolicies"]:
                self.iam_client.detach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy["PolicyArn"]
                )

            # Then delete the role
            self.iam_client.delete_role(RoleName=role_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                # Role doesn't exist, which is fine
                return True
            else:
                raise ValueError(f"Failed to delete role: {str(e)}")

    def delete_policy(self, policy_arn: str) -> bool:
        """
        Delete an IAM policy.

        Args:
            policy_arn: ARN of the policy to delete

        Returns:
            True if policy was deleted successfully

        Raises:
            ValueError: If deletion fails
        """
        try:
            # First, detach policy from all roles
            entities = self.iam_client.list_entities_for_policy(PolicyArn=policy_arn)
            for role in entities.get("PolicyRoles", []):
                self.iam_client.detach_role_policy(
                    RoleName=role["RoleName"],
                    PolicyArn=policy_arn
                )

            # Then delete the policy
            self.iam_client.delete_policy(PolicyArn=policy_arn)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                # Policy doesn't exist, which is fine
                return True
            else:
                raise ValueError(f"Failed to delete policy: {str(e)}")

    def get_role_info(self, role_name: str) -> Dict[str, Any]:
        """
        Get information about an IAM role.

        Args:
            role_name: Name of the IAM role

        Returns:
            Dictionary containing role information

        Raises:
            ValueError: If role cannot be retrieved
        """
        try:
            role = self.iam_client.get_role(RoleName=role_name)
            return {
                "role_name": role["Role"]["RoleName"],
                "role_arn": role["Role"]["Arn"],
                "role_id": role["Role"]["RoleId"],
                "create_date": role["Role"]["CreateDate"].isoformat()
            }
        except ClientError as e:
            raise ValueError(f"Failed to get role information: {str(e)}")

    def get_policy_info(self, policy_arn: str) -> Dict[str, Any]:
        """
        Get information about an IAM policy.

        Args:
            policy_arn: ARN of the IAM policy

        Returns:
            Dictionary containing policy information

        Raises:
            ValueError: If policy cannot be retrieved
        """
        try:
            policy = self.iam_client.get_policy(PolicyArn=policy_arn)
            return {
                "policy_name": policy["Policy"]["PolicyName"],
                "policy_arn": policy["Policy"]["Arn"],
                "policy_id": policy["Policy"]["PolicyId"],
                "create_date": policy["Policy"]["CreateDate"].isoformat()
            }
        except ClientError as e:
            raise ValueError(f"Failed to get policy information: {str(e)}")
