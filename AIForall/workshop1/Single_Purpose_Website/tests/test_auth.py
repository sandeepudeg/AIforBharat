import pytest
import json
from app import app
from routes.auth_routes import verification_tokens
from datetime import datetime, timedelta

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def app_context():
    """Create app context"""
    with app.app_context():
        yield

class TestAuthSignup:
    """Test signup functionality"""
    
    def test_signup_page_loads(self, client):
        """Test that signup page loads successfully"""
        response = client.get('/auth/signup')
        assert response.status_code == 200
        assert b'Sign Up' in response.data
    
    def test_signup_with_valid_email(self, client):
        """Test signup with valid email"""
        response = client.post('/auth/signup', 
            json={'email': 'test@example.com'},
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'verification_link' in data
        assert 'message' in data
    
    def test_signup_with_invalid_email_format(self, client):
        """Test signup with invalid email format"""
        response = client.post('/auth/signup',
            json={'email': 'invalid-email'},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_signup_with_empty_email(self, client):
        """Test signup with empty email"""
        response = client.post('/auth/signup',
            json={'email': ''},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_signup_with_whitespace_email(self, client):
        """Test signup with whitespace-only email"""
        response = client.post('/auth/signup',
            json={'email': '   '},
            content_type='application/json'
        )
        assert response.status_code == 400

class TestAuthSignin:
    """Test signin functionality"""
    
    def test_signin_page_loads(self, client):
        """Test that signin page loads successfully"""
        response = client.get('/auth/signin')
        assert response.status_code == 200
        assert b'Sign In' in response.data
    
    def test_signin_with_valid_email(self, client):
        """Test signin with valid email"""
        response = client.post('/auth/signin',
            json={'email': 'user@example.com'},
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'verification_link' in data
    
    def test_signin_with_invalid_email_format(self, client):
        """Test signin with invalid email format"""
        response = client.post('/auth/signin',
            json={'email': 'not-an-email'},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_signin_with_empty_email(self, client):
        """Test signin with empty email"""
        response = client.post('/auth/signin',
            json={'email': ''},
            content_type='application/json'
        )
        assert response.status_code == 400

class TestEmailVerification:
    """Test email verification"""
    
    def test_verify_with_valid_token(self, client):
        """Test verification with valid token"""
        # Create a valid token
        token = 'test_token_12345'
        verification_tokens[token] = {
            'email': 'test@example.com',
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=1),
            'verified': False
        }
        
        response = client.get(f'/auth/verify?token={token}')
        assert response.status_code == 302  # Redirect
        
        # Token should be removed after verification
        assert token not in verification_tokens
    
    def test_verify_with_invalid_token(self, client):
        """Test verification with invalid token"""
        response = client.get('/auth/verify?token=invalid_token')
        assert response.status_code == 400
        assert b'Invalid or expired token' in response.data
    
    def test_verify_with_expired_token(self, client):
        """Test verification with expired token"""
        # Create an expired token
        token = 'expired_token_12345'
        verification_tokens[token] = {
            'email': 'test@example.com',
            'created_at': datetime.now() - timedelta(hours=2),
            'expires_at': datetime.now() - timedelta(hours=1),
            'verified': False
        }
        
        response = client.get(f'/auth/verify?token={token}')
        assert response.status_code == 400
        assert b'expired' in response.data.lower()
        
        # Expired token should be removed
        assert token not in verification_tokens
    
    def test_verify_creates_session(self, client):
        """Test that verification creates a session"""
        token = 'session_token_12345'
        verification_tokens[token] = {
            'email': 'session@example.com',
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=1),
            'verified': False
        }
        
        response = client.get(f'/auth/verify?token={token}', follow_redirects=False)
        # Should redirect to contract generator
        assert response.status_code == 302

class TestLogout:
    """Test logout functionality"""
    
    def test_logout_clears_session(self, client):
        """Test that logout clears the session"""
        # First, create a session
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # Then logout
        response = client.get('/auth/logout', follow_redirects=False)
        assert response.status_code == 302
        
        # Session should be cleared
        with client.session_transaction() as sess:
            assert 'user_email' not in sess

class TestAuthenticationProtection:
    """Test that routes are protected"""
    
    def test_unauthenticated_user_redirected_from_generator(self, client):
        """Test that unauthenticated users are redirected from generator"""
        response = client.get('/contract/generator', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/signin' in response.location
    
    def test_authenticated_user_can_access_generator(self, client):
        """Test that authenticated users can access generator"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        assert response.status_code == 200
        assert b'Contract Generator' in response.data
