"""Tests for S3 bucket management"""

import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch, call
from botocore.exceptions import ClientError
from src.s3_manager import S3Manager


class TestS3ManagerInitialization:
    """Tests for S3 Manager initialization"""

    def test_init_with_aws_config(self, mock_s3_client):
        """Test S3 Manager initialization with AWS config"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)

                assert manager.aws_config is config
                assert manager.s3_client is mock_s3_client
                assert manager.region == 'us-east-1'


class TestBucketCreation:
    """Tests for S3 bucket creation"""

    def test_create_bucket_success_us_east_1(self, mock_s3_client):
        """Test successful bucket creation in us-east-1"""
        from config.aws_config import AWSConfig

        mock_s3_client.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "404"}}, "HeadBucket"
        )
        mock_s3_client.create_bucket.return_value = {}
        mock_s3_client.put_bucket_versioning.return_value = {}
        mock_s3_client.put_public_access_block.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.create_bucket("test-bedrock-rag-bucket")

                assert result["bucket_name"] == "test-bedrock-rag-bucket"
                assert result["status"] == "created"
                assert result["region"] == "us-east-1"
                mock_s3_client.create_bucket.assert_called_once()

    def test_create_bucket_success_other_region(self, mock_s3_client):
        """Test successful bucket creation in non-us-east-1 region"""
        from config.aws_config import AWSConfig

        mock_s3_client.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "404"}}, "HeadBucket"
        )
        mock_s3_client.create_bucket.return_value = {}
        mock_s3_client.put_bucket_versioning.return_value = {}
        mock_s3_client.put_public_access_block.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-west-2'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.create_bucket("test-bedrock-rag-bucket", region="us-west-2")

                assert result["bucket_name"] == "test-bedrock-rag-bucket"
                assert result["status"] == "created"
                assert result["region"] == "us-west-2"

    def test_create_bucket_already_exists(self, mock_s3_client):
        """Test creation when bucket already exists"""
        from config.aws_config import AWSConfig

        mock_s3_client.head_bucket.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.create_bucket("test-bedrock-rag-bucket")

                assert result["bucket_name"] == "test-bedrock-rag-bucket"
                assert result["status"] == "already_exists"

    def test_create_bucket_invalid_name(self, mock_s3_client):
        """Test bucket creation with invalid name"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)

                with pytest.raises(ValueError, match="Invalid bucket name"):
                    manager.create_bucket("INVALID-BUCKET-NAME")

    def test_create_bucket_empty_name(self, mock_s3_client):
        """Test bucket creation with empty name"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)

                with pytest.raises(ValueError, match="bucket_name cannot be empty"):
                    manager.create_bucket("")

    def test_create_bucket_with_versioning(self, mock_s3_client):
        """Test bucket creation with versioning enabled"""
        from config.aws_config import AWSConfig

        mock_s3_client.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "404"}}, "HeadBucket"
        )
        mock_s3_client.create_bucket.return_value = {}
        mock_s3_client.put_bucket_versioning.return_value = {}
        mock_s3_client.put_public_access_block.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.create_bucket(
                    "test-bedrock-rag-bucket",
                    versioning_enabled=True
                )

                assert result["versioning_enabled"] is True
                mock_s3_client.put_bucket_versioning.assert_called_once()


class TestBucketExistence:
    """Tests for checking bucket existence"""

    def test_bucket_exists_true(self, mock_s3_client):
        """Test bucket existence check returns True"""
        from config.aws_config import AWSConfig

        mock_s3_client.head_bucket.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.bucket_exists("test-bedrock-rag-bucket")

                assert result is True

    def test_bucket_exists_false(self, mock_s3_client):
        """Test bucket existence check returns False"""
        from config.aws_config import AWSConfig

        mock_s3_client.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "404"}}, "HeadBucket"
        )

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.bucket_exists("test-bedrock-rag-bucket")

                assert result is False

    def test_bucket_exists_access_denied(self, mock_s3_client):
        """Test bucket existence check with access denied"""
        from config.aws_config import AWSConfig

        mock_s3_client.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "403"}}, "HeadBucket"
        )

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)

                with pytest.raises(ValueError, match="Access denied"):
                    manager.bucket_exists("test-bedrock-rag-bucket")


class TestGetBucketInfo:
    """Tests for getting bucket information"""

    def test_get_bucket_info_success(self, mock_s3_client):
        """Test successful bucket information retrieval"""
        from config.aws_config import AWSConfig
        from datetime import datetime

        mock_s3_client.get_bucket_location.return_value = {
            "LocationConstraint": "us-west-2"
        }
        mock_s3_client.get_bucket_versioning.return_value = {
            "Status": "Enabled"
        }
        mock_s3_client.get_public_access_block.return_value = {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True
            }
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.get_bucket_info("test-bedrock-rag-bucket")

                assert result["bucket_name"] == "test-bedrock-rag-bucket"
                assert result["region"] == "us-west-2"
                assert result["versioning_enabled"] is True

    def test_get_bucket_info_not_found(self, mock_s3_client):
        """Test bucket info retrieval for non-existent bucket"""
        from config.aws_config import AWSConfig

        mock_s3_client.get_bucket_location.side_effect = ClientError(
            {"Error": {"Code": "NoSuchBucket"}}, "GetBucketLocation"
        )

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)

                with pytest.raises(ValueError, match="does not exist"):
                    manager.get_bucket_info("test-bedrock-rag-bucket")



class TestDocumentUpload:
    """Tests for document upload"""

    def test_upload_document_success(self, mock_s3_client):
        """Test successful document upload"""
        from config.aws_config import AWSConfig

        mock_s3_client.head_bucket.return_value = {}
        mock_s3_client.upload_file.return_value = None

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test document content")
            tmp_path = tmp.name

        try:
            with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = S3Manager(config)
                    result = manager.upload_document(
                        "test-bedrock-rag-bucket",
                        tmp_path
                    )

                    assert result["bucket_name"] == "test-bedrock-rag-bucket"
                    assert result["status"] == "uploaded"
                    assert result["file_size"] > 0
                    mock_s3_client.upload_file.assert_called_once()
        finally:
            os.unlink(tmp_path)

    def test_upload_document_with_custom_key(self, mock_s3_client):
        """Test document upload with custom object key"""
        from config.aws_config import AWSConfig

        mock_s3_client.head_bucket.return_value = {}
        mock_s3_client.upload_file.return_value = None

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test document content")
            tmp_path = tmp.name

        try:
            with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = S3Manager(config)
                    result = manager.upload_document(
                        "test-bedrock-rag-bucket",
                        tmp_path,
                        object_key="documents/custom-name.txt"
                    )

                    assert result["object_key"] == "documents/custom-name.txt"
                    assert result["s3_uri"] == "s3://test-bedrock-rag-bucket/documents/custom-name.txt"
        finally:
            os.unlink(tmp_path)

    def test_upload_document_file_not_found(self, mock_s3_client):
        """Test document upload with non-existent file"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)

                with pytest.raises(ValueError, match="does not exist"):
                    manager.upload_document(
                        "test-bedrock-rag-bucket",
                        "/nonexistent/file.txt"
                    )

    def test_upload_document_bucket_not_found(self, mock_s3_client):
        """Test document upload to non-existent bucket"""
        from config.aws_config import AWSConfig

        mock_s3_client.upload_file.side_effect = ClientError(
            {"Error": {"Code": "NoSuchBucket"}}, "PutObject"
        )

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test document content")
            tmp_path = tmp.name

        try:
            with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = S3Manager(config)

                    with pytest.raises(ValueError, match="does not exist"):
                        manager.upload_document(
                            "test-bedrock-rag-bucket",
                            tmp_path
                        )
        finally:
            os.unlink(tmp_path)


