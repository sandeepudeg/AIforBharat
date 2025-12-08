"""S3 bucket management for Bedrock RAG Retrieval System"""

import os
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig


class S3Manager:
    """Manages S3 buckets for document storage and ingestion"""

    def __init__(self, aws_config: AWSConfig):
        """
        Initialize S3 Manager.

        Args:
            aws_config: AWSConfig instance for AWS client management
        """
        self.aws_config = aws_config
        self.s3_client = aws_config.get_client("s3")
        self.region = aws_config.get_region()

    def create_bucket(
        self,
        bucket_name: str,
        region: Optional[str] = None,
        versioning_enabled: bool = False,
        public_access_blocked: bool = True
    ) -> Dict[str, Any]:
        """
        Create an S3 bucket for document storage.

        Args:
            bucket_name: Name of the S3 bucket to create
            region: AWS region for the bucket (defaults to configured region)
            versioning_enabled: Whether to enable versioning on the bucket
            public_access_blocked: Whether to block all public access

        Returns:
            Dictionary containing bucket information

        Raises:
            ValueError: If bucket creation fails
        """
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("bucket_name cannot be empty")

        # Validate bucket name format
        if not self._validate_bucket_name(bucket_name):
            raise ValueError(
                f"Invalid bucket name '{bucket_name}'. "
                "Bucket names must be 3-63 characters, lowercase, and contain only alphanumeric characters, hyphens, and dots."
            )

        region = region or self.region

        try:
            # Check if bucket already exists
            if self.bucket_exists(bucket_name):
                return {
                    "bucket_name": bucket_name,
                    "region": region,
                    "status": "already_exists",
                    "arn": f"arn:aws:s3:::{bucket_name}"
                }

            # Create the bucket
            if region == "us-east-1":
                # us-east-1 doesn't require LocationConstraint
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region}
                )

            # Enable versioning if requested
            if versioning_enabled:
                self.s3_client.put_bucket_versioning(
                    Bucket=bucket_name,
                    VersioningConfiguration={"Status": "Enabled"}
                )

            # Block public access if requested
            if public_access_blocked:
                self.s3_client.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        "BlockPublicAcls": True,
                        "IgnorePublicAcls": True,
                        "BlockPublicPolicy": True,
                        "RestrictPublicBuckets": True
                    }
                )

            return {
                "bucket_name": bucket_name,
                "region": region,
                "status": "created",
                "versioning_enabled": versioning_enabled,
                "public_access_blocked": public_access_blocked,
                "arn": f"arn:aws:s3:::{bucket_name}"
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "BucketAlreadyExists":
                # Bucket exists in another account
                raise ValueError(f"Bucket '{bucket_name}' already exists in another AWS account")
            elif e.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
                # Bucket already exists and is owned by this account
                return {
                    "bucket_name": bucket_name,
                    "region": region,
                    "status": "already_exists",
                    "arn": f"arn:aws:s3:::{bucket_name}"
                }
            else:
                raise ValueError(f"Failed to create S3 bucket: {str(e)}")

    def bucket_exists(self, bucket_name: str) -> bool:
        """
        Check if an S3 bucket exists and is accessible.

        Args:
            bucket_name: Name of the S3 bucket

        Returns:
            True if bucket exists and is accessible, False otherwise

        Raises:
            ValueError: If bucket check fails
        """
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("bucket_name cannot be empty")

        try:
            self.s3_client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            elif e.response["Error"]["Code"] == "403":
                # Bucket exists but we don't have access
                raise ValueError(f"Access denied to bucket '{bucket_name}'")
            else:
                # For other errors, assume bucket doesn't exist
                return False

    def get_bucket_info(self, bucket_name: str) -> Dict[str, Any]:
        """
        Get information about an S3 bucket.

        Args:
            bucket_name: Name of the S3 bucket

        Returns:
            Dictionary containing bucket information

        Raises:
            ValueError: If bucket cannot be accessed
        """
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("bucket_name cannot be empty")

        try:
            # Get bucket location
            location_response = self.s3_client.get_bucket_location(Bucket=bucket_name)
            region = location_response.get("LocationConstraint") or "us-east-1"

            # Get versioning status
            versioning_response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
            versioning_enabled = versioning_response.get("Status") == "Enabled"

            # Get public access block status
            try:
                public_access_response = self.s3_client.get_public_access_block(Bucket=bucket_name)
                public_access_blocked = public_access_response["PublicAccessBlockConfiguration"]
            except ClientError:
                public_access_blocked = None

            return {
                "bucket_name": bucket_name,
                "region": region,
                "versioning_enabled": versioning_enabled,
                "public_access_blocked": public_access_blocked,
                "arn": f"arn:aws:s3:::{bucket_name}"
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                raise ValueError(f"Bucket '{bucket_name}' does not exist")
            else:
                raise ValueError(f"Failed to get bucket information: {str(e)}")

    def upload_document(
        self,
        bucket_name: str,
        file_path: str,
        object_key: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload a document to an S3 bucket.

        Args:
            bucket_name: Name of the S3 bucket
            file_path: Local file path to upload
            object_key: S3 object key (defaults to file name)
            metadata: Optional metadata to attach to the object

        Returns:
            Dictionary containing upload information

        Raises:
            ValueError: If upload fails
        """
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("bucket_name cannot be empty")

        if not file_path or len(file_path.strip()) == 0:
            raise ValueError("file_path cannot be empty")

        if not os.path.exists(file_path):
            raise ValueError(f"File '{file_path}' does not exist")

        # Use file name as object key if not provided
        if not object_key:
            object_key = os.path.basename(file_path)

        try:
            # Prepare upload parameters
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata

            # Upload the file
            self.s3_client.upload_file(
                file_path,
                bucket_name,
                object_key,
                ExtraArgs=extra_args if extra_args else None
            )

            # Get file size
            file_size = os.path.getsize(file_path)

            return {
                "bucket_name": bucket_name,
                "object_key": object_key,
                "file_path": file_path,
                "file_size": file_size,
                "status": "uploaded",
                "s3_uri": f"s3://{bucket_name}/{object_key}"
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                raise ValueError(f"Bucket '{bucket_name}' does not exist")
            elif e.response["Error"]["Code"] == "AccessDenied":
                raise ValueError(f"Access denied to bucket '{bucket_name}'")
            else:
                raise ValueError(f"Failed to upload document: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to upload document: {str(e)}")

    def upload_documents_batch(
        self,
        bucket_name: str,
        file_paths: List[str],
        prefix: str = "",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload multiple documents to an S3 bucket.

        Args:
            bucket_name: Name of the S3 bucket
            file_paths: List of local file paths to upload
            prefix: S3 prefix for all objects (e.g., "documents/")
            metadata: Optional metadata to attach to all objects

        Returns:
            Dictionary containing batch upload information

        Raises:
            ValueError: If batch upload fails
        """
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("bucket_name cannot be empty")

        if not file_paths or len(file_paths) == 0:
            raise ValueError("file_paths cannot be empty")

        successful_uploads = []
        failed_uploads = []

        for file_path in file_paths:
            try:
                # Build object key with prefix
                file_name = os.path.basename(file_path)
                object_key = f"{prefix}{file_name}" if prefix else file_name

                # Upload the file
                result = self.upload_document(
                    bucket_name=bucket_name,
                    file_path=file_path,
                    object_key=object_key,
                    metadata=metadata
                )
                successful_uploads.append(result)
            except ValueError as e:
                failed_uploads.append({
                    "file_path": file_path,
                    "error": str(e)
                })

        return {
            "bucket_name": bucket_name,
            "total_files": len(file_paths),
            "successful_uploads": len(successful_uploads),
            "failed_uploads": len(failed_uploads),
            "uploaded_files": successful_uploads,
            "failed_files": failed_uploads,
            "status": "completed"
        }

    def list_objects(
        self,
        bucket_name: str,
        prefix: str = "",
        max_keys: int = 1000
    ) -> Dict[str, Any]:
        """
        List objects in an S3 bucket.

        Args:
            bucket_name: Name of the S3 bucket
            prefix: S3 prefix to filter objects
            max_keys: Maximum number of objects to return

        Returns:
            Dictionary containing list of objects

        Raises:
            ValueError: If listing fails
        """
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("bucket_name cannot be empty")

        if max_keys <= 0:
            raise ValueError("max_keys must be greater than 0")

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            objects = []
            for obj in response.get("Contents", []):
                objects.append({
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"].isoformat(),
                    "storage_class": obj.get("StorageClass", "STANDARD")
                })

            return {
                "bucket_name": bucket_name,
                "prefix": prefix,
                "object_count": len(objects),
                "objects": objects,
                "is_truncated": response.get("IsTruncated", False)
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                raise ValueError(f"Bucket '{bucket_name}' does not exist")
            else:
                raise ValueError(f"Failed to list objects: {str(e)}")

    def delete_object(self, bucket_name: str, object_key: str) -> bool:
        """
        Delete an object from an S3 bucket.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: S3 object key to delete

        Returns:
            True if object was deleted successfully

        Raises:
            ValueError: If deletion fails
        """
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("bucket_name cannot be empty")

        if not object_key or len(object_key.strip()) == 0:
            raise ValueError("object_key cannot be empty")

        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                raise ValueError(f"Bucket '{bucket_name}' does not exist")
            else:
                raise ValueError(f"Failed to delete object: {str(e)}")

    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Delete an S3 bucket.

        Args:
            bucket_name: Name of the S3 bucket to delete
            force: If True, delete all objects in the bucket before deleting it

        Returns:
            True if bucket was deleted successfully

        Raises:
            ValueError: If deletion fails
        """
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("bucket_name cannot be empty")

        try:
            if force:
                # Delete all objects in the bucket first
                response = self.s3_client.list_objects_v2(Bucket=bucket_name)
                for obj in response.get("Contents", []):
                    self.s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])

            # Delete the bucket
            self.s3_client.delete_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                # Bucket doesn't exist, which is fine
                return True
            elif e.response["Error"]["Code"] == "BucketNotEmpty":
                raise ValueError(
                    f"Bucket '{bucket_name}' is not empty. "
                    "Use force=True to delete all objects before deleting the bucket."
                )
            else:
                raise ValueError(f"Failed to delete bucket: {str(e)}")

    def get_object(
        self,
        bucket_name: str,
        object_key: str
    ) -> Dict[str, Any]:
        """
        Get an object from an S3 bucket.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: S3 object key to retrieve

        Returns:
            Dictionary containing object data and metadata

        Raises:
            ValueError: If retrieval fails
        """
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("bucket_name cannot be empty")

        if not object_key or len(object_key.strip()) == 0:
            raise ValueError("object_key cannot be empty")

        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)

            # Read the object body
            body = response["Body"].read()

            return {
                "bucket_name": bucket_name,
                "object_key": object_key,
                "body": body,
                "content_type": response.get("ContentType"),
                "content_length": response.get("ContentLength"),
                "last_modified": response.get("LastModified").isoformat() if response.get("LastModified") else None,
                "metadata": response.get("Metadata", {})
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                raise ValueError(f"Bucket '{bucket_name}' does not exist")
            elif e.response["Error"]["Code"] == "NoSuchKey":
                raise ValueError(f"Object '{object_key}' does not exist in bucket '{bucket_name}'")
            else:
                raise ValueError(f"Failed to get object: {str(e)}")

    def download_object(
        self,
        bucket_name: str,
        object_key: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Download an object from an S3 bucket to a local file.

        Args:
            bucket_name: Name of the S3 bucket
            object_key: S3 object key to download
            file_path: Local file path to save the object

        Returns:
            Dictionary containing download information

        Raises:
            ValueError: If download fails
        """
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("bucket_name cannot be empty")

        if not object_key or len(object_key.strip()) == 0:
            raise ValueError("object_key cannot be empty")

        if not file_path or len(file_path.strip()) == 0:
            raise ValueError("file_path cannot be empty")

        try:
            self.s3_client.download_file(bucket_name, object_key, file_path)

            # Get file size
            file_size = os.path.getsize(file_path)

            return {
                "bucket_name": bucket_name,
                "object_key": object_key,
                "file_path": file_path,
                "file_size": file_size,
                "status": "downloaded"
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                raise ValueError(f"Bucket '{bucket_name}' does not exist")
            elif e.response["Error"]["Code"] == "NoSuchKey":
                raise ValueError(f"Object '{object_key}' does not exist in bucket '{bucket_name}'")
            else:
                raise ValueError(f"Failed to download object: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to download object: {str(e)}")

    def _validate_bucket_name(self, bucket_name: str) -> bool:
        """
        Validate S3 bucket name format.

        Args:
            bucket_name: Name of the bucket to validate

        Returns:
            True if bucket name is valid, False otherwise
        """
        if not bucket_name or len(bucket_name) < 3 or len(bucket_name) > 63:
            return False

        # Bucket names must be lowercase
        if bucket_name != bucket_name.lower():
            return False

        # Bucket names can only contain alphanumeric characters, hyphens, and dots
        valid_chars = set("abcdefghijklmnopqrstuvwxyz0123456789.-")
        if not all(c in valid_chars for c in bucket_name):
            return False

        # Bucket names cannot start or end with a hyphen or dot
        if bucket_name.startswith("-") or bucket_name.startswith("."):
            return False
        if bucket_name.endswith("-") or bucket_name.endswith("."):
            return False

        # Bucket names cannot contain consecutive dots or hyphens followed by dots
        if ".." in bucket_name or ".-" in bucket_name or "-." in bucket_name:
            return False

        return True
