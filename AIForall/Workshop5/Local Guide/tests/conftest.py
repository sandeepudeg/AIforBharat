"""
Pytest configuration and fixtures
"""
import pytest
import os
import json
from services.data_service import DataService
from services.search_service import SearchService
from services.chat_service import ChatService
from services.category_service import CategoryService
from services.article_service import ArticleService

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create a temporary data directory for testing"""
    return tmp_path_factory.mktemp("test_data")

@pytest.fixture(scope="session")
def sample_articles():
    """Sample articles for testing"""
    return [
        {
            "id": "test_article_1",
            "title": "Test Article 1",
            "category": "food",
            "subcategory": "test",
            "description": "Test description",
            "content": "Test content",
            "tags": ["test", "food"],
            "related_articles": ["test_article_2"],
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        },
        {
            "id": "test_article_2",
            "title": "Test Article 2",
            "category": "culture",
            "subcategory": "test",
            "description": "Another test description",
            "content": "Another test content",
            "tags": ["test", "culture"],
            "related_articles": ["test_article_1"],
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }
    ]

@pytest.fixture(scope="session")
def sample_categories():
    """Sample categories for testing"""
    return [
        {
            "id": "food",
            "name": "Food & Street Culture",
            "description": "Test category",
            "icon": "fa-utensils",
            "article_count": 0
        },
        {
            "id": "culture",
            "name": "Puneri Culture & Humor",
            "description": "Test category",
            "icon": "fa-masks-theater",
            "article_count": 0
        }
    ]

@pytest.fixture(scope="function")
def data_service(test_data_dir, sample_articles, sample_categories):
    """Create a DataService instance with test data"""
    service = DataService(str(test_data_dir))
    
    # Populate with test data
    # Convert categories list to dict for internal storage
    service.categories = {cat['id']: cat.copy() for cat in sample_categories}
    service.articles = {article['id']: article.copy() for article in sample_articles}
    service._build_index()
    
    return service

@pytest.fixture(scope="function")
def search_service(data_service):
    """Create a SearchService instance"""
    return SearchService(data_service)

@pytest.fixture(scope="function")
def chat_service(data_service):
    """Create a ChatService instance"""
    return ChatService(data_service)

@pytest.fixture(scope="function")
def category_service(data_service):
    """Create a CategoryService instance"""
    return CategoryService(data_service)

@pytest.fixture(scope="function")
def article_service(data_service):
    """Create an ArticleService instance"""
    return ArticleService(data_service)
