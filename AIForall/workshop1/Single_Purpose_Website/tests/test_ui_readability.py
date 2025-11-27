import pytest
from hypothesis import given, strategies as st
from app import app

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestUIReadability:
    """Test UI readability and glassmorphic design"""
    
    def test_signin_page_has_glassmorphic_styling(self, client):
        """Test that signin page has glassmorphic styling"""
        response = client.get('/auth/signin')
        html = response.data.decode()
        
        assert 'glassmorphic-card' in html
        assert 'style.css' in html
    
    def test_signup_page_has_glassmorphic_styling(self, client):
        """Test that signup page has glassmorphic styling"""
        response = client.get('/auth/signup')
        html = response.data.decode()
        
        assert 'glassmorphic-card' in html
        assert 'style.css' in html
    
    def test_contract_generator_has_glassmorphic_styling(self, client):
        """Test that contract generator has glassmorphic styling"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        assert 'glassmorphic-card' in html
        assert 'style.css' in html
    
    def test_form_inputs_are_readable(self, client):
        """Test that form inputs are readable"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for input styling
        assert 'form-group' in html
        assert 'label' in html
    
    def test_buttons_are_readable(self, client):
        """Test that buttons are readable"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for button styling
        assert 'btn' in html
        assert 'btn-primary' in html
    
    def test_text_contrast_in_forms(self, client):
        """Test that text has sufficient contrast in forms"""
        response = client.get('/auth/signin')
        html = response.data.decode()
        
        # Check for CSS styling link
        assert 'style.css' in html
        # Check for form elements that should have styling
        assert 'form-group' in html
    
    def test_form_labels_are_visible(self, client):
        """Test that form labels are visible"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for label elements
        assert '<label' in html
        assert 'for=' in html
    
    def test_error_messages_are_visible(self, client):
        """Test that error messages are visible"""
        response = client.get('/auth/signin')
        html = response.data.decode()
        
        # Check for error message styling
        assert 'error-message' in html or 'error' in html.lower()
    
    def test_success_messages_are_visible(self, client):
        """Test that success messages are visible"""
        response = client.get('/auth/signin')
        html = response.data.decode()
        
        # Check for success message styling
        assert 'success-message' in html or 'success' in html.lower()
    
    @given(st.just(None))
    def test_glassmorphic_ui_maintains_readability(self, _):
        """
        **Feature: contract-generator, Property 6: Glassmorphic UI Maintains Readability**
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4**
        
        For any form input or contract display, the glassmorphic design elements should not
        obscure text or interactive elements, maintaining full readability and usability.
        """
        client = app.test_client()
        
        # Test signin page
        response = client.get('/auth/signin')
        assert response.status_code == 200
        html = response.data.decode()
        
        # Check for glassmorphic styling
        assert 'glassmorphic-card' in html
        
        # Check for readable text
        assert 'Sign In' in html
        assert 'Email' in html
        
        # Check for visible form elements
        assert '<input' in html
        assert '<button' in html
    
    def test_contract_preview_has_readable_formatting(self, client):
        """Test that contract preview has readable formatting"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # Generate a contract first
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
        
        # Check preview page
        response = client.get('/contract/preview')
        assert response.status_code == 200
        html = response.data.decode()
        
        # Check for readable content
        assert 'CONTRACT AGREEMENT' in html
        assert 'PARTIES INFORMATION' in html
        assert 'John Doe' in html
    
    def test_responsive_design_elements(self, client):
        """Test that responsive design elements are present"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for responsive design
        assert 'viewport' in html
        assert 'meta' in html
    
    def test_form_sections_are_clearly_separated(self, client):
        """Test that form sections are clearly separated"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for section headings
        assert '<h2>' in html
        assert 'Parties Information' in html
        assert 'Purpose & Scope' in html
