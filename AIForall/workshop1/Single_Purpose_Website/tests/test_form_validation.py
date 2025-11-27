import pytest
import json
from hypothesis import given, strategies as st
from app import app

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def generate_valid_form_data():
    """Generate valid form data"""
    return {
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

class TestFormValidation:
    """Test form validation"""
    
    def test_form_submission_with_valid_data(self, client):
        """Test form submission with valid data"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        data = generate_valid_form_data()
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'message' in result
        assert 'Contract generated successfully' in result['message']
    
    def test_form_submission_missing_required_field(self, client):
        """Test form submission with missing required field"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        data = generate_valid_form_data()
        del data['party1_name']  # Remove required field
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
        assert 'Validation failed' in result['error']
    
    def test_form_submission_empty_required_field(self, client):
        """Test form submission with empty required field"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        data = generate_valid_form_data()
        data['party1_name'] = ''  # Empty required field
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_form_submission_whitespace_only_field(self, client):
        """Test form submission with whitespace-only required field"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        data = generate_valid_form_data()
        data['party1_name'] = '   '  # Whitespace only
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_form_submission_invalid_date_range(self, client):
        """Test form submission with invalid date range"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        data = generate_valid_form_data()
        data['start_date'] = '2024-12-31'
        data['end_date'] = '2024-01-01'  # End before start
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_form_submission_with_optional_fields(self, client):
        """Test form submission with optional fields filled"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        data = generate_valid_form_data()
        data['late_payment_penalty'] = '1.5% per month'
        data['performance_standards'] = 'On-time delivery'
        data['legal_compliance'] = 'Compliant with laws'
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'message' in result
    
    def test_form_submission_without_optional_fields(self, client):
        """Test form submission without optional fields"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        data = generate_valid_form_data()
        # Don't include optional fields
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'message' in result
    
    def test_form_submission_requires_authentication(self, client):
        """Test that form submission requires authentication"""
        data = generate_valid_form_data()
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        
        # Should redirect to signin
        assert response.status_code == 302
    
    def test_form_submission_with_special_characters(self, client):
        """Test form submission with special characters"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        data = generate_valid_form_data()
        data['contract_purpose'] = 'Service Agreement with "quotes" & special chars'
        data['scope_of_work'] = 'Work with @#$%^&*() characters'
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'message' in result
    
    def test_form_submission_with_unicode(self, client):
        """Test form submission with unicode characters"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        data = generate_valid_form_data()
        data['party1_name'] = 'José García'
        data['party2_name'] = '李明'
        data['contract_purpose'] = 'Contrato de servicios - 服务合同'
        
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'message' in result

class TestFormValidationProperty:
    """Property-based tests for form validation"""
    
    @given(st.just(generate_valid_form_data()))
    def test_form_validation_prevents_invalid_submissions(self, data):
        """
        **Feature: contract-generator, Property 1: Form Validation Prevents Invalid Submissions**
        **Validates: Requirements 1.4**
        
        For any form submission with missing required fields, the system should reject
        the submission and display validation error messages without generating a contract.
        """
        client = app.test_client()
        
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # Test with valid data first
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Now test with missing required field
        invalid_data = data.copy()
        del invalid_data['party1_name']
        
        response = client.post('/contract/generate',
            json=invalid_data,
            content_type='application/json'
        )
        
        # Should be rejected
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
        assert 'errors' in result
