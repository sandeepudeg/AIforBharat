import json
from datetime import datetime
from typing import Optional, Dict, Any

class ContractData:
    """Data model for contract information"""
    
    def __init__(self):
        # Party 1 Information
        self.party1_name: str = ""
        self.party1_address: str = ""
        self.party1_entity_type: str = ""
        
        # Party 2 Information
        self.party2_name: str = ""
        self.party2_address: str = ""
        self.party2_entity_type: str = ""
        
        # Purpose & Scope
        self.contract_purpose: str = ""
        self.scope_of_work: str = ""
        self.deliverables: str = ""
        
        # Key Terms
        self.start_date: str = ""
        self.end_date: str = ""
        self.payment_amount: str = ""
        self.payment_schedule: str = ""
        self.late_payment_penalty: str = ""
        self.performance_standards: str = ""
        
        # Legal Compliance
        self.legal_compliance: str = ""
        self.licenses_permits: str = ""
        
        # Risk & Liability
        self.liability_clauses: str = ""
        self.indemnity_provisions: str = ""
        self.insurance_requirements: str = ""
        
        # Confidentiality & IP
        self.confidentiality_obligations: str = ""
        self.ip_ownership: str = ""
        
        # Termination
        self.termination_conditions: str = ""
        self.notice_period: str = ""
        self.termination_consequences: str = ""
        
        # Dispute Resolution
        self.dispute_resolution_method: str = ""
        self.jurisdiction: str = ""
        self.governing_law: str = ""
        
        # Metadata
        self.created_date: str = datetime.now().isoformat()
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate contract data for required fields.
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields validation
        required_fields = {
            'party1_name': 'Party 1 Name',
            'party1_address': 'Party 1 Address',
            'party1_entity_type': 'Party 1 Entity Type',
            'party2_name': 'Party 2 Name',
            'party2_address': 'Party 2 Address',
            'party2_entity_type': 'Party 2 Entity Type',
            'contract_purpose': 'Contract Purpose',
            'scope_of_work': 'Scope of Work',
            'deliverables': 'Deliverables',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'payment_amount': 'Payment Amount',
            'payment_schedule': 'Payment Schedule',
            'dispute_resolution_method': 'Dispute Resolution Method',
            'jurisdiction': 'Jurisdiction',
            'governing_law': 'Governing Law',
        }
        
        for field, label in required_fields.items():
            value = getattr(self, field, "").strip()
            if not value:
                errors.append(f"{label} is required")
        
        # Date validation
        if self.start_date and self.end_date:
            try:
                start = datetime.fromisoformat(self.start_date)
                end = datetime.fromisoformat(self.end_date)
                if start >= end:
                    errors.append("End date must be after start date")
            except ValueError:
                errors.append("Invalid date format. Use YYYY-MM-DD")
        
        return len(errors) == 0, errors
    
    def to_json(self) -> str:
        """Serialize contract data to JSON string"""
        data = {
            'party1_name': self.party1_name,
            'party1_address': self.party1_address,
            'party1_entity_type': self.party1_entity_type,
            'party2_name': self.party2_name,
            'party2_address': self.party2_address,
            'party2_entity_type': self.party2_entity_type,
            'contract_purpose': self.contract_purpose,
            'scope_of_work': self.scope_of_work,
            'deliverables': self.deliverables,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'payment_amount': self.payment_amount,
            'payment_schedule': self.payment_schedule,
            'late_payment_penalty': self.late_payment_penalty,
            'performance_standards': self.performance_standards,
            'legal_compliance': self.legal_compliance,
            'licenses_permits': self.licenses_permits,
            'liability_clauses': self.liability_clauses,
            'indemnity_provisions': self.indemnity_provisions,
            'insurance_requirements': self.insurance_requirements,
            'confidentiality_obligations': self.confidentiality_obligations,
            'ip_ownership': self.ip_ownership,
            'termination_conditions': self.termination_conditions,
            'notice_period': self.notice_period,
            'termination_consequences': self.termination_consequences,
            'dispute_resolution_method': self.dispute_resolution_method,
            'jurisdiction': self.jurisdiction,
            'governing_law': self.governing_law,
            'created_date': self.created_date,
        }
        return json.dumps(data, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ContractData':
        """Deserialize contract data from JSON string"""
        data = json.loads(json_str)
        contract = cls()
        
        for key, value in data.items():
            if hasattr(contract, key):
                setattr(contract, key, value)
        
        return contract
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContractData':
        """Create contract from dictionary"""
        contract = cls()
        
        for key, value in data.items():
            if hasattr(contract, key):
                setattr(contract, key, value)
        
        return contract
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contract to dictionary"""
        return {
            'party1_name': self.party1_name,
            'party1_address': self.party1_address,
            'party1_entity_type': self.party1_entity_type,
            'party2_name': self.party2_name,
            'party2_address': self.party2_address,
            'party2_entity_type': self.party2_entity_type,
            'contract_purpose': self.contract_purpose,
            'scope_of_work': self.scope_of_work,
            'deliverables': self.deliverables,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'payment_amount': self.payment_amount,
            'payment_schedule': self.payment_schedule,
            'late_payment_penalty': self.late_payment_penalty,
            'performance_standards': self.performance_standards,
            'legal_compliance': self.legal_compliance,
            'licenses_permits': self.licenses_permits,
            'liability_clauses': self.liability_clauses,
            'indemnity_provisions': self.indemnity_provisions,
            'insurance_requirements': self.insurance_requirements,
            'confidentiality_obligations': self.confidentiality_obligations,
            'ip_ownership': self.ip_ownership,
            'termination_conditions': self.termination_conditions,
            'notice_period': self.notice_period,
            'termination_consequences': self.termination_consequences,
            'dispute_resolution_method': self.dispute_resolution_method,
            'jurisdiction': self.jurisdiction,
            'governing_law': self.governing_law,
            'created_date': self.created_date,
        }
