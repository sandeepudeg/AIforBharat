"""Data source connector interface for Bedrock RAG Retrieval System"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DataSourceType(Enum):
    """Supported data source types"""
    S3 = "S3"
    CONFLUENCE = "CONFLUENCE"
    SHAREPOINT = "SHAREPOINT"
    SALESFORCE = "SALESFORCE"
    WEB = "WEB"


@dataclass
class Document:
    """Represents a document from a data source"""
    id: str
    content: str
    source: str
    source_type: DataSourceType
    metadata: Dict[str, Any]
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "source_type": self.source_type.value,
            "metadata": self.metadata,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "modified_date": self.modified_date.isoformat() if self.modified_date else None,
            "author": self.author,
            "tags": self.tags or []
        }


class DataSourceConnector(ABC):
    """Abstract base class for data source connectors"""

    def __init__(self, source_type: DataSourceType):
        """
        Initialize the data source connector.

        Args:
            source_type: Type of data source
        """
        self.source_type = source_type
        self._connected = False

    @abstractmethod
    def connect(self, credentials: Dict[str, Any]) -> bool:
        """
        Connect to the data source.

        Args:
            credentials: Dictionary containing connection credentials

        Returns:
            True if connection successful, False otherwise

        Raises:
            ValueError: If credentials are invalid or connection fails
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the data source.

        Returns:
            True if disconnection successful, False otherwise
        """
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the connection to the data source is active.

        Returns:
            True if connection is valid, False otherwise
        """
        pass

    @abstractmethod
    def fetch_documents(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Document]:
        """
        Fetch documents from the data source.

        Args:
            query: Optional query to filter documents
            limit: Maximum number of documents to fetch
            offset: Number of documents to skip

        Returns:
            List of Document objects

        Raises:
            ValueError: If fetch operation fails
        """
        pass

    @abstractmethod
    def fetch_document_by_id(self, document_id: str) -> Optional[Document]:
        """
        Fetch a specific document by ID.

        Args:
            document_id: ID of the document to fetch

        Returns:
            Document object if found, None otherwise

        Raises:
            ValueError: If fetch operation fails
        """
        pass

    @abstractmethod
    def get_document_count(self) -> int:
        """
        Get the total number of documents in the data source.

        Returns:
            Total number of documents

        Raises:
            ValueError: If count operation fails
        """
        pass

    def is_connected(self) -> bool:
        """
        Check if the connector is currently connected.

        Returns:
            True if connected, False otherwise
        """
        return self._connected


