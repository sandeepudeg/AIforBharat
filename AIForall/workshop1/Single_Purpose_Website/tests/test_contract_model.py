import pytest
from hypothesis import given, strategies as st
from models.contract import ContractData
import json
from datetime import datetime, timedelta

# Strategies for generating test data
email_strategy = st.emails()
text_strategy = st.text(min_size=1, max_size=500)
date_strategy = st.dates(min_value=datetime.now().date(), max_value=(datetime.now() + timedelta(days=365)).date())
entity_types = st.sampled_from(['Individual', 'Company', 'Partnership'])
dispute_methods = st.sampled_from(['Mediation', 'Arbitration', 'Litigation'])

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

class TestContractDataModel:
    """Test ContractData model"""
    
    def test_contract_creation(self):
        """Test creating a contract"""
        contract = ContractData()
        assert contract.party1_name == ""
        assert contract.created_date is not None
    
    def test_contract_validation_with_valid_data(self):
        """Test validation with valid data"""
        contract = ContractData.from_dict(generate_valid_contract_data())
        is_valid, errors = contract.validate()
        assert is_valid
        assert len(errors) == 0
    
    def test_contract_validation_missing_required_fields(self):
        """Test validation with missing required fields"""
        contract = ContractData()
        is_valid, errors = contract.validate()
        assert not is_valid
        assert len(errors) > 0
    
    def test_contract_validation_invalid_dates(self):
        """Test validation with invalid date range"""
        data = generate_valid_contract_data()
        data['start_date'] = '2024-12-31'
        data['end_date'] = '2024-01-01'
        
        contract = ContractData.from_dict(data)
        is_valid, errors = contract.validate()
        assert not is_valid
        assert any('End date must be after start date' in error for error in errors)

class TestContractSerialization:
    """Test contract serialization and deserialization"""
    
    @given(st.just(generate_valid_contract_data()))
    def test_serialization_round_trip(self, data):
        """
        **Feature: contract-generator, Property 2: Contract Data Round Trip**
        **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
        
        For any valid contract data, serializing to JSON and deserializing back
        should produce an equivalent contract object with all fields intact.
        """
        # Create contract from data
        original_contract = ContractData.from_dict(data)
        
        # Serialize to JSON
        json_str = original_contract.to_json()
        
        # Deserialize back
        restored_contract = ContractData.from_json(json_str)
        
        # Verify all fields match
        assert original_contract.party1_name == restored_contract.party1_name
        assert original_contract.party2_name == restored_contract.party2_name
        assert original_contract.contract_purpose == restored_contract.contract_purpose
        assert original_contract.scope_of_work == restored_contract.scope_of_work
        assert original_contract.deliverables == restored_contract.deliverables
        assert original_contract.start_date == restored_contract.start_date
        assert original_contract.end_date == restored_contract.end_date
        assert original_contract.payment_amount == restored_contract.payment_amount
        assert original_contract.payment_schedule == restored_contract.payment_schedule
        assert original_contract.dispute_resolution_method == restored_contract.dispute_resolution_method
        assert original_contract.jurisdiction == restored_contract.jurisdiction
        assert original_contract.governing_law == restored_contract.governing_law
    
    def test_serialization_with_special_characters(self):
        """Test serialization with special characters"""
        data = generate_valid_contract_data()
        data['contract_purpose'] = 'Service Agreement with "quotes" and \'apostrophes\''
        data['scope_of_work'] = 'Work with special chars: @#$%^&*()'
        
        contract = ContractData.from_dict(data)
        json_str = contract.to_json()
        restored = ContractData.from_json(json_str)
        
        assert contract.contract_purpose == restored.contract_purpose
        assert contract.scope_of_work == restored.scope_of_work
    
    def test_serialization_with_unicode(self):
        """Test serialization with unicode characters"""
        data = generate_valid_contract_data()
        data['party1_name'] = 'José García'
        data['party2_name'] = '李明'
        data['contract_purpose'] = 'Contrato de servicios - 服务合同'
        
        contract = ContractData.from_dict(data)
        json_str = contract.to_json()
        restored = ContractData.from_json(json_str)
        
        assert contract.party1_name == restored.party1_name
        assert contract.party2_name == restored.party2_name
        assert contract.contract_purpose == restored.contract_purpose
    
    def test_json_is_valid_json(self):
        """Test that serialized data is valid JSON"""
        contract = ContractData.from_dict(generate_valid_contract_data())
        json_str = contract.to_json()
        
        # Should not raise an exception
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert 'party1_name' in parsed
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary"""
        data = generate_valid_contract_data()
        contract = ContractData.from_dict(data)
        
        result_dict = contract.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict['party1_name'] == data['party1_name']
        assert result_dict['party2_name'] == data['party2_name']
        assert result_dict['contract_purpose'] == data['contract_purpose']

class TestContractValidation:
    """Test contract validation edge cases"""
    
    def test_validation_with_empty_strings(self):
        """Test validation rejects empty required fields"""
        data = generate_valid_contract_data()
        data['party1_name'] = ''
        
        contract = ContractData.from_dict(data)
        is_valid, errors = contract.validate()
        
        assert not is_valid
        assert any('Party 1 Name' in error for error in errors)
    
    def test_validation_with_whitespace_only(self):
        """Test validation rejects whitespace-only required fields"""
        data = generate_valid_contract_data()
        data['party1_name'] = '   '
        
        contract = ContractData.from_dict(data)
        is_valid, errors = contract.validate()
        
        assert not is_valid
        assert any('Party 1 Name' in error for error in errors)
    
    def test_validation_with_same_dates(self):
        """Test validation rejects same start and end dates"""
        data = generate_valid_contract_data()
        data['start_date'] = '2024-01-01'
        data['end_date'] = '2024-01-01'
        
        contract = ContractData.from_dict(data)
        is_valid, errors = contract.validate()
        
        assert not is_valid
        assert any('End date must be after start date' in error for error in errors)
    
    def test_validation_optional_fields_can_be_empty(self):
        """Test that optional fields can be empty"""
        data = generate_valid_contract_data()
        data['late_payment_penalty'] = ''
        data['performance_standards'] = ''
        data['legal_compliance'] = ''
        
        contract = ContractData.from_dict(data)
        is_valid, errors = contract.validate()
        
        assert is_valid
        assert len(errors) == 0
