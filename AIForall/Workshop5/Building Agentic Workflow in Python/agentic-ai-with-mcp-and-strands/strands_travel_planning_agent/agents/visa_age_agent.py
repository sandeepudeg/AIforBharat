#!/usr/bin/env python3
"""
Visa and Age Agent using Strands Framework

This agent handles visa requirements, age restrictions, and travel eligibility.
"""

import logging
from strands import Agent
from strands.models import BedrockModel
from strands.session.s3_session_manager import S3SessionManager

logger = logging.getLogger(__name__)


class VisaAgeAgent(Agent):
    """Visa and age specialist agent using Strands framework."""
    
    def __init__(self, session_manager: S3SessionManager = None):
        """Initialize Visa and Age Agent with Bedrock model and tools."""
        
        model = BedrockModel(
            model_id="us.amazon.nova-pro-v1:0",
            temperature=0.3
        )
        
        system_prompt = """You are a travel documentation and eligibility expert. Your responsibilities:
1. Check visa requirements for destinations
2. Verify age restrictions for activities
3. Filter activities based on age
4. Provide visa application guidance
5. Offer travel eligibility advice

When users ask about visas or age restrictions, use the available tools to check
requirements, verify eligibility, and provide guidance."""
        
        super().__init__(
            model=model,
            system_prompt=system_prompt,
            session_manager=session_manager,
            tools=[
                self.check_visa_requirement,
                self.check_age_restriction,
                self.filter_activities_by_age,
                self.get_visa_application_info
            ]
        )
    
    def check_visa_requirement(self, origin_country: str, 
                              destination_country: str) -> dict:
        """
        Check visa requirements for travel.
        
        Args:
            origin_country: Country of citizenship
            destination_country: Destination country
            
        Returns:
            Visa requirement information
        """
        logger.info(f"Checking visa requirement from {origin_country} to {destination_country}")
        
        # Mock visa requirements
        visa_requirements = {
            ("USA", "France"): {"required": False, "visa_free_days": 90, "type": "Schengen"},
            ("USA", "Japan"): {"required": False, "visa_free_days": 90, "type": "Tourist"},
            ("USA", "India"): {"required": True, "processing_days": 5, "type": "Tourist Visa"},
            ("India", "USA"): {"required": True, "processing_days": 7, "type": "B1/B2 Visa"},
            ("India", "France"): {"required": True, "processing_days": 10, "type": "Schengen"},
            ("India", "Japan"): {"required": True, "processing_days": 5, "type": "Tourist Visa"},
        }
        
        key = (origin_country, destination_country)
        requirement = visa_requirements.get(key, {
            "required": True,
            "processing_days": 7,
            "type": "Tourist Visa"
        })
        
        return {
            "origin_country": origin_country,
            "destination_country": destination_country,
            "visa_required": requirement.get("required", True),
            "visa_type": requirement.get("type", "Tourist Visa"),
            "processing_days": requirement.get("processing_days"),
            "visa_free_days": requirement.get("visa_free_days"),
            "note": "Check official embassy website for latest requirements"
        }
    
    def check_age_restriction(self, activity: str, age: int) -> dict:
        """
        Check age restrictions for an activity.
        
        Args:
            activity: Activity name
            age: Traveler's age
            
        Returns:
            Age restriction information
        """
        logger.info(f"Checking age restriction for {activity}")
        
        # Mock age restrictions
        restrictions = {
            "Bungee Jumping": {"min_age": 18, "max_age": None},
            "Skydiving": {"min_age": 18, "max_age": None},
            "Scuba Diving": {"min_age": 10, "max_age": None},
            "Wine Tasting": {"min_age": 21, "max_age": None},
            "Casino": {"min_age": 21, "max_age": None},
            "Nightclub": {"min_age": 18, "max_age": None},
            "Museum": {"min_age": 0, "max_age": None},
            "Hiking": {"min_age": 0, "max_age": None},
            "Zip-lining": {"min_age": 12, "max_age": None},
            "Helicopter Tour": {"min_age": 0, "max_age": None}
        }
        
        restriction = restrictions.get(activity, {"min_age": 0, "max_age": None})
        min_age = restriction.get("min_age", 0)
        max_age = restriction.get("max_age")
        
        eligible = age >= min_age and (max_age is None or age <= max_age)
        
        return {
            "activity": activity,
            "traveler_age": age,
            "minimum_age": min_age,
            "maximum_age": max_age,
            "eligible": eligible,
            "message": f"{'Eligible' if eligible else 'Not eligible'} for {activity}"
        }
    
    def filter_activities_by_age(self, activities: list, age: int) -> list:
        """
        Filter activities based on age eligibility.
        
        Args:
            activities: List of activities
            age: Traveler's age
            
        Returns:
            Filtered list of age-appropriate activities
        """
        logger.info(f"Filtering activities for age {age}")
        
        eligible_activities = []
        
        for activity in activities:
            check = self.check_age_restriction(activity, age)
            if check["eligible"]:
                eligible_activities.append(activity)
        
        return eligible_activities
    
    def get_visa_application_info(self, destination_country: str) -> dict:
        """
        Get visa application information for a destination.
        
        Args:
            destination_country: Destination country
            
        Returns:
            Visa application information
        """
        logger.info(f"Getting visa application info for {destination_country}")
        
        # Mock visa application info
        visa_info = {
            "India": {
                "visa_type": "Tourist Visa",
                "processing_time": "5-7 business days",
                "validity": "6 months to 10 years",
                "cost": "$25-100 USD",
                "required_documents": [
                    "Valid passport (6+ months validity)",
                    "Completed visa application form",
                    "Passport-sized photograph",
                    "Proof of accommodation",
                    "Return flight ticket",
                    "Bank statements"
                ],
                "application_method": "Online (e-Visa) or Embassy",
                "website": "https://indianvisaonline.gov.in"
            },
            "France": {
                "visa_type": "Schengen Visa",
                "processing_time": "15 days",
                "validity": "90 days within 180 days",
                "cost": "€80 EUR",
                "required_documents": [
                    "Valid passport",
                    "Completed visa application",
                    "Passport photos",
                    "Travel insurance",
                    "Proof of accommodation",
                    "Flight bookings",
                    "Bank statements"
                ],
                "application_method": "Embassy or Consulate",
                "website": "https://france-visas.gouv.fr"
            },
            "Japan": {
                "visa_type": "Tourist Visa",
                "processing_time": "5-7 business days",
                "validity": "90 days",
                "cost": "Free for most nationalities",
                "required_documents": [
                    "Valid passport",
                    "Completed application form",
                    "Passport photo",
                    "Return flight ticket",
                    "Proof of funds"
                ],
                "application_method": "Embassy or Online",
                "website": "https://www.mofa.go.jp"
            }
        }
        
        return visa_info.get(destination_country, {
            "visa_type": "Tourist Visa",
            "processing_time": "7-10 business days",
            "validity": "Variable",
            "cost": "Variable",
            "required_documents": [
                "Valid passport",
                "Completed visa application",
                "Proof of accommodation",
                "Return flight ticket",
                "Bank statements"
            ],
            "application_method": "Embassy or Consulate",
            "website": "Check official embassy website"
        })
