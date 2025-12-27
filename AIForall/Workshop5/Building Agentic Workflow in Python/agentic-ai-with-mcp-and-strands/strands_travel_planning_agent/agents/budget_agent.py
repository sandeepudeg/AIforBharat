#!/usr/bin/env python3
"""
Budget Agent using Strands Framework

This agent handles budget tracking, cost analysis, and financial planning for trips.
Includes real-time currency conversion using exchange rate APIs.
"""

import logging
import requests
from typing import Dict, Optional

# Try to import Strands, but make it optional
try:
    from strands import Agent, tool
    from strands.models import BedrockModel
    from strands.session.s3_session_manager import S3SessionManager
    STRANDS_AVAILABLE = True
except ImportError:
    STRANDS_AVAILABLE = False
    # Create dummy classes for when Strands is not available
    class Agent:
        def __init__(self, *args, **kwargs):
            pass
    
    def tool(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)

# Exchange rate cache to minimize API calls
_exchange_rate_cache: Dict[str, float] = {}


class BudgetAgent(Agent):
    """Budget specialist agent using Strands framework."""
    
    def __init__(self, session_manager=None):
        """Initialize Budget Agent with Bedrock model and tools."""
        
        if STRANDS_AVAILABLE:
            model = BedrockModel(
                model_id="us.amazon.nova-pro-v1:0",
                temperature=0.3
            )
            
            system_prompt = """You are a travel budget expert. Your responsibilities:
1. Track and manage travel expenses
2. Provide budget breakdowns by category
3. Convert currencies for international travel
4. Suggest cost-saving opportunities
5. Provide financial planning advice

When users ask about budgets, use the available tools to track costs,
analyze spending, and provide money-saving recommendations."""
            
            super().__init__(
                model=model,
                system_prompt=system_prompt,
                session_manager=session_manager,
                tools=[
                    self.calculate_total_cost,
                    self.get_budget_breakdown,
                    self.convert_currency,
                    self.get_cost_saving_tips
                ]
            )
        else:
            # Initialize without Strands if not available
            logger.warning("Strands framework not available. Budget Agent will use fallback mode.")
            super().__init__()
    
    def calculate_total_cost(self, flights_cost: float, hotels_cost: float,
                            activities_cost: float, meals_cost: float,
                            transport_cost: float) -> dict:
        """
        Calculate total trip cost.
        
        Args:
            flights_cost: Flight expenses in USD
            hotels_cost: Hotel expenses in USD
            activities_cost: Activities and attractions in USD
            meals_cost: Food and dining in USD
            transport_cost: Local transportation in USD
            
        Returns:
            Total cost breakdown
        """
        logger.info("Calculating total trip cost")
        
        total = flights_cost + hotels_cost + activities_cost + meals_cost + transport_cost
        
        return {
            "flights": flights_cost,
            "hotels": hotels_cost,
            "activities": activities_cost,
            "meals": meals_cost,
            "transport": transport_cost,
            "total": total,
            "currency": "USD"
        }
    
    def get_budget_breakdown(self, total_budget: float, trip_days: int,
                            home_currency: str = "USD", 
                            destination_currency: str = "USD") -> dict:
        """
        Get recommended budget breakdown with dual-currency display.
        
        Args:
            total_budget: Total trip budget in home currency
            trip_days: Number of days
            home_currency: User's home currency code
            destination_currency: Destination country currency code
            
        Returns:
            Recommended budget allocation in both currencies
        """
        logger.info(f"Getting budget breakdown for ${total_budget} over {trip_days} days")
        
        # Typical allocation percentages
        allocation = {
            "flights": total_budget * 0.35,
            "hotels": total_budget * 0.35,
            "meals": total_budget * 0.15,
            "activities": total_budget * 0.10,
            "transport": total_budget * 0.05
        }
        
        daily_budget = total_budget / trip_days if trip_days > 0 else 0
        
        # Convert to destination currency if different
        result = {
            "total_budget": total_budget,
            "home_currency": home_currency,
            "trip_days": trip_days,
            "daily_budget": round(daily_budget, 2),
            "allocation": {k: round(v, 2) for k, v in allocation.items()},
            "allocation_percentages": {
                "flights": "35%",
                "hotels": "35%",
                "meals": "15%",
                "activities": "10%",
                "transport": "5%"
            }
        }
        
        # Add destination currency conversion if different
        if home_currency != destination_currency:
            try:
                exchange_rate = self._get_exchange_rate(home_currency, destination_currency)
                
                result["destination_currency"] = destination_currency
                result["total_budget_destination"] = round(total_budget * exchange_rate, 2)
                result["daily_budget_destination"] = round(daily_budget * exchange_rate, 2)
                result["allocation_destination"] = {
                    k: round(v * exchange_rate, 2) for k, v in allocation.items()
                }
                result["exchange_rate"] = round(exchange_rate, 4)
                
            except Exception as e:
                logger.warning(f"Could not convert to destination currency: {e}")
                result["conversion_note"] = "Destination currency conversion unavailable"
        
        return result
    
    def convert_currency(self, amount: float, from_currency: str, 
                        to_currency: str) -> dict:
        """
        Convert currency for international travel using real exchange rates.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (e.g., "USD")
            to_currency: Target currency code (e.g., "EUR")
            
        Returns:
            Converted amount with exchange rate
        """
        logger.info(f"Converting {amount} {from_currency} to {to_currency}")
        
        # Return early if same currency
        if from_currency == to_currency:
            return {
                "original_amount": amount,
                "original_currency": from_currency,
                "converted_amount": round(amount, 2),
                "converted_currency": to_currency,
                "exchange_rate": 1.0,
                "source": "same_currency"
            }
        
        try:
            # Try to fetch real exchange rates from exchangerate-api.com (free tier)
            exchange_rate = self._get_exchange_rate(from_currency, to_currency)
            converted = amount * exchange_rate
            
            return {
                "original_amount": amount,
                "original_currency": from_currency,
                "converted_amount": round(converted, 2),
                "converted_currency": to_currency,
                "exchange_rate": round(exchange_rate, 4),
                "source": "live_api"
            }
        except Exception as e:
            logger.warning(f"Failed to fetch live rates: {e}. Using fallback rates.")
            # Fallback to mock rates if API fails
            return self._convert_with_fallback_rates(amount, from_currency, to_currency)
    
    def _get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Fetch exchange rate from API with caching.
        
        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Exchange rate (to_currency per from_currency)
        """
        cache_key = f"{from_currency}_{to_currency}"
        
        # Check cache first
        if cache_key in _exchange_rate_cache:
            return _exchange_rate_cache[cache_key]
        
        try:
            # Use exchangerate-api.com free tier (no key required for basic usage)
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            rate = data.get("rates", {}).get(to_currency)
            
            if rate is None:
                raise ValueError(f"Currency {to_currency} not found in API response")
            
            # Cache the rate
            _exchange_rate_cache[cache_key] = rate
            return rate
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse exchange rate: {e}")
            raise
    
    def _convert_with_fallback_rates(self, amount: float, from_currency: str,
                                     to_currency: str) -> dict:
        """
        Convert using fallback mock rates when API is unavailable.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Converted amount with fallback rates
        """
        # Fallback exchange rates (as of reference date)
        rates = {
            "USD": 1.0,
            "EUR": 0.92,
            "GBP": 0.79,
            "JPY": 149.50,
            "AUD": 1.53,
            "CAD": 1.36,
            "CHF": 0.88,
            "CNY": 7.24,
            "INR": 83.12,
            "MXN": 17.05,
            "SGD": 1.34,
            "HKD": 7.81,
            "NZD": 1.68,
            "SEK": 10.45,
            "NOK": 10.65
        }
        
        from_rate = rates.get(from_currency, 1.0)
        to_rate = rates.get(to_currency, 1.0)
        
        converted = (amount / from_rate) * to_rate
        
        return {
            "original_amount": amount,
            "original_currency": from_currency,
            "converted_amount": round(converted, 2),
            "converted_currency": to_currency,
            "exchange_rate": round(to_rate / from_rate, 4),
            "source": "fallback_rates",
            "note": "Using cached rates - API unavailable"
        }
    
    def format_dual_currency(self, amount: float, home_currency: str,
                            destination_currency: str) -> dict:
        """
        Format a price in both home and destination currencies.
        
        Args:
            amount: Amount in home currency
            home_currency: User's home currency code
            destination_currency: Destination currency code
            
        Returns:
            Formatted price in both currencies
        """
        logger.info(f"Formatting {amount} {home_currency} in dual currency")
        
        result = {
            "home_amount": round(amount, 2),
            "home_currency": home_currency
        }
        
        if home_currency != destination_currency:
            try:
                conversion = self.convert_currency(amount, home_currency, destination_currency)
                result["destination_amount"] = conversion["converted_amount"]
                result["destination_currency"] = destination_currency
                result["exchange_rate"] = conversion["exchange_rate"]
                result["formatted"] = f"{home_currency} {amount:.2f} = {destination_currency} {conversion['converted_amount']:.2f}"
            except Exception as e:
                logger.warning(f"Could not format dual currency: {e}")
                result["formatted"] = f"{home_currency} {amount:.2f}"
        else:
            result["formatted"] = f"{home_currency} {amount:.2f}"
        
        return result
    
    def get_cost_saving_tips(self, destination: str, trip_type: str = "general") -> list:
        """
        Get cost-saving tips for a destination.
        
        Args:
            destination: City name
            trip_type: Type of trip (e.g., "budget", "luxury", "general")
            
        Returns:
            List of cost-saving tips
        """
        logger.info(f"Getting cost-saving tips for {destination}")
        
        general_tips = [
            "Book flights 2-3 months in advance",
            "Travel during shoulder season for better rates",
            "Use public transportation instead of taxis",
            "Eat at local restaurants instead of tourist areas",
            "Look for free attractions and walking tours",
            "Stay in hostels or budget hotels",
            "Buy groceries for some meals",
            "Use travel passes for attractions",
            "Negotiate prices at markets",
            "Travel with a group to share costs"
        ]
        
        destination_tips = {
            "Paris": [
                "Get a Paris Museum Pass for unlimited museum access",
                "Use the Metro instead of taxis",
                "Eat at bistros in residential areas",
                "Visit free attractions like parks and churches"
            ],
            "Tokyo": [
                "Get a Suica card for transportation",
                "Eat at convenience stores for cheap meals",
                "Visit temples and shrines (mostly free)",
                "Use the extensive public transportation system"
            ],
            "New York": [
                "Get a MetroCard for subway travel",
                "Visit free museums on designated hours",
                "Eat at food carts and delis",
                "Walk across bridges for free views"
            ]
        }
        
        tips = destination_tips.get(destination, general_tips)
        
        if trip_type == "budget":
            tips.extend([
                "Stay outside city center",
                "Cook your own meals",
                "Use free walking tours"
            ])
        
        return tips
