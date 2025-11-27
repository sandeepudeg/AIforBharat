import pytest
from hypothesis import given, strategies as st
from app import app

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestAuthenticationProtection:
    """Test authentication protection"""
    
    def test_unauthenticated_user_cannot_access_generator(self, client):
        """Test that unauthenticated users cannot access generator"""
        response = client.get('/contract/generator', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/signin' in response.location
    
    def test_unauthenticated_user_cannot_generate_contract(self, client):
        """Test that unauthenticated users cannot generate contract"""
        data = {
            'party1_name': 'John Doe',
            'party1_address': '123 Main St',
            'party1_entity_type': 'Individual',
            'party2_name': 'Jane Smith',
            'party2_address': '456 Oak Ave',
            'party2_entity_type': 'Company',
            'contract_purpose': 'Service Agreement',
            'scope_of_work': 'Consulting',
            'deliverables': 'Reports',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'payment_amount': '$5,000',
            'payment_schedule': 'Monthly',
            'dispute_resolution_method': 'Mediation',
            'jurisdiction': 'California',
            'governing_law': 'California Law',
        }
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 302
    
    def test_unauthenticated_user_cannot_download_pdf(self, client):
        """Test that unauthenticated users cannot download PDF"""
        response = client.get('/contract/download/pdf', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/signin' in response.location
    
    def test_unauthenticated_user_cannot_download_docx(self, client):
        """Test that unauthenticated users cannot download DOCX"""
        response = client.get('/contract/download/docx', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/signin' in response.location
    
    def test_unauthenticated_user_cannot_view_preview(self, client):
        """Test that unauthenticated users cannot view preview"""
        response = client.get('/contract/preview', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/signin' in response.location
    
    def test_authenticated_user_can_access_generator(self, client):
        """Test that authenticated users can access generator"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        assert response.status_code == 200
        assert b'Contract Generator' in response.data
    
    def test_authenticated_user_can_generate_contract(self, client):
        """Test that authenticated users can generate contract"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        data = {
            'party1_name': 'John Doe',
            'party1_address': '123 Main St',
            'party1_entity_type': 'Individual',
            'party2_name': 'Jane Smith',
            'party2_address': '456 Oak Ave',
            'party2_entity_type': 'Company',
            'contract_purpose': 'Service Agreement',
            'scope_of_work': 'Consulting',
            'deliverables': 'Reports',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'payment_amount': '$5,000',
            'payment_schedule': 'Monthly',
            'dispute_resolution_method': 'Mediation',
            'jurisdiction': 'California',
            'governing_law': 'California Law',
        }
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
    
    def test_authenticated_user_can_download_pdf(self, client):
        """Test that authenticated users can download PDF"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # First generate a contract
        data = {
            'party1_name': 'John Doe',
            'party1_address': '123 Main St',
            'party1_entity_type': 'Individual',
            'party2_name': 'Jane Smith',
            'party2_address': '456 Oak Ave',
            'party2_entity_type': 'Company',
            'contract_purpose': 'Service Agreement',
            'scope_of_work': 'Consulting',
            'deliverables': 'Reports',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'payment_amount': '$5,000',
            'payment_schedule': 'Monthly',
            'dispute_resolution_method': 'Mediation',
            'jurisdiction': 'California',
            'governing_law': 'California Law',
        }
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Then download PDF
        response = client.get('/contract/download/pdf')
        assert response.status_code == 200
    
    def test_authenticated_user_can_download_docx(self, client):
        """Test that authenticated users can download DOCX"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # First generate a contract
        data = {
            'party1_name': 'John Doe',
            'party1_address': '123 Main St',
            'party1_entity_type': 'Individual',
            'party2_name': 'Jane Smith',
            'party2_address': '456 Oak Ave',
            'party2_entity_type': 'Company',
            'contract_purpose': 'Service Agreement',
            'scope_of_work': 'Consulting',
            'deliverables': 'Reports',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'payment_amount': '$5,000',
            'payment_schedule': 'Monthly',
            'dispute_resolution_method': 'Mediation',
            'jurisdiction': 'California',
            'governing_law': 'California Law',
        }
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Then download DOCX
        response = client.get('/contract/download/docx')
        assert response.status_code == 200
    
    @given(st.just(None))
    def test_unauthenticated_users_cannot_access_contract_generation(self, _):
        """
        **Feature: contract-generator, Property 8: Unauthenticated Users Cannot Access Contract Generation**
        **Validates: Requirements 1.1**
        
        For any unauthenticated user attempting to access the contract generator, the system
        should redirect them to the signin/signup page without allowing access to contract
        generation functionality.
        """
        client = app.test_client()
        
        # Try to access generator without authentication
        response = client.get('/contract/generator', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/signin' in response.location
        
        # Try to generate contract without authentication
        data = {
            'party1_name': 'John Doe',
            'party1_address': '123 Main St',
            'party1_entity_type': 'Individual',
            'party2_name': 'Jane Smith',
            'party2_address': '456 Oak Ave',
            'party2_entity_type': 'Company',
            'contract_purpose': 'Service Agreement',
            'scope_of_work': 'Consulting',
            'deliverables': 'Reports',
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'payment_amount': '$5,000',
            'payment_schedule': 'Monthly',
            'dispute_resolution_method': 'Mediation',
            'jurisdiction': 'California',
            'governing_law': 'California Law',
        }
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 302
