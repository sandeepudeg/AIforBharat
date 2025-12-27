#!/usr/bin/env python3
"""
Mock data for testing without API keys
Provides realistic sample data for all agents
"""

def get_mock_flights():
    """Return mock flight data"""
    return {
        "round_trips": [
            {
                "outbound": {
                    "airline": "United Airlines",
                    "flight_number": "UA123",
                    "departure_time": "2025-01-15 08:00",
                    "arrival_time": "2025-01-15 20:00",
                    "duration_minutes": 720,
                    "stops": 0,
                    "price": 450
                },
                "return": {
                    "airline": "United Airlines",
                    "flight_number": "UA456",
                    "departure_time": "2025-01-22 10:00",
                    "arrival_time": "2025-01-22 12:00",
                    "duration_minutes": 720,
                    "stops": 0,
                    "price": 450
                },
                "total_price": 900
            }
        ],
        "best_options": {
            "cheapest": {
                "outbound": {
                    "airline": "United Airlines",
                    "flight_number": "UA123",
                    "departure_time": "2025-01-15 08:00",
                    "arrival_time": "2025-01-15 20:00",
                    "duration_minutes": 720,
                    "stops": 0,
                    "price": 450
                },
                "return": {
                    "airline": "United Airlines",
                    "flight_number": "UA456",
                    "departure_time": "2025-01-22 10:00",
                    "arrival_time": "2025-01-22 12:00",
                    "duration_minutes": 720,
                    "stops": 0,
                    "price": 450
                },
                "total_price": 900
            }
        }
    }


def get_mock_hotels():
    """Return mock hotel data"""
    return [
        {
            "name": "Hotel Le Marais",
            "address": "75003 Paris, France",
            "price_per_night": 85,
            "rating": 4.5,
            "rooms_available": 5,
            "amenities": ["WiFi", "Breakfast", "Gym", "Spa"],
            "check_in_time": "15:00",
            "check_out_time": "11:00",
            "total_cost": 595
        },
        {
            "name": "Boutique Hotel Eiffel",
            "address": "75015 Paris, France",
            "price_per_night": 120,
            "rating": 4.8,
            "rooms_available": 3,
            "amenities": ["WiFi", "Restaurant", "Bar", "Concierge"],
            "check_in_time": "14:00",
            "check_out_time": "12:00",
            "total_cost": 840
        }
    ]


def get_mock_weather():
    """Return mock weather data"""
    return {
        "daily_forecasts": [
            {
                "date": "2025-01-15",
                "day_of_week": "Wednesday",
                "condition": "Rainy",
                "high_temp": 8,
                "low_temp": 5,
                "precipitation_chance": 80,
                "humidity": 75
            },
            {
                "date": "2025-01-16",
                "day_of_week": "Thursday",
                "condition": "Cloudy",
                "high_temp": 10,
                "low_temp": 6,
                "precipitation_chance": 40,
                "humidity": 65
            },
            {
                "date": "2025-01-17",
                "day_of_week": "Friday",
                "condition": "Sunny",
                "high_temp": 12,
                "low_temp": 7,
                "precipitation_chance": 10,
                "humidity": 55
            }
        ],
        "average_temp": 9,
        "conditions": "Mixed",
        "packing_tips": "Bring warm coat, umbrella, and comfortable walking shoes"
    }


def get_mock_itinerary():
    """Return mock itinerary data"""
    return {
        "weather_aware": True,
        "daily_itinerary": [
            {
                "day": 1,
                "date": "2025-01-15",
                "day_of_week": "Wednesday",
                "weather": {
                    "condition": "Rainy",
                    "high_temp": 8,
                    "precipitation_chance": 80,
                    "humidity": 75
                },
                "morning": {
                    "activity": "Arrival & Hotel Check-in",
                    "time": "09:00",
                    "reason": "Settle in after flight"
                },
                "afternoon": {
                    "activity": "Louvre Museum (Indoor)",
                    "time": "14:00",
                    "reason": "Perfect for rainy weather"
                },
                "evening": {
                    "activity": "Dinner at Local Bistro",
                    "time": "19:00",
                    "reason": "Cozy indoor dining"
                },
                "meals": {
                    "breakfast": "Hotel",
                    "lunch": "Café near Louvre",
                    "dinner": "Bistro in Marais"
                },
                "warnings": [
                    "Bring umbrella - 80% chance of rain",
                    "Wear waterproof jacket",
                    "Indoor activities recommended"
                ],
                "notes": "Day 1 cost: €120"
            },
            {
                "day": 2,
                "date": "2025-01-16",
                "day_of_week": "Thursday",
                "weather": {
                    "condition": "Cloudy",
                    "high_temp": 10,
                    "precipitation_chance": 40,
                    "humidity": 65
                },
                "morning": {
                    "activity": "Eiffel Tower Visit",
                    "time": "09:00",
                    "reason": "Best views in morning light"
                },
                "afternoon": {
                    "activity": "Seine River Cruise",
                    "time": "14:00",
                    "reason": "Scenic views of Paris"
                },
                "evening": {
                    "activity": "Montmartre Walk",
                    "time": "18:00",
                    "reason": "Beautiful sunset views"
                },
                "meals": {
                    "breakfast": "Café au lait & croissants",
                    "lunch": "Crêperie",
                    "dinner": "Traditional French restaurant"
                },
                "notes": "Day 2 cost: €150"
            }
        ]
    }


def get_mock_budget():
    """Return mock budget data"""
    return {
        "total_budget": 3000,
        "home_currency": "USD",
        "trip_days": 7,
        "daily_budget": 428.57,
        "allocation": {
            "flights": 1050.0,
            "hotels": 1050.0,
            "meals": 450.0,
            "activities": 300.0,
            "transport": 150.0
        },
        "allocation_percentages": {
            "flights": "35%",
            "hotels": "35%",
            "meals": "15%",
            "activities": "10%",
            "transport": "5%"
        }
    }


def get_mock_visa():
    """Return mock visa data"""
    return {
        "requirement": {
            "required": False,
            "visa_type": "Schengen",
            "duration_allowed": "90 days",
            "processing_time": "N/A"
        },
        "application_info": {
            "documents": [],
            "cost": 0,
            "notes": "US citizens do not require visa for Schengen area"
        }
    }


def get_mock_language():
    """Return mock language data"""
    return {
        "guide": {
            "primary_language": "French",
            "language_family": "Romance",
            "difficulty": "Moderate"
        },
        "common_phrases": {
            "hello": "Bonjour",
            "goodbye": "Au revoir",
            "thank_you": "Merci",
            "please": "S'il vous plaît",
            "excuse_me": "Excusez-moi",
            "help": "Aide!",
            "water": "Eau",
            "food": "Nourriture"
        }
    }


def get_mock_local_transport():
    """Return mock local transport data"""
    return {
        "airport_transfer": "RER B train (€11.45) or taxi (€50-60)",
        "public_transit": "Metro, buses, trams - Get Paris Visite pass",
        "rental_car": "Not recommended - parking expensive",
        "recommendations": "Use Metro for main attractions, walking for neighborhoods"
    }