class TestBatchUpload:
    """Tests for batch document upload"""

    def test_upload_documents_batch_success(self, mock_s3_client):
        """Test successful batch document upload"""
        from config.aws_config import AWSConfig

        mock_s3_client.head_bucket.return_value = {}
        mock_s3_client.upload_file.return_value = None

        # Create temporary files
        tmp_files = []
        for i in range(3):
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.write(f"test document {i}".encode())
            tmp.close()
            tmp_files.append(tmp.name)

        try:
            with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = S3Manager(config)
                    result = manager.upload_documents_batch(
                        "test-bedrock-rag-bucket",
                        tmp_files,
                        prefix="documents/"
                    )

                    assert result["total_files"] == 3
                    assert result["successful_uploads"] == 3
                    assert result["failed_uploads"] == 0
                    assert result["status"] == "completed"
        finally:
            for tmp_file in tmp_files:
                os.unlink(tmp_file)

    def test_upload_documents_batch_partial_failure(self, mock_s3_client):
        """Test batch upload with partial failures"""
        from config.aws_config import AWSConfig

        mock_s3_client.head_bucket.return_value = {}
        mock_s3_client.upload_file.side_effect = [
            None,  # First upload succeeds
            ClientError({"Error": {"Code": "AccessDenied"}}, "PutObject"),  # Second fails
            None  # Third succeeds
        ]

        # Create temporary files
        tmp_files = []
        for i in range(3):
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.write(f"test document {i}".encode())
            tmp.close()
            tmp_files.append(tmp.name)

        try:
            with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    config = AWSConfig()
                    manager = S3Manager(config)
                    result = manager.upload_documents_batch(
                        "test-bedrock-rag-bucket",
                        tmp_files
                    )

                    assert result["total_files"] == 3
                    assert result["successful_uploads"] == 2
                    assert result["failed_uploads"] == 1
        finally:
            for tmp_file in tmp_files:
                os.unlink(tmp_file)


