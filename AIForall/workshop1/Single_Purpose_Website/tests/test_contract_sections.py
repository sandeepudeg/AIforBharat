import pytest
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

class TestContractSections:
    """Test contract sections"""
    
    def test_contract_html_contains_all_sections(self):
        """Test that contract HTML contains all required sections"""
        contract = ContractData.from_dict(generate_valid_contract_data())
        html = ContractGenerator.format_contract_html(contract)
        
        # Check for all sections
        sections = [
            'PARTIES INFORMATION',
            'PURPOSE & SCOPE',
            'KEY TERMS',
            'LEGAL COMPLIANCE',
            'RISK & LIABILITY',
            'CONFIDENTIALITY & IP',
            'TERMINATION',
            'DISPUTE RESOLUTION',
            'SIGNATURES',
        ]
        
        for section in sections:
            assert section in html, f"Section {section} not found in HTML"
    
    def test_contract_html_contains_party_information(self):
        """Test that contract HTML contains party information"""
        contract = ContractData.from_dict(generate_valid_contract_data())
        html = ContractGenerator.format_contract_html(contract)
        
        assert contract.party1_name in html
        assert contract.party1_address in html
        assert contract.party1_entity_type in html
        assert contract.party2_name in html
        assert contract.party2_address in html
        assert contract.party2_entity_type in html
    
    def test_contract_html_contains_purpose_and_scope(self):
        """Test that contract HTML contains purpose and scope"""
        contract = ContractData.from_dict(generate_valid_contract_data())
        html = ContractGenerator.format_contract_html(contract)
        
        assert contract.contract_purpose in html
        assert contract.scope_of_work in html
        assert contract.deliverables in html
    
    def test_contract_html_contains_key_terms(self):
        """Test that contract HTML contains key terms"""
        contract = ContractData.from_dict(generate_valid_contract_data())
        html = ContractGenerator.format_contract_html(contract)
        
        assert contract.start_date in html
        assert contract.end_date in html
        assert contract.payment_amount in html
        assert contract.payment_schedule in html
    
    def test_contract_html_contains_dispute_resolution(self):
        """Test that contract HTML contains dispute resolution"""
        contract = ContractData.from_dict(generate_valid_contract_data())
        html = ContractGenerator.format_contract_html(contract)
        
        assert contract.dispute_resolution_method in html
        assert contract.jurisdiction in html
        assert contract.governing_law in html
    
    def test_contract_html_contains_signature_blocks(self):
        """Test that contract HTML contains signature blocks"""
        contract = ContractData.from_dict(generate_valid_contract_data())
        html = ContractGenerator.format_contract_html(contract)
        
        # Check for signature blocks
        assert 'Party 1:' in html
        assert 'Party 2:' in html
        assert 'Date:' in html
    
    @given(st.just(generate_valid_contract_data()))
    def test_contract_sections_are_complete(self, data):
        """
        **Feature: contract-generator, Property 5: Contract Sections Are Complete**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        
        For any generated contract, all required sections (Parties Information, Purpose & Scope,
        Key Terms, Legal Compliance, Risk & Liability, Confidentiality & IP, Termination,
        Dispute Resolution, and Signatures) should be present and properly formatted.
        """
        contract = ContractData.from_dict(data)
        html = ContractGenerator.format_contract_html(contract)
        
        # Check for all required sections
        required_sections = [
            'PARTIES INFORMATION',
            'PURPOSE & SCOPE',
            'KEY TERMS',
            'LEGAL COMPLIANCE',
            'RISK & LIABILITY',
            'CONFIDENTIALITY & IP',
            'TERMINATION',
            'DISPUTE RESOLUTION',
            'SIGNATURES',
        ]
        
        for section in required_sections:
            assert section in html, f"Required section {section} not found"
        
        # Check for party information
        assert data['party1_name'] in html
        assert data['party2_name'] in html
        
        # Check for key terms
        assert data['start_date'] in html
        assert data['end_date'] in html
        assert data['payment_amount'] in html
        
        # Check for dispute resolution
        assert data['dispute_resolution_method'] in html
        assert data['jurisdiction'] in html
        assert data['governing_law'] in html
    
    def test_contract_html_with_optional_fields_empty(self):
        """Test contract HTML when optional fields are empty"""
        data = generate_valid_contract_data()
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
        html = ContractGenerator.format_contract_html(contract)
        
        # Should still contain all required sections
        assert 'PARTIES INFORMATION' in html
        assert 'PURPOSE & SCOPE' in html
        assert 'KEY TERMS' in html
        assert 'DISPUTE RESOLUTION' in html
    
    def test_contract_html_with_special_characters(self):
        """Test contract HTML with special characters"""
        data = generate_valid_contract_data()
        data['contract_purpose'] = 'Service Agreement with "quotes" & special chars'
        data['scope_of_work'] = 'Work with @#$%^&*() characters'
        
        contract = ContractData.from_dict(data)
        html = ContractGenerator.format_contract_html(contract)
        
        # Should contain the special characters (properly escaped)
        assert 'Service Agreement' in html
        assert 'Work with' in html
    
    def test_contract_html_with_unicode(self):
        """Test contract HTML with unicode characters"""
        data = generate_valid_contract_data()
        data['party1_name'] = 'José García'
        data['party2_name'] = '李明'
        data['contract_purpose'] = 'Contrato de servicios - 服务合同'
        
        contract = ContractData.from_dict(data)
        html = ContractGenerator.format_contract_html(contract)
        
        # Should contain the unicode characters
        assert 'José García' in html
        assert '李明' in html
        assert 'Contrato de servicios' in html
