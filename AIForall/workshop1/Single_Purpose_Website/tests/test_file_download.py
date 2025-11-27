import pytest
import json
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

class TestFileDownload:
    """Test file download functionality"""
    
    def test_pdf_download_requires_authentication(self, client):
        """Test that PDF download requires authentication"""
        response = client.get('/contract/download/pdf')
        assert response.status_code == 302  # Redirect to signin
    
    def test_docx_download_requires_authentication(self, client):
        """Test that DOCX download requires authentication"""
        response = client.get('/contract/download/docx')
        assert response.status_code == 302  # Redirect to signin
    
    def test_pdf_download_without_contract_data(self, client):
        """Test PDF download without contract data"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/download/pdf')
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_docx_download_without_contract_data(self, client):
        """Test DOCX download without contract data"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        response = client.get('/contract/download/docx')
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result
    
    def test_pdf_download_with_valid_contract(self, client):
        """Test PDF download with valid contract"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # First generate a contract
        data = generate_valid_form_data()
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Then download PDF
        response = client.get('/contract/download/pdf')
        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
        assert len(response.data) > 0
    
    def test_docx_download_with_valid_contract(self, client):
        """Test DOCX download with valid contract"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # First generate a contract
        data = generate_valid_form_data()
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Then download DOCX
        response = client.get('/contract/download/docx')
        assert response.status_code == 200
        assert 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in response.content_type
        assert len(response.data) > 0
    
    def test_pdf_download_filename(self, client):
        """Test PDF download has correct filename"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # First generate a contract
        data = generate_valid_form_data()
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Then download PDF
        response = client.get('/contract/download/pdf')
        assert response.status_code == 200
        
        # Check filename in Content-Disposition header
        assert 'Content-Disposition' in response.headers
        disposition = response.headers['Content-Disposition']
        assert 'contract_' in disposition
        assert '.pdf' in disposition
    
    def test_docx_download_filename(self, client):
        """Test DOCX download has correct filename"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # First generate a contract
        data = generate_valid_form_data()
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Then download DOCX
        response = client.get('/contract/download/docx')
        assert response.status_code == 200
        
        # Check filename in Content-Disposition header
        assert 'Content-Disposition' in response.headers
        disposition = response.headers['Content-Disposition']
        assert 'contract_' in disposition
        assert '.docx' in disposition
    
    def test_pdf_download_content_is_valid(self, client):
        """Test PDF download content is valid PDF"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # First generate a contract
        data = generate_valid_form_data()
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Then download PDF
        response = client.get('/contract/download/pdf')
        assert response.status_code == 200
        
        # Check PDF header
        assert response.data.startswith(b'%PDF')
    
    def test_docx_download_content_is_valid(self, client):
        """Test DOCX download content is valid DOCX"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # First generate a contract
        data = generate_valid_form_data()
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Then download DOCX
        response = client.get('/contract/download/docx')
        assert response.status_code == 200
        
        # Check DOCX header (ZIP file)
        assert response.data.startswith(b'PK')  # ZIP file signature
    
    def test_multiple_downloads_same_contract(self, client):
        """Test multiple downloads of the same contract"""
        with client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
        
        # First generate a contract
        data = generate_valid_form_data()
        response = client.post('/contract/generate',
            json=data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Download PDF multiple times
        response1 = client.get('/contract/download/pdf')
        response2 = client.get('/contract/download/pdf')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(response1.data) > 0
        assert len(response2.data) > 0