class TestListObjects:
    """Tests for listing objects in bucket"""

    def test_list_objects_success(self, mock_s3_client):
        """Test successful object listing"""
        from config.aws_config import AWSConfig
        from datetime import datetime

        mock_s3_client.list_objects_v2.return_value = {
            "Contents": [
                {
                    "Key": "documents/doc1.txt",
                    "Size": 1024,
                    "LastModified": datetime.now(),
                    "StorageClass": "STANDARD"
                },
                {
                    "Key": "documents/doc2.txt",
                    "Size": 2048,
                    "LastModified": datetime.now(),
                    "StorageClass": "STANDARD"
                }
            ],
            "IsTruncated": False
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.list_objects("test-bedrock-rag-bucket", prefix="documents/")

                assert result["bucket_name"] == "test-bedrock-rag-bucket"
                assert result["object_count"] == 2
                assert len(result["objects"]) == 2

    def test_list_objects_empty_bucket(self, mock_s3_client):
        """Test listing objects in empty bucket"""
        from config.aws_config import AWSConfig

        mock_s3_client.list_objects_v2.return_value = {
            "Contents": [],
            "IsTruncated": False
        }

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.list_objects("test-bedrock-rag-bucket")

                assert result["object_count"] == 0
                assert len(result["objects"]) == 0


class TestDeleteObject:
    """Tests for deleting objects"""

    def test_delete_object_success(self, mock_s3_client):
        """Test successful object deletion"""
        from config.aws_config import AWSConfig

        mock_s3_client.delete_object.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.delete_object(
                    "test-bedrock-rag-bucket",
                    "documents/doc1.txt"
                )

                assert result is True
                mock_s3_client.delete_object.assert_called_once()

    def test_delete_object_bucket_not_found(self, mock_s3_client):
        """Test object deletion from non-existent bucket"""
        from config.aws_config import AWSConfig

        mock_s3_client.delete_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchBucket"}}, "DeleteObject"
        )

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)

                with pytest.raises(ValueError, match="does not exist"):
                    manager.delete_object(
                        "test-bedrock-rag-bucket",
                        "documents/doc1.txt"
                    )


