#!/usr/bin/env python3
"""
Date Optimizer Component

Analyzes flight prices across multiple dates and recommends optimal travel windows.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable

logger = logging.getLogger(__name__)


class DateOptimizer:
    """Optimizes travel dates based on price analysis."""
    
    # Deal thresholds
    GREAT_DEAL_THRESHOLD = 0.20  # 20% savings
    EXCEPTIONAL_SAVINGS_THRESHOLD = 0.30  # 30% savings
    
    # Price trend thresholds
    STABLE_THRESHOLD = 0.05  # 5% variation
    
    @staticmethod
    def analyze_date_window(
        origin: str,
        destination: str,
        center_date: str,
        fetch_flights_fn: Callable,
        window_days: int = 7
    ) -> Dict:
        """
        Analyze flight prices across a date window.
        
        Args:
            origin: Departure city
            destination: Arrival city
            center_date: Center date (YYYY-MM-DD)
            fetch_flights_fn: Function to fetch flights for a date
            window_days: Days before/after center date to analyze
            
        Returns:
            Date analysis result with statistics and recommendations
        """
        try:
            center = datetime.strptime(center_date, "%Y-%m-%d")
        except ValueError:
            logger.error(f"Invalid date format: {center_date}")
            return {"error": "Invalid date format"}
        
        # Generate date range
        dates = []
        for i in range(-window_days, window_days + 1):
            date = center + timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
        
        # Fetch flights for each date
        date_flights = {}
        for date in dates:
            try:
                flights = fetch_flights_fn(origin, destination, date)
                date_flights[date] = flights if flights else []
            except Exception as e:
                logger.warning(f"Failed to fetch flights for {date}: {e}")
                date_flights[date] = []
        
        # Calculate statistics for each date
        date_stats = DateOptimizer.calculate_date_statistics(date_flights)
        
        # Identify peak and off-peak dates
        peak_date = DateOptimizer.identify_peak_price_date(date_stats)
        off_peak_date = DateOptimizer.identify_off_peak_date(date_stats)
        
        # Get reference price (center date)
        reference_price = date_stats.get(center_date, {}).get("average_price", 0)
        
        # Calculate savings potential for each date
        for stat in date_stats.values():
            if reference_price > 0:
                savings = ((reference_price - stat["average_price"]) / reference_price) * 100
                stat["savings_vs_requested"] = round(savings, 2)
            else:
                stat["savings_vs_requested"] = 0
        
        # Recommend cost-effective dates
        recommendations = DateOptimizer.recommend_cost_effective_dates(date_stats, top_n=3)
        
        # Identify price trend
        trend = DateOptimizer.identify_price_trends(date_stats)
        
        # Calculate overall price range
        all_prices = [s["average_price"] for s in date_stats.values() if s["average_price"] > 0]
        price_range = {
            "min": min(all_prices) if all_prices else 0,
            "max": max(all_prices) if all_prices else 0,
            "difference": (max(all_prices) - min(all_prices)) if all_prices else 0
        }
        
        return {
            "origin": origin,
            "destination": destination,
            "center_date": center_date,
            "window_days": window_days,
            "date_statistics": date_stats,
            "peak_price_date": peak_date,
            "off_peak_date": off_peak_date,
            "recommendations": recommendations,
            "price_trend": trend,
            "average_price_all_dates": sum(s["average_price"] for s in date_stats.values()) / len(date_stats) if date_stats else 0,
            "price_range": price_range
        }
    
    @staticmethod
    def calculate_date_statistics(date_flights: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """
        Calculate price statistics for each date.
        
        Args:
            date_flights: Dictionary mapping dates to flight lists
            
        Returns:
            Dictionary with statistics for each date
        """
        stats = {}
        
        for date, flights in date_flights.items():
            if not flights:
                stats[date] = {
                    "date": date,
                    "day_of_week": DateOptimizer._get_day_of_week(date),
                    "average_price": 0,
                    "min_price": 0,
                    "max_price": 0,
                    "flight_count": 0
                }
                continue
            
            prices = [f.get("price", 0) for f in flights if f.get("price", 0) > 0]
            
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
            else:
                avg_price = min_price = max_price = 0
            
            stats[date] = {
                "date": date,
                "day_of_week": DateOptimizer._get_day_of_week(date),
                "average_price": round(avg_price, 2),
                "min_price": round(min_price, 2),
                "max_price": round(max_price, 2),
                "flight_count": len(flights)
            }
        
        return stats
    
    @staticmethod
    def identify_peak_price_date(date_stats: Dict[str, Dict]) -> Optional[Dict]:
        """
        Find the date with highest average price.
        
        Args:
            date_stats: Dictionary with date statistics
            
        Returns:
            Peak price date statistics or None
        """
        if not date_stats:
            return None
        
        valid_stats = [s for s in date_stats.values() if s.get("average_price", 0) > 0]
        if not valid_stats:
            return None
        
        peak = max(valid_stats, key=lambda s: s.get("average_price", 0))
        peak["is_peak"] = True
        return peak
    
    @staticmethod
    def identify_off_peak_date(date_stats: Dict[str, Dict]) -> Optional[Dict]:
        """
        Find the date with lowest average price.
        
        Args:
            date_stats: Dictionary with date statistics
            
        Returns:
            Off-peak date statistics or None
        """
        if not date_stats:
            return None
        
        valid_stats = [s for s in date_stats.values() if s.get("average_price", 0) > 0]
        if not valid_stats:
            return None
        
        off_peak = min(valid_stats, key=lambda s: s.get("average_price", 0))
        off_peak["is_off_peak"] = True
        return off_peak
    
    @staticmethod
    def calculate_savings_potential(date_price: float, reference_price: float) -> float:
        """
        Calculate percentage savings compared to reference price.
        
        Args:
            date_price: Price on the date
            reference_price: Reference price for comparison
            
        Returns:
            Savings percentage
        """
        if reference_price <= 0:
            return 0
        
        savings = ((reference_price - date_price) / reference_price) * 100
        return round(savings, 2)
    
    @staticmethod
    def recommend_cost_effective_dates(
        date_stats: Dict[str, Dict],
        top_n: int = 3
    ) -> List[Dict]:
        """
        Recommend the top N most cost-effective dates.
        
        Args:
            date_stats: Dictionary with date statistics
            top_n: Number of recommendations to return
            
        Returns:
            List of recommended dates with reasoning
        """
        # Filter dates with flights
        valid_dates = [
            (date, stats) for date, stats in date_stats.items()
            if stats.get("average_price", 0) > 0
        ]
        
        if not valid_dates:
            return []
        
        # Sort by average price (lowest first)
        valid_dates.sort(key=lambda x: x[1].get("average_price", 0))
        
        # Get reference price (average of all dates)
        all_prices = [s.get("average_price", 0) for _, s in valid_dates]
        avg_price = sum(all_prices) / len(all_prices) if all_prices else 0
        
        recommendations = []
        for date, stats in valid_dates[:top_n]:
            savings_pct = DateOptimizer.calculate_savings_potential(
                stats.get("average_price", 0),
                avg_price
            )
            
            # Determine deal level
            if savings_pct > (DateOptimizer.EXCEPTIONAL_SAVINGS_THRESHOLD * 100):
                deal_level = "Exceptional Savings"
            elif savings_pct > (DateOptimizer.GREAT_DEAL_THRESHOLD * 100):
                deal_level = "Great Deal"
            else:
                deal_level = "Good Deal"
            
            savings_amount = avg_price - stats.get("average_price", 0)
            
            reason = f"Save ${savings_amount:.2f} ({savings_pct:.1f}%) on {stats['day_of_week']}"
            
            recommendations.append({
                "date": date,
                "day_of_week": stats["day_of_week"],
                "average_price": stats["average_price"],
                "savings_amount": round(savings_amount, 2),
                "savings_percentage": savings_pct,
                "reason": reason,
                "deal_level": deal_level,
                "flight_count": stats.get("flight_count", 0)
            })
        
        return recommendations
    
    @staticmethod
    def identify_price_trends(date_stats: Dict[str, Dict]) -> str:
        """
        Identify price trends (increasing, decreasing, stable).
        
        Args:
            date_stats: Dictionary with date statistics
            
        Returns:
            Trend description
        """
        if not date_stats:
            return "unknown"
        
        # Sort by date
        sorted_dates = sorted(date_stats.keys())
        valid_prices = [
            date_stats[d].get("average_price", 0)
            for d in sorted_dates
            if date_stats[d].get("average_price", 0) > 0
        ]
        
        if len(valid_prices) < 2:
            return "insufficient_data"
        
        # Calculate average price for first and second half
        mid = len(valid_prices) // 2
        first_half_avg = sum(valid_prices[:mid]) / len(valid_prices[:mid])
        second_half_avg = sum(valid_prices[mid:]) / len(valid_prices[mid:])
        
        # Calculate percentage change
        if first_half_avg > 0:
            pct_change = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        else:
            pct_change = 0
        
        # Determine trend
        if abs(pct_change) < DateOptimizer.STABLE_THRESHOLD * 100:
            return "stable"
        elif pct_change > 0:
            return "increasing"
        else:
            return "decreasing"
    
    @staticmethod
    def _get_day_of_week(date_str: str) -> str:
        """
        Get day of week for a date string.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            Day of week name
        """
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            return days[date.weekday()]
        except ValueError:
            return "Unknown"
