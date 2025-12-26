"""
Unit tests for error page rendering
"""
import pytest
from app import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app('testing')
    with app.test_client() as client:
        yield client


class TestErrorPages:
    """Tests for error page rendering"""
    
    def test_404_page_renders(self, client):
        """Test 404 error page renders correctly"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'404' in response.data
        assert b'Page Not Found' in response.data
        assert b'Go to Homepage' in response.data
    
    def test_404_page_has_suggestions(self, client):
        """Test 404 page includes helpful suggestions"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'Browse all categories' in response.data or b'Browse Categories' in response.data
    
    def test_404_article_not_found(self, client):
        """Test 404 page when article is not found"""
        response = client.get('/articles/nonexistent_article')
        assert response.status_code == 404
        assert b'404' in response.data
    
    def test_error_page_has_home_link(self, client):
        """Test error pages have link to homepage"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'href="/"' in response.data or b'Go to Homepage' in response.data
    
    def test_error_page_responsive(self, client):
        """Test error pages are responsive"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        # Check for responsive design classes
        assert b'container' in response.data
        assert b'col-lg' in response.data or b'row' in response.data


class TestErrorHandling:
    """Tests for error handling in routes"""
    
    def test_search_with_empty_query(self, client):
        """Test search with empty query"""
        response = client.get('/search?q=')
        assert response.status_code == 200
        assert b'error' in response.data.lower() or b'query' in response.data.lower()
    
    def test_search_with_short_query(self, client):
        """Test search with query too short"""
        response = client.get('/search?q=a')
        assert response.status_code == 200
        # Should show error message
        assert b'error' in response.data.lower() or b'character' in response.data.lower()
    
    def test_api_search_with_invalid_query(self, client):
        """Test API search with invalid query"""
        response = client.get('/api/search?q=a')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_api_chat_with_empty_message(self, client):
        """Test API chat with empty message"""
        response = client.post('/api/chat', 
                              json={'message': ''},
                              content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_api_invalid_category_id(self, client):
        """Test API with invalid category ID"""
        response = client.get('/api/categories/invalid@category')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_api_invalid_article_id(self, client):
        """Test API with invalid article ID"""
        response = client.get('/api/articles/invalid@article')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data


class TestErrorMessages:
    """Tests for error message quality"""
    
    def test_404_message_is_helpful(self, client):
        """Test 404 error message is helpful"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        content = response.data.decode()
        # Should have helpful suggestions
        assert 'homepage' in content.lower() or 'categories' in content.lower()
    
    def test_error_pages_have_consistent_styling(self, client):
        """Test error pages have consistent styling"""
        response_404 = client.get('/nonexistent-page')
        
        # Should have error container styling
        assert b'error-container' in response_404.data
    
    def test_api_error_response_format(self, client):
        """Test API error responses have consistent format"""
        response = client.get('/api/search?q=a')
        assert response.status_code == 400
        data = response.get_json()
        
        # Should have required fields
        assert 'success' in data
        assert 'error' in data
        assert data['success'] is False
    
    def test_validation_error_messages(self, client):
        """Test validation error messages are descriptive"""
        response = client.get('/api/search?q=a')
        data = response.get_json()
        
        # Error message should be descriptive
        assert 'character' in data['error'].lower() or 'query' in data['error'].lower()