class TestDeleteBucket:
    """Tests for deleting buckets"""

    def test_delete_bucket_success(self, mock_s3_client):
        """Test successful bucket deletion"""
        from config.aws_config import AWSConfig

        mock_s3_client.delete_bucket.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.delete_bucket("test-bedrock-rag-bucket")

                assert result is True
                mock_s3_client.delete_bucket.assert_called_once()

    def test_delete_bucket_not_found(self, mock_s3_client):
        """Test deletion of non-existent bucket"""
        from config.aws_config import AWSConfig

        mock_s3_client.delete_bucket.side_effect = ClientError(
            {"Error": {"Code": "NoSuchBucket"}}, "DeleteBucket"
        )

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.delete_bucket("test-bedrock-rag-bucket")

                # Should return True even if bucket doesn't exist
                assert result is True

    def test_delete_bucket_not_empty_without_force(self, mock_s3_client):
        """Test deletion of non-empty bucket without force flag"""
        from config.aws_config import AWSConfig

        mock_s3_client.delete_bucket.side_effect = ClientError(
            {"Error": {"Code": "BucketNotEmpty"}}, "DeleteBucket"
        )

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)

                with pytest.raises(ValueError, match="not empty"):
                    manager.delete_bucket("test-bedrock-rag-bucket", force=False)

    def test_delete_bucket_with_force(self, mock_s3_client):
        """Test deletion of non-empty bucket with force flag"""
        from config.aws_config import AWSConfig
        from datetime import datetime

        mock_s3_client.list_objects_v2.return_value = {
            "Contents": [
                {
                    "Key": "documents/doc1.txt",
                    "Size": 1024,
                    "LastModified": datetime.now()
                }
            ]
        }
        mock_s3_client.delete_object.return_value = {}
        mock_s3_client.delete_bucket.return_value = {}

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.delete_bucket("test-bedrock-rag-bucket", force=True)

                assert result is True
                mock_s3_client.delete_object.assert_called()
                mock_s3_client.delete_bucket.assert_called_once()


class TestGetObject:
    """Tests for getting objects"""

    def test_get_object_success(self, mock_s3_client):
        """Test successful object retrieval"""
        from config.aws_config import AWSConfig
        from datetime import datetime

        mock_response = MagicMock()
        mock_response.__getitem__ = MagicMock(side_effect=lambda x: {
            "Body": MagicMock(read=lambda: b"test content"),
            "ContentType": "text/plain",
            "ContentLength": 12,
            "LastModified": datetime.now(),
            "Metadata": {"key": "value"}
        }[x])
        mock_response.get = MagicMock(side_effect=lambda x, default=None: {
            "ContentType": "text/plain",
            "ContentLength": 12,
            "LastModified": datetime.now(),
            "Metadata": {"key": "value"}
        }.get(x, default))

        mock_s3_client.get_object.return_value = mock_response

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)
                result = manager.get_object(
                    "test-bedrock-rag-bucket",
                    "documents/doc1.txt"
                )

                assert result["bucket_name"] == "test-bedrock-rag-bucket"
                assert result["object_key"] == "documents/doc1.txt"
                assert result["body"] == b"test content"


class TestDownloadObject:
    """Tests for downloading objects"""

    def test_download_object_success(self, mock_s3_client):
        """Test successful object download"""
        from config.aws_config import AWSConfig

        mock_s3_client.download_file.return_value = None

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "downloaded.txt")

            with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
                with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                    # Create a dummy file to simulate download
                    with open(output_path, 'w') as f:
                        f.write("test content")

                    config = AWSConfig()
                    manager = S3Manager(config)
                    result = manager.download_object(
                        "test-bedrock-rag-bucket",
                        "documents/doc1.txt",
                        output_path
                    )

                    assert result["bucket_name"] == "test-bedrock-rag-bucket"
                    assert result["object_key"] == "documents/doc1.txt"
                    assert result["status"] == "downloaded"
                    assert result["file_size"] > 0


class TestBucketNameValidation:
    """Tests for bucket name validation"""

    def test_validate_bucket_name_valid(self, mock_s3_client):
        """Test validation of valid bucket names"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)

                valid_names = [
                    "test-bucket",
                    "test-bucket-123",
                    "test.bucket",
                    "a" * 63,  # Max length
                ]

                for name in valid_names:
                    assert manager._validate_bucket_name(name) is True

    def test_validate_bucket_name_invalid(self, mock_s3_client):
        """Test validation of invalid bucket names"""
        from config.aws_config import AWSConfig

        with patch.object(AWSConfig, 'get_client', return_value=mock_s3_client):
            with patch.object(AWSConfig, 'get_region', return_value='us-east-1'):
                config = AWSConfig()
                manager = S3Manager(config)

                invalid_names = [
                    "UPPERCASE",  # Uppercase
                    "test_bucket",  # Underscore
                    "test-",  # Ends with hyphen
                    "-test",  # Starts with hyphen
                    "a" * 64,  # Too long
                    "ab",  # Too short
                    "test..bucket",  # Consecutive dots
                ]

                for name in invalid_names:
                    assert manager._validate_bucket_name(name) is False
