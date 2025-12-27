#!/usr/bin/env python3
"""
Weather Agent using Strands Framework

This agent demonstrates how to build a weather specialist using the Strands Agent framework
with Bedrock models and session management capabilities.
"""

import logging
from datetime import datetime, timedelta
from strands import Agent
from strands.models import BedrockModel
from strands.session.s3_session_manager import S3SessionManager

logger = logging.getLogger(__name__)


class WeatherAgent(Agent):
    """Weather specialist agent using Strands framework."""
    
    def __init__(self, session_manager: S3SessionManager = None):
        """Initialize Weather Agent with Bedrock model and tools."""
        
        model = BedrockModel(
            model_id="us.amazon.nova-pro-v1:0",
            temperature=0.3
        )
        
        system_prompt = """You are a weather expert assistant for travel planning. Your responsibilities:
1. Provide accurate weather forecasts for destinations
2. Analyze climate patterns and seasonal weather
3. Give packing recommendations based on weather conditions
4. Identify the best days for outdoor activities
5. Provide weather-related travel advice

When users ask about weather, use the available tools to get forecast data,
analyze it, and provide comprehensive recommendations."""
        
        super().__init__(
            model=model,
            system_prompt=system_prompt,
            session_manager=session_manager,
            tools=[
                self.get_forecast,
                self.analyze_weather,
                self.get_packing_recommendations,
                self.identify_best_days
            ]
        )
    
    def get_forecast(self, destination: str, start_date: str, end_date: str) -> dict:
        """
        Get weather forecast for a destination and date range.
        
        Args:
            destination: City name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with forecast data
        """
        logger.info(f"Getting forecast for {destination} ({start_date} to {end_date})")
        
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except (ValueError, TypeError):
            return {"error": "Invalid date format"}
        
        daily_forecasts = []
        current = start
        
        while current <= end:
            day_forecast = {
                "date": current.strftime("%Y-%m-%d"),
                "day_of_week": current.strftime("%A"),
                "high_temp": 20 + (hash(current.isoformat()) % 10),
                "low_temp": 12 + (hash(current.isoformat()) % 8),
                "condition": self._get_mock_condition(current),
                "precipitation_chance": (hash(current.isoformat()) % 100),
                "wind_speed": 5 + (hash(current.isoformat()) % 15),
                "humidity": 40 + (hash(current.isoformat()) % 50)
            }
            daily_forecasts.append(day_forecast)
            current += timedelta(days=1)
        
        forecast = {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "daily_forecasts": daily_forecasts
        }
        
        return forecast
    
    def analyze_weather(self, destination: str, start_date: str, end_date: str) -> dict:
        """
        Analyze weather patterns for a destination.
        
        Args:
            destination: City name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Analysis dictionary with insights
        """
        logger.info(f"Analyzing weather for {destination}")
        
        forecast = self.get_forecast(destination, start_date, end_date)
        daily_forecasts = forecast.get("daily_forecasts", [])
        
        if not daily_forecasts:
            return {"error": "No forecast data to analyze"}
        
        temps = [f.get("high_temp", 0) for f in daily_forecasts]
        precip = [f.get("precipitation_chance", 0) for f in daily_forecasts]
        
        analysis = {
            "destination": destination,
            "average_high_temp": round(sum(temps) / len(temps), 1) if temps else 0,
            "average_precipitation": round(sum(precip) / len(precip), 1) if precip else 0,
            "rainy_days": sum(1 for f in daily_forecasts if f.get("precipitation_chance", 0) > 50),
            "sunny_days": sum(1 for f in daily_forecasts if f.get("condition") == "Sunny"),
            "overall_assessment": self._assess_weather(daily_forecasts)
        }
        
        return analysis
    
    def get_packing_recommendations(self, destination: str, start_date: str, end_date: str) -> list:
        """
        Get packing recommendations based on forecast.
        
        Args:
            destination: City name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of packing recommendations
        """
        logger.info(f"Getting packing recommendations for {destination}")
        
        forecast = self.get_forecast(destination, start_date, end_date)
        daily_forecasts = forecast.get("daily_forecasts", [])
        recommendations = []
        
        if not daily_forecasts:
            return ["Valid passport", "Travel documents"]
        
        # Check for rain
        rainy_days = sum(1 for f in daily_forecasts if f.get("precipitation_chance", 0) > 50)
        if rainy_days > 0:
            recommendations.append("Umbrella or rain jacket")
        
        # Check for cold
        min_temp = min(f.get("low_temp", 20) for f in daily_forecasts)
        if min_temp < 10:
            recommendations.append("Warm jacket or sweater")
        elif min_temp < 15:
            recommendations.append("Light jacket")
        
        # Check for heat
        max_temp = max(f.get("high_temp", 20) for f in daily_forecasts)
        if max_temp > 25:
            recommendations.append("Sunscreen and sunglasses")
        if max_temp > 30:
            recommendations.append("Light, breathable clothing")
        
        # Always recommend
        recommendations.extend([
            "Comfortable walking shoes",
            "Portable charger for phone"
        ])
        
        return recommendations
    
    def identify_best_days(self, destination: str, start_date: str, end_date: str) -> list:
        """
        Identify the best days for outdoor activities.
        
        Args:
            destination: City name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of best days with reasons
        """
        logger.info(f"Identifying best days for {destination}")
        
        forecast = self.get_forecast(destination, start_date, end_date)
        daily_forecasts = forecast.get("daily_forecasts", [])
        best_days = []
        
        for day in daily_forecasts:
            score = 0
            
            # Sunny weather is best
            if day.get("condition") == "Sunny":
                score += 3
            elif day.get("condition") == "Partly Cloudy":
                score += 2
            
            # Low precipitation is good
            precip = day.get("precipitation_chance", 0)
            if precip < 20:
                score += 2
            elif precip < 50:
                score += 1
            
            # Moderate temperature is best
            high_temp = day.get("high_temp", 20)
            if 15 <= high_temp <= 25:
                score += 2
            elif 10 <= high_temp <= 30:
                score += 1
            
            if score >= 5:
                best_days.append({
                    "date": day.get("date"),
                    "day_of_week": day.get("day_of_week"),
                    "reason": f"{day.get('condition')}, {high_temp}°C",
                    "score": score
                })
        
        return best_days
    
    def _get_mock_condition(self, date: datetime) -> str:
        """Get mock weather condition based on date."""
        conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Stormy"]
        return conditions[hash(date.isoformat()) % len(conditions)]
    
    def _assess_weather(self, daily_forecasts: list) -> str:
        """Assess overall weather conditions."""
        sunny_days = sum(1 for f in daily_forecasts if f.get("condition") == "Sunny")
        rainy_days = sum(1 for f in daily_forecasts if f.get("precipitation_chance", 0) > 50)
        total_days = len(daily_forecasts)
        
        if sunny_days >= total_days * 0.7:
            return "Excellent weather for outdoor activities"
        elif rainy_days >= total_days * 0.5:
            return "Mixed weather - plan indoor activities for rainy days"
        else:
            return "Good weather overall"
