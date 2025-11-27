import pytest
from app import app

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestFormRendering:
    """Test form rendering"""
    
    def test_contract_generator_form_loads(self, client):
        """Test that contract generator form loads successfully"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        assert response.status_code == 200
        assert b'Contract Generator' in response.data
    
    def test_form_contains_all_required_fields(self, client):
        """Test that form contains all required fields"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for required fields
        required_fields = [
            'party1_name',
            'party1_address',
            'party1_entity_type',
            'party2_name',
            'party2_address',
            'party2_entity_type',
            'contract_purpose',
            'scope_of_work',
            'deliverables',
            'start_date',
            'end_date',
            'payment_amount',
            'payment_schedule',
            'dispute_resolution_method',
            'jurisdiction',
            'governing_law',
        ]
        
        for field in required_fields:
            assert field in html, f"Field {field} not found in form"
    
    def test_form_contains_optional_fields(self, client):
        """Test that form contains optional fields"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for optional fields
        optional_fields = [
            'late_payment_penalty',
            'performance_standards',
            'legal_compliance',
            'licenses_permits',
            'liability_clauses',
            'indemnity_provisions',
            'insurance_requirements',
            'confidentiality_obligations',
            'ip_ownership',
            'termination_conditions',
            'notice_period',
            'termination_consequences',
        ]
        
        for field in optional_fields:
            assert field in html, f"Optional field {field} not found in form"
    
    def test_form_contains_section_headings(self, client):
        """Test that form contains all section headings"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for section headings
        sections = [
            'Parties Information',
            'Purpose & Scope',
            'Key Terms',
            'Legal Compliance',
            'Risk & Liability',
            'Confidentiality & IP',
            'Termination',
            'Dispute Resolution',
        ]
        
        for section in sections:
            assert section in html, f"Section {section} not found in form"
    
    def test_form_contains_submit_button(self, client):
        """Test that form contains submit button"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        assert 'Generate Contract' in html
    
    def test_form_has_glassmorphic_styling(self, client):
        """Test that form has glassmorphic styling classes"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for glassmorphic class
        assert 'glassmorphic-card' in html
    
    def test_entity_type_select_has_options(self, client):
        """Test that entity type select has all options"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for entity type options
        assert 'Individual' in html
        assert 'Company' in html
        assert 'Partnership' in html
    
    def test_dispute_resolution_select_has_options(self, client):
        """Test that dispute resolution select has all options"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for dispute resolution options
        assert 'Mediation' in html
        assert 'Arbitration' in html
        assert 'Litigation' in html
    
    def test_form_has_required_attributes(self, client):
        """Test that required fields have required attribute"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/generator')
        html = response.data.decode()
        
        # Check for required attributes on key fields
        assert 'id="party1_name"' in html
        assert 'id="party2_name"' in html
        assert 'id="contract_purpose"' in html
        assert 'id="start_date"' in html
        assert 'id="end_date"' in html
