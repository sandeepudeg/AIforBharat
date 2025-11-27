import pytest
from hypothesis import given, strategies as st
from app import app
from routes.auth_routes import verification_tokens
from datetime import datetime, timedelta
import json

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestCredentialStorage:
    """Test that credentials are not stored"""
    
    def test_signup_does_not_store_password(self, client):
        """Test that signup does not store password"""
        response = client.post('/auth/signup',
            json={'email': 'test@example.com'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Check that no password is stored in verification tokens
        for token, data in verification_tokens.items():
            assert 'password' not in data
            assert 'pwd' not in data
            assert 'secret' not in data
    
    def test_signin_does_not_store_password(self, client):
        """Test that signin does not store password"""
        response = client.post('/auth/signin',
            json={'email': 'test@example.com'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Check that no password is stored in verification tokens
        for token, data in verification_tokens.items():
            assert 'password' not in data
            assert 'pwd' not in data
            assert 'secret' not in data
    
    def test_verification_token_only_contains_email(self, client):
        """Test that verification token only contains email"""
        response = client.post('/auth/signup',
            json={'email': 'test@example.com'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Check verification token contents
        for token, data in verification_tokens.items():
            # Should only contain email, created_at, expires_at, verified
            allowed_keys = {'email', 'created_at', 'expires_at', 'verified'}
            assert set(data.keys()) == allowed_keys
    
    def test_session_does_not_contain_password(self, client):
        """Test that session does not contain password"""
        # Create a token and verify it
        token = 'test_token_12345'
        verification_tokens[token] = {
            'email': 'test@example.com',
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=1),
            'verified': False
        }
        
        response = client.get(f'/auth/verify?token={token}', follow_redirects=False)
        
        # Check session contents
        with client.session_transaction() as sess:
            assert 'user_email' in sess
            assert 'password' not in sess
            assert 'pwd' not in sess
            assert 'secret' not in sess
    
    def test_email_verification_uses_tokens_not_passwords(self, client):
        """Test that email verification uses tokens, not passwords"""
        response = client.post('/auth/signup',
            json={'email': 'test@example.com'},
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        
        # Should have verification_link, not password
        assert 'verification_link' in data
        assert 'password' not in data
        assert 'token' in data['verification_link']
    
    def test_no_credentials_in_response(self, client):
        """Test that no credentials are in response"""
        response = client.post('/auth/signup',
            json={'email': 'test@example.com'},
            content_type='application/json'
        )
        
        response_data = json.loads(response.data)
        response_str = json.dumps(response_data)
        
        # Should not contain password-related fields
        assert 'password' not in response_str.lower()
        assert 'pwd' not in response_str.lower()
        assert 'secret' not in response_str.lower()
    
    @given(st.just(None))
    def test_email_authentication_does_not_store_credentials(self, _):
        """
        **Feature: contract-generator, Property 9: Email Authentication Does Not Store Credentials**
        **Validates: Requirements 1.1**
        
        For any user authentication flow, the system should not store email passwords or
        credentials in any persistent storage, using only email verification tokens for
        authentication.
        """
        client = app.test_client()
        
        # Test signup
        response = client.post('/auth/signup',
            json={'email': 'test@example.com'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Verify no credentials are stored
        for token, data in verification_tokens.items():
            # Should only have email and token metadata
            assert 'email' in data
            assert 'created_at' in data
            assert 'expires_at' in data
            
            # Should NOT have any credentials
            assert 'password' not in data
            assert 'pwd' not in data
            assert 'secret' not in data
            assert 'token' not in data  # Token is the key, not in data
    
    def test_verification_token_is_random(self, client):
        """Test that verification tokens are random"""
        # Generate multiple tokens
        tokens = []
        
        for i in range(5):
            response = client.post('/auth/signup',
                json={'email': f'test{i}@example.com'},
                content_type='application/json'
            )
            
            data = json.loads(response.data)
            verification_link = data['verification_link']
            
            # Extract token from link
            token = verification_link.split('token=')[1]
            tokens.append(token)
        
        # All tokens should be different
        assert len(set(tokens)) == len(tokens)
    
    def test_token_is_not_email(self, client):
        """Test that token is not the email address"""
        response = client.post('/auth/signup',
            json={'email': 'test@example.com'},
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        verification_link = data['verification_link']
        
        # Extract token from link
        token = verification_link.split('token=')[1]
        
        # Token should not be the email
        assert token != 'test@example.com'
        assert 'test@example.com' not in token
    
    def test_token_expires(self, client):
        """Test that verification tokens expire"""
        # Create a token
        token = 'test_token_12345'
        verification_tokens[token] = {
            'email': 'test@example.com',
            'created_at': datetime.now() - timedelta(hours=2),
            'expires_at': datetime.now() - timedelta(hours=1),
            'verified': False
        }
        
        # Try to verify with expired token
        response = client.get(f'/auth/verify?token={token}')
        
        # Should fail
        assert response.status_code == 400
        assert b'expired' in response.data.lower()