class S3DataSourceConnector(DataSourceConnector):
    """Connector for S3 data sources"""

    def __init__(self, s3_manager):
        """
        Initialize S3 data source connector.

        Args:
            s3_manager: S3Manager instance for S3 operations
        """
        super().__init__(DataSourceType.S3)
        self.s3_manager = s3_manager
        self.bucket_name: Optional[str] = None
        self.prefix: str = ""

    def connect(self, credentials: Dict[str, Any]) -> bool:
        """
        Connect to S3 bucket.

        Args:
            credentials: Dictionary with 'bucket_name' and optional 'prefix'

        Returns:
            True if connection successful

        Raises:
            ValueError: If credentials are invalid or bucket doesn't exist
        """
        if not credentials or "bucket_name" not in credentials:
            raise ValueError("credentials must contain 'bucket_name'")

        bucket_name = credentials.get("bucket_name")
        if not bucket_name or len(bucket_name.strip()) == 0:
            raise ValueError("bucket_name cannot be empty")

        # Validate bucket exists
        if not self.s3_manager.bucket_exists(bucket_name):
            raise ValueError(f"S3 bucket '{bucket_name}' does not exist or is not accessible")

        self.bucket_name = bucket_name
        self.prefix = credentials.get("prefix", "")
        self._connected = True

        return True

    def disconnect(self) -> bool:
        """
        Disconnect from S3 bucket.

        Returns:
            True if disconnection successful
        """
        self.bucket_name = None
        self.prefix = ""
        self._connected = False
        return True

    def validate_connection(self) -> bool:
        """
        Validate S3 connection.

        Returns:
            True if connection is valid
        """
        if not self._connected or not self.bucket_name:
            return False

        try:
            return self.s3_manager.bucket_exists(self.bucket_name)
        except Exception:
            return False

    def fetch_documents(
        self,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Document]:
        """
        Fetch documents from S3 bucket.

        Args:
            query: Optional prefix filter for object keys
            limit: Maximum number of documents to fetch
            offset: Number of documents to skip

        Returns:
            List of Document objects

        Raises:
            ValueError: If fetch operation fails
        """
        if not self._connected or not self.bucket_name:
            raise ValueError("Not connected to S3 bucket")

        try:
            # Build prefix for filtering
            prefix = self.prefix
            if query:
                prefix = f"{self.prefix}{query}" if self.prefix else query

            # List objects with prefix
            max_keys = limit + offset if limit else 1000
            result = self.s3_manager.list_objects(
                self.bucket_name,
                prefix=prefix,
                max_keys=max_keys
            )

            documents = []
            for i, obj in enumerate(result.get("objects", [])):
                # Skip offset documents
                if i < offset:
                    continue

                # Stop if limit reached
                if limit and len(documents) >= limit:
                    break

                # Fetch object content
                try:
                    obj_result = self.s3_manager.get_object(
                        self.bucket_name,
                        obj["key"]
                    )

                    # Create document from S3 object
                    doc = Document(
                        id=obj["key"],
                        content=obj_result["body"].decode("utf-8", errors="ignore"),
                        source=f"s3://{self.bucket_name}/{obj['key']}",
                        source_type=DataSourceType.S3,
                        metadata={
                            "s3_key": obj["key"],
                            "size": obj["size"],
                            "storage_class": obj.get("storage_class", "STANDARD")
                        },
                        modified_date=datetime.fromisoformat(obj["last_modified"]) if obj.get("last_modified") else None
                    )
                    documents.append(doc)
                except Exception as e:
                    # Log error but continue processing other documents
                    continue

            return documents
        except Exception as e:
            raise ValueError(f"Failed to fetch documents from S3: {str(e)}")

    def fetch_document_by_id(self, document_id: str) -> Optional[Document]:
        """
        Fetch a specific document from S3 by key.

        Args:
            document_id: S3 object key

        Returns:
            Document object if found, None otherwise

        Raises:
            ValueError: If fetch operation fails
        """
        if not self._connected or not self.bucket_name:
            raise ValueError("Not connected to S3 bucket")

        if not document_id or len(document_id.strip()) == 0:
            raise ValueError("document_id cannot be empty")

        try:
            obj_result = self.s3_manager.get_object(self.bucket_name, document_id)

            doc = Document(
                id=document_id,
                content=obj_result["body"].decode("utf-8", errors="ignore"),
                source=f"s3://{self.bucket_name}/{document_id}",
                source_type=DataSourceType.S3,
                metadata={
                    "s3_key": document_id,
                    "content_type": obj_result.get("content_type"),
                    "content_length": obj_result.get("content_length")
                },
                modified_date=datetime.fromisoformat(obj_result["last_modified"]) if obj_result.get("last_modified") else None
            )
            return doc
        except ValueError as e:
            if "does not exist" in str(e):
                return None
            raise
        except Exception as e:
            raise ValueError(f"Failed to fetch document from S3: {str(e)}")

    def get_document_count(self) -> int:
        """
        Get the total number of documents in S3 bucket.

        Returns:
            Total number of documents

        Raises:
            ValueError: If count operation fails
        """
        if not self._connected or not self.bucket_name:
            raise ValueError("Not connected to S3 bucket")

        try:
            result = self.s3_manager.list_objects(
                self.bucket_name,
                prefix=self.prefix,
                max_keys=1000
            )
            return result.get("object_count", 0)
        except Exception as e:
            raise ValueError(f"Failed to get document count from S3: {str(e)}")
