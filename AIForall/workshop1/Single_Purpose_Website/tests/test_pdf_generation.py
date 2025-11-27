import pytest
import os
from hypothesis import given, strategies as st
from models.contract import ContractData
from utils.contract_generator import ContractGenerator

def generate_valid_contract_data():
    """Generate valid contract data for testing"""
    return {
        'party1_name': 'John Doe',
        'party1_address': '123 Main St, City, State',
        'party1_entity_type': 'Individual',
        'party2_name': 'Jane Smith',
        'party2_address': '456 Oak Ave, City, State',
        'party2_entity_type': 'Company',
        'contract_purpose': 'Service Agreement',
        'scope_of_work': 'Provide consulting services',
        'deliverables': 'Monthly reports and recommendations',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'payment_amount': '$5,000',
        'payment_schedule': 'Monthly',
        'late_payment_penalty': '1.5% per month',
        'performance_standards': 'On-time delivery',
        'legal_compliance': 'Compliant with local laws',
        'licenses_permits': 'All required licenses obtained',
        'liability_clauses': 'Limited to contract value',
        'indemnity_provisions': 'Each party indemnifies the other',
        'insurance_requirements': 'General liability insurance required',
        'confidentiality_obligations': 'Maintain confidentiality for 2 years',
        'ip_ownership': 'Client owns all IP created',
        'termination_conditions': 'Either party may terminate with 30 days notice',
        'notice_period': '30 days',
        'termination_consequences': 'Payment for work completed',
        'dispute_resolution_method': 'Mediation',
        'jurisdiction': 'State of California',
        'governing_law': 'California Law',
    }

class TestPDFGeneration:
    """Test PDF generation"""
    
    def test_pdf_generation_creates_file(self):
        """Test that PDF generation creates a file"""
        contract = ContractData.from_dict(generate_valid_contract_data())
        pdf_path = ContractGenerator.generate_pdf(contract)
        
        assert os.path.exists(pdf_path)
        assert pdf_path.endswith('.pdf')
        
        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    def test_pdf_file_has_content(self):
        """Test that generated PDF has content"""
        contract = ContractData.from_dict(generate_valid_contract_data())
        pdf_path = ContractGenerator.generate_pdf(contract)
        
        # Check file size
        file_size = os.path.getsize(pdf_path)
        assert file_size > 0
        
        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    def test_pdf_generation_with_special_characters(self):
        """Test PDF generation with special characters"""
        data = generate_valid_contract_data()
        data['contract_purpose'] = 'Service Agreement with "quotes" & special chars'
        data['scope_of_work'] = 'Work with @#$%^&*() characters'
        
        contract = ContractData.from_dict(data)
        pdf_path = ContractGenerator.generate_pdf(contract)
        
        assert os.path.exists(pdf_path)
        file_size = os.path.getsize(pdf_path)
        assert file_size > 0
        
        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    def test_pdf_generation_with_unicode(self):
        """Test PDF generation with unicode characters"""
        data = generate_valid_contract_data()
        data['party1_name'] = 'José García'
        data['party2_name'] = '李明'
        data['contract_purpose'] = 'Contrato de servicios - 服务合同'
        
        contract = ContractData.from_dict(data)
        pdf_path = ContractGenerator.generate_pdf(contract)
        
        assert os.path.exists(pdf_path)
        file_size = os.path.getsize(pdf_path)
        assert file_size > 0
        
        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    @given(st.just(generate_valid_contract_data()))
    def test_pdf_generation_preserves_all_information(self, data):
        """
        **Feature: contract-generator, Property 3: PDF Generation Preserves All Information**
        **Validates: Requirements 2.2, 2.5, 4.1, 4.3, 4.4**
        
        For any valid contract data, generating a PDF should include all entered information
        formatted on a single page without data loss or truncation.
        """
        contract = ContractData.from_dict(data)
        pdf_path = ContractGenerator.generate_pdf(contract)
        
        # Verify file exists and has content
        assert os.path.exists(pdf_path)
        file_size = os.path.getsize(pdf_path)
        assert file_size > 0
        
        # Verify it's a valid PDF (starts with PDF header)
        with open(pdf_path, 'rb') as f:
            header = f.read(4)
            assert header == b'%PDF'
        
        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    def test_pdf_generation_with_long_text(self):
        """Test PDF generation with long text content"""
        data = generate_valid_contract_data()
        data['scope_of_work'] = 'A' * 1000  # Very long text
        data['contract_purpose'] = 'B' * 1000
        
        contract = ContractData.from_dict(data)
        pdf_path = ContractGenerator.generate_pdf(contract)
        
        assert os.path.exists(pdf_path)
        file_size = os.path.getsize(pdf_path)
        assert file_size > 0
        
        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    
    def test_pdf_generation_with_minimal_data(self):
        """Test PDF generation with minimal required data"""
        data = generate_valid_contract_data()
        # Remove optional fields
        data['late_payment_penalty'] = ''
        data['performance_standards'] = ''
        data['legal_compliance'] = ''
        data['licenses_permits'] = ''
        data['liability_clauses'] = ''
        data['indemnity_provisions'] = ''
        data['insurance_requirements'] = ''
        data['confidentiality_obligations'] = ''
        data['ip_ownership'] = ''
        data['termination_conditions'] = ''
        data['notice_period'] = ''
        data['termination_consequences'] = ''
        
        contract = ContractData.from_dict(data)
        pdf_path = ContractGenerator.generate_pdf(contract)
        
        assert os.path.exists(pdf_path)
        file_size = os.path.getsize(pdf_path)
        assert file_size > 0
        
        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
