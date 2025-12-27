#!/usr/bin/env python3
"""
Itinerary Agent using Strands Framework

This agent handles itinerary planning, attraction recommendations, and daily schedules.
"""

import logging
from datetime import datetime, timedelta
from strands import Agent
from strands.models import BedrockModel
from strands.session.s3_session_manager import S3SessionManager

logger = logging.getLogger(__name__)


class ItineraryAgent(Agent):
    """Itinerary specialist agent using Strands framework."""
    
    def __init__(self, session_manager: S3SessionManager = None):
        """Initialize Itinerary Agent with Bedrock model and tools."""
        
        model = BedrockModel(
            model_id="us.amazon.nova-pro-v1:0",
            temperature=0.3
        )
        
        system_prompt = """You are an itinerary planning expert for travel. Your responsibilities:
1. Create day-by-day itineraries for trips
2. Recommend attractions and activities
3. Suggest meal options and restaurants
4. Calculate travel times between locations
5. Optimize daily schedules for maximum enjoyment

When users ask about itineraries, use the available tools to create detailed plans,
recommend attractions, and provide comprehensive travel schedules."""
        
        super().__init__(
            model=model,
            system_prompt=system_prompt,
            session_manager=session_manager,
            tools=[
                self.create_itinerary,
                self.get_attractions,
                self.suggest_meals,
                self.calculate_travel_time
            ]
        )
    
    def create_itinerary(self, destination: str, start_date: str, 
                        end_date: str, interests: list = None, weather_data: dict = None) -> dict:
        """
        Create a day-by-day itinerary, optionally weather-aware.
        
        Args:
            destination: City name
            start_date: Trip start date (YYYY-MM-DD)
            end_date: Trip end date (YYYY-MM-DD)
            interests: List of interests (e.g., ["culture", "food", "nature"])
            weather_data: Optional weather forecast data for weather-aware planning
            
        Returns:
            Detailed itinerary
        """
        logger.info(f"Creating itinerary for {destination} ({start_date} to {end_date})")
        
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except (ValueError, TypeError):
            return {"error": "Invalid date format"}
        
        attractions = self.get_attractions(destination, interests or [])
        daily_itinerary = []
        current = start
        day_num = 1
        
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            
            # Get weather for this day if available
            day_weather = None
            if weather_data:
                day_weather = next(
                    (f for f in weather_data.get("daily_forecasts", []) 
                     if f.get("date") == date_str),
                    None
                )
            
            # Use weather-aware planning if weather data available
            if day_weather:
                day_plan = self._create_weather_aware_day_plan(
                    destination, day_num, current, day_weather, attractions
                )
            else:
                day_attractions = attractions[day_num-1:day_num+2] if day_num < len(attractions) else attractions[-3:]
                
                day_plan = {
                    "day": day_num,
                    "date": date_str,
                    "day_of_week": current.strftime("%A"),
                    "morning": {
                        "activity": day_attractions[0].get("name") if day_attractions else "Rest",
                        "time": "09:00-12:00"
                    },
                    "afternoon": {
                        "activity": day_attractions[1].get("name") if len(day_attractions) > 1 else "Lunch & Explore",
                        "time": "13:00-17:00"
                    },
                    "evening": {
                        "activity": day_attractions[2].get("name") if len(day_attractions) > 2 else "Dinner",
                        "time": "18:00-21:00"
                    },
                    "meals": self.suggest_meals(destination, day_num),
                    "notes": f"Day {day_num} of your {(end-start).days + 1}-day trip"
                }
            
            daily_itinerary.append(day_plan)
            current += timedelta(days=1)
            day_num += 1
        
        return {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": (end - start).days + 1,
            "daily_itinerary": daily_itinerary,
            "weather_aware": weather_data is not None
        }
    
    def get_attractions(self, destination: str, interests: list = None) -> list:
        """
        Get attractions for a destination.
        
        Args:
            destination: City name
            interests: List of interest categories
            
        Returns:
            List of attractions
        """
        logger.info(f"Getting attractions for {destination}")
        
        attractions = self._get_mock_attractions(destination)
        
        if interests:
            attractions = [a for a in attractions if a.get("category") in interests]
        
        return attractions
    
    def suggest_meals(self, destination: str, day: int) -> dict:
        """
        Suggest meals for a day.
        
        Args:
            destination: City name
            day: Day number
            
        Returns:
            Meal suggestions
        """
        logger.info(f"Suggesting meals for {destination} day {day}")
        
        meal_options = {
            "breakfast": [
                "Local café with pastries",
                "Hotel breakfast buffet",
                "Street food market"
            ],
            "lunch": [
                "Traditional restaurant",
                "Food court",
                "Picnic at park"
            ],
            "dinner": [
                "Fine dining restaurant",
                "Local bistro",
                "Street food experience"
            ]
        }
        
        return {
            "breakfast": meal_options["breakfast"][day % 3],
            "lunch": meal_options["lunch"][day % 3],
            "dinner": meal_options["dinner"][day % 3],
            "estimated_cost": f"${30 + (day * 5)}"
        }
    
    def calculate_travel_time(self, origin: str, destination: str, 
                             transport_mode: str = "public") -> dict:
        """
        Calculate travel time between locations.
        
        Args:
            origin: Starting location
            destination: Ending location
            transport_mode: "public", "taxi", "walking"
            
        Returns:
            Travel time information
        """
        logger.info(f"Calculating travel time from {origin} to {destination}")
        
        # Mock travel times
        base_time = 30
        
        if transport_mode == "walking":
            time_minutes = base_time * 2
            cost = 0
        elif transport_mode == "taxi":
            time_minutes = base_time // 2
            cost = 15
        else:  # public transport
            time_minutes = base_time
            cost = 3
        
        return {
            "origin": origin,
            "destination": destination,
            "transport_mode": transport_mode,
            "time_minutes": time_minutes,
            "estimated_cost": f"${cost}",
            "description": f"{time_minutes} minutes by {transport_mode} transport"
        }
    
    def _create_weather_aware_day_plan(self, destination: str, day_num: int, 
                                       date: datetime, weather: dict, attractions: list) -> dict:
        """
        Create a day plan based on weather conditions.
        
        Args:
            destination: City name
            day_num: Day number
            date: Date object
            weather: Weather forecast for the day
            attractions: Available attractions
            
        Returns:
            Weather-aware day plan
        """
        condition = weather.get("condition", "Cloudy")
        temp = weather.get("high_temp", 20)
        precip = weather.get("precipitation_chance", 0)
        
        # Select activities based on weather
        activities = self._select_activities_by_weather(condition, temp, precip)
        
        # Get specific activities for each time period
        morning = self._get_morning_activity(activities, condition, temp)
        afternoon = self._get_afternoon_activity(activities, condition, temp)
        evening = self._get_evening_activity(activities, condition)
        
        # Get weather-appropriate meals
        meals = self._suggest_weather_based_meals(destination, condition, temp)
        
        # Get weather warnings
        warnings = self._get_weather_warnings(condition, temp, precip)
        
        day_plan = {
            "day": day_num,
            "date": date.strftime("%Y-%m-%d"),
            "day_of_week": date.strftime("%A"),
            "weather": {
                "condition": condition,
                "high_temp": temp,
                "low_temp": weather.get("low_temp", 15),
                "precipitation_chance": precip,
                "wind_speed": weather.get("wind_speed", 5),
                "humidity": weather.get("humidity", 50)
            },
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
            "meals": meals,
            "warnings": warnings,
            "notes": f"Day {day_num} - Activities adapted to {condition} weather"
        }
        
        return day_plan
    
    def _select_activities_by_weather(self, condition: str, temp: float, precip: float) -> dict:
        """
        Select activity categories based on weather conditions.
        
        Args:
            condition: Weather condition (Sunny, Rainy, etc.)
            temp: Temperature in Celsius
            precip: Precipitation chance (0-100)
            
        Returns:
            Dictionary with outdoor and indoor activity suggestions
        """
        activities = {
            "Sunny": {
                "outdoor": ["Beach", "Hiking", "Sightseeing", "Picnic", "Photography", "Park Visit"],
                "indoor": ["Museum", "Shopping", "Cafe", "Restaurant"]
            },
            "Partly Cloudy": {
                "outdoor": ["Walking Tour", "Park Visit", "Outdoor Market", "Sightseeing"],
                "indoor": ["Museum", "Gallery", "Shopping", "Cafe"]
            },
            "Cloudy": {
                "outdoor": ["Walking Tour", "Local Market", "Sightseeing"],
                "indoor": ["Museum", "Shopping", "Cafe", "Theater", "Gallery"]
            },
            "Rainy": {
                "outdoor": [],
                "indoor": ["Museum", "Shopping", "Spa", "Theater", "Restaurant", "Cooking Class", "Art Gallery"]
            },
            "Stormy": {
                "outdoor": [],
                "indoor": ["Museum", "Shopping", "Spa", "Theater", "Restaurant", "Hotel Activities", "Movie"]
            }
        }
        
        # Temperature-based adjustments
        if temp > 30:  # Hot
            outdoor = activities[condition].get("outdoor", [])
            outdoor = [a for a in outdoor if a not in ["Hiking"]]
            outdoor.extend(["Water Sports", "Swimming", "Beach"])
            activities[condition]["outdoor"] = outdoor
        
        if temp < 10:  # Cold
            outdoor = activities[condition].get("outdoor", [])
            outdoor = [a for a in outdoor if a not in ["Beach", "Water Sports", "Swimming"]]
            outdoor.extend(["Skiing", "Winter Sports", "Hot Springs"])
            activities[condition]["outdoor"] = outdoor
        
        return activities.get(condition, activities["Cloudy"])
    
    def _get_morning_activity(self, activities: dict, condition: str, temp: float) -> dict:
        """Get morning activity based on weather."""
        outdoor = activities.get("outdoor", [])
        indoor = activities.get("indoor", [])
        
        if outdoor and condition != "Rainy" and condition != "Stormy":
            return {
                "activity": outdoor[0],
                "time": "08:00-12:00",
                "duration": "4 hours",
                "reason": "Best time for outdoor activities"
            }
        else:
            return {
                "activity": indoor[0] if indoor else "Rest",
                "time": "09:00-12:00",
                "duration": "3 hours",
                "reason": "Weather not suitable for outdoor activities"
            }
    
    def _get_afternoon_activity(self, activities: dict, condition: str, temp: float) -> dict:
        """Get afternoon activity based on weather."""
        outdoor = activities.get("outdoor", [])
        indoor = activities.get("indoor", [])
        
        if len(outdoor) > 1 and condition not in ["Rainy", "Stormy"]:
            return {
                "activity": outdoor[1],
                "time": "13:00-17:00",
                "duration": "4 hours",
                "reason": "Continue outdoor exploration"
            }
        elif outdoor and condition not in ["Rainy", "Stormy"]:
            return {
                "activity": outdoor[0],
                "time": "13:00-17:00",
                "duration": "4 hours",
                "reason": "Afternoon outdoor activity"
            }
        else:
            return {
                "activity": indoor[1] if len(indoor) > 1 else indoor[0] if indoor else "Rest",
                "time": "13:00-17:00",
                "duration": "4 hours",
                "reason": "Indoor activity due to weather"
            }
    
    def _get_evening_activity(self, activities: dict, condition: str) -> dict:
        """Get evening activity based on weather."""
        return {
            "activity": "Dinner & Local Entertainment",
            "time": "18:00-21:00",
            "duration": "3 hours",
            "reason": "Evening relaxation and dining"
        }
    
    def _suggest_weather_based_meals(self, destination: str, condition: str, temp: float) -> dict:
        """Suggest meals based on weather and destination."""
        meal_suggestions = {
            "Sunny": {
                "breakfast": "Outdoor cafe breakfast with fresh juice",
                "lunch": "Picnic or outdoor restaurant with light meals",
                "dinner": "Rooftop restaurant with views"
            },
            "Partly Cloudy": {
                "breakfast": "Cafe breakfast",
                "lunch": "Restaurant or outdoor seating",
                "dinner": "Traditional restaurant"
            },
            "Cloudy": {
                "breakfast": "Hotel breakfast or cozy cafe",
                "lunch": "Restaurant or food court",
                "dinner": "Warm restaurant"
            },
            "Rainy": {
                "breakfast": "Hotel breakfast or cozy cafe",
                "lunch": "Indoor restaurant or food court",
                "dinner": "Warm restaurant or hotel dining"
            },
            "Stormy": {
                "breakfast": "Hotel breakfast",
                "lunch": "Room service or nearby restaurant",
                "dinner": "Hotel dining or nearby warm restaurant"
            }
        }
        
        meals = meal_suggestions.get(condition, {
            "breakfast": "Local breakfast spot",
            "lunch": "Restaurant or local food",
            "dinner": "Traditional restaurant"
        })
        
        # Temperature adjustments
        if temp > 30:
            meals["lunch"] = meals["lunch"].replace("warm", "cool").replace("Warm", "Cool")
            meals["lunch"] += " (cold drinks recommended)"
        
        if temp < 10:
            meals["breakfast"] = "Hot breakfast with warm beverages"
            meals["lunch"] = "Warm soup or hot meal"
            meals["dinner"] = "Warm restaurant with hot meals"
        
        return meals
    
    def _get_weather_warnings(self, condition: str, temp: float, precip: float) -> list:
        """Get weather-related warnings and tips."""
        warnings = []
        
        if condition == "Rainy":
            warnings.append("☔ Bring umbrella and waterproof jacket")
            warnings.append("⚠️ Watch for slippery surfaces")
        
        if condition == "Stormy":
            warnings.append("⛈️ Stay indoors, avoid outdoor activities")
            warnings.append("⚠️ Check weather updates regularly")
            warnings.append("🏨 Consider indoor attractions only")
        
        if temp > 35:
            warnings.append("🌡️ Extreme heat - stay hydrated")
            warnings.append("☀️ Use high SPF sunscreen (SPF 50+)")
            warnings.append("⏰ Avoid midday sun (12 PM - 3 PM)")
            warnings.append("👕 Wear light, breathable clothing")
        
        if temp < 0:
            warnings.append("❄️ Freezing conditions - dress warmly")
            warnings.append("⚠️ Watch for ice on roads and paths")
            warnings.append("🧤 Wear gloves, hat, and warm layers")
        
        if precip > 70:
            warnings.append("💧 High chance of rain - plan indoor activities")
        
        return warnings
    
    def _get_mock_attractions(self, destination: str) -> list:
        """Generate mock attraction data."""
        attractions_db = {
            "Paris": [
                {"name": "Eiffel Tower", "category": "landmark", "duration_hours": 2, "rating": 4.8},
                {"name": "Louvre Museum", "category": "culture", "duration_hours": 3, "rating": 4.7},
                {"name": "Notre-Dame Cathedral", "category": "culture", "duration_hours": 1.5, "rating": 4.6},
                {"name": "Arc de Triomphe", "category": "landmark", "duration_hours": 1, "rating": 4.5},
                {"name": "Sacré-Cœur", "category": "culture", "duration_hours": 1.5, "rating": 4.4},
                {"name": "Seine River Cruise", "category": "nature", "duration_hours": 2, "rating": 4.3},
                {"name": "Versailles Palace", "category": "culture", "duration_hours": 4, "rating": 4.7},
                {"name": "Latin Quarter", "category": "culture", "duration_hours": 2, "rating": 4.2},
                {"name": "Montmartre", "category": "culture", "duration_hours": 2, "rating": 4.3},
                {"name": "Champs-Élysées", "category": "shopping", "duration_hours": 2, "rating": 4.1}
            ],
            "Tokyo": [
                {"name": "Senso-ji Temple", "category": "culture", "duration_hours": 1.5, "rating": 4.6},
                {"name": "Tokyo Tower", "category": "landmark", "duration_hours": 2, "rating": 4.5},
                {"name": "Shibuya Crossing", "category": "landmark", "duration_hours": 1, "rating": 4.4},
                {"name": "Meiji Shrine", "category": "culture", "duration_hours": 1.5, "rating": 4.5},
                {"name": "Tsukiji Market", "category": "food", "duration_hours": 2, "rating": 4.3},
                {"name": "Akihabara", "category": "shopping", "duration_hours": 2, "rating": 4.2},
                {"name": "Harajuku", "category": "culture", "duration_hours": 2, "rating": 4.1},
                {"name": "Imperial Palace", "category": "culture", "duration_hours": 2, "rating": 4.3},
                {"name": "Roppongi Hills", "category": "landmark", "duration_hours": 1.5, "rating": 4.0},
                {"name": "Ueno Park", "category": "nature", "duration_hours": 2, "rating": 4.2}
            ]
        }
        
        return attractions_db.get(destination, [
            {"name": "Main Attraction", "category": "landmark", "duration_hours": 2, "rating": 4.0},
            {"name": "Museum", "category": "culture", "duration_hours": 2, "rating": 4.0},
            {"name": "Park", "category": "nature", "duration_hours": 1.5, "rating": 4.0},
            {"name": "Restaurant", "category": "food", "duration_hours": 1.5, "rating": 4.0},
            {"name": "Shopping District", "category": "shopping", "duration_hours": 2, "rating": 4.0}
        ])
