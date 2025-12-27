#!/usr/bin/env python3
"""
Property-based tests for Date_Optimizer component.

Tests validate correctness properties for date analysis functionality.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from date_optimizer import DateOptimizer


# Strategies for generating test data
@st.composite
def date_string_strategy(draw):
    """Generate a valid date string."""
    year = draw(st.integers(min_value=2024, max_value=2025))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))
    return f"{year:04d}-{month:02d}-{day:02d}"


@st.composite
def flight_strategy(draw):
    """Generate a valid flight dictionary."""
    return {
        "flight_id": draw(st.text(min_size=1, max_size=10)),
        "airline": draw(st.text(min_size=1, max_size=20)),
        "price": draw(st.floats(min_value=50, max_value=2000)),
        "duration_minutes": draw(st.integers(min_value=30, max_value=1440))
    }


@st.composite
def flights_list_strategy(draw):
    """Generate a list of flights."""
    return draw(st.lists(flight_strategy(), min_size=1, max_size=20))


@st.composite
def date_flights_strategy(draw):
    """Generate date to flights mapping."""
    dates = draw(st.lists(date_string_strategy(), min_size=3, max_size=10, unique=True))
    return {date: draw(flights_list_strategy()) for date in dates}


class TestDateWindowAnalysisCompleteness:
    """Test Property 6: Date Window Analysis Completeness."""
    
    def test_date_window_includes_all_dates(self):
        """
        For any center date and window size N,
        analysis should include all dates in [center_date - N, center_date + N].
        """
        center_date = "2024-06-15"
        window_days = 3
        
        # Mock fetch function
        def mock_fetch(origin, dest, date):
            return [{"price": 100, "duration_minutes": 300}]
        
        result = DateOptimizer.analyze_date_window(
            "NYC", "LAX", center_date, mock_fetch, window_days
        )
        
        # Should have 2*window_days + 1 dates (including center)
        expected_count = 2 * window_days + 1
        assert len(result["date_statistics"]) == expected_count
        
        # Verify all dates are in range
        center = datetime.strptime(center_date, "%Y-%m-%d")
        for date_str in result["date_statistics"].keys():
            date = datetime.strptime(date_str, "%Y-%m-%d")
            days_diff = abs((date - center).days)
            assert days_diff <= window_days


class TestDateStatisticsCalculation:
    """Test date statistics calculation."""
    
    @given(date_flights=date_flights_strategy())
    def test_statistics_calculated_for_all_dates(self, date_flights):
        """Statistics should be calculated for all dates."""
        stats = DateOptimizer.calculate_date_statistics(date_flights)
        
        assert len(stats) == len(date_flights)
        assert set(stats.keys()) == set(date_flights.keys())
    
    @given(date_flights=date_flights_strategy())
    def test_average_price_calculation(self, date_flights):
        """Average price should be correctly calculated."""
        stats = DateOptimizer.calculate_date_statistics(date_flights)
        
        for date, flights in date_flights.items():
            stat = stats[date]
            
            if flights:
                prices = [f.get("price", 0) for f in flights]
                expected_avg = sum(prices) / len(prices)
                assert abs(stat["average_price"] - expected_avg) < 0.01
            else:
                assert stat["average_price"] == 0
    
    @given(date_flights=date_flights_strategy())
    def test_min_max_prices_correct(self, date_flights):
        """Min and max prices should be correct."""
        stats = DateOptimizer.calculate_date_statistics(date_flights)
        
        for date, flights in date_flights.items():
            stat = stats[date]
            
            if flights:
                prices = [f.get("price", 0) for f in flights]
                # Account for rounding to 2 decimal places
                assert abs(stat["min_price"] - min(prices)) < 0.01
                assert abs(stat["max_price"] - max(prices)) < 0.01


class TestOffPeakDateIdentification:
    """Test Property 7: Off-Peak Date Identification."""
    
    @given(date_flights=date_flights_strategy())
    def test_off_peak_has_lowest_average_price(self, date_flights):
        """
        Off-peak date should have average price ≤ all other dates.
        """
        stats = DateOptimizer.calculate_date_statistics(date_flights)
        off_peak = DateOptimizer.identify_off_peak_date(stats)
        
        if off_peak:
            off_peak_price = off_peak.get("average_price", 0)
            
            for stat in stats.values():
                if stat.get("average_price", 0) > 0:
                    assert off_peak_price <= stat.get("average_price", 0)
    
    def test_off_peak_empty_stats(self):
        """Off-peak should return None for empty stats."""
        result = DateOptimizer.identify_off_peak_date({})
        assert result is None


class TestPeakPriceDateIdentification:
    """Test Property 8: Peak Price Date Identification."""
    
    @given(date_flights=date_flights_strategy())
    def test_peak_has_highest_average_price(self, date_flights):
        """
        Peak price date should have average price ≥ all other dates.
        """
        stats = DateOptimizer.calculate_date_statistics(date_flights)
        peak = DateOptimizer.identify_peak_price_date(stats)
        
        if peak:
            peak_price = peak.get("average_price", 0)
            
            for stat in stats.values():
                if stat.get("average_price", 0) > 0:
                    assert peak_price >= stat.get("average_price", 0)
    
    def test_peak_empty_stats(self):
        """Peak should return None for empty stats."""
        result = DateOptimizer.identify_peak_price_date({})
        assert result is None


class TestSavingsPotentialCalculation:
    """Test Property 9: Savings Potential Calculation Accuracy."""
    
    @given(
        date_price=st.floats(min_value=50, max_value=1000),
        reference_price=st.floats(min_value=100, max_value=1000)
    )
    def test_savings_calculation_accuracy(self, date_price, reference_price):
        """
        Savings percentage should equal ((reference - date) / reference) * 100.
        """
        savings = DateOptimizer.calculate_savings_potential(date_price, reference_price)
        
        expected = ((reference_price - date_price) / reference_price) * 100
        assert abs(savings - expected) < 0.01
    
    def test_savings_zero_reference(self):
        """Savings should be 0 when reference price is 0."""
        result = DateOptimizer.calculate_savings_potential(100, 0)
        assert result == 0


class TestTopRecommendationsAccuracy:
    """Test Property 10: Top 3 Recommendations Accuracy."""
    
    @given(date_flights=date_flights_strategy())
    def test_top_3_are_cheapest_dates(self, date_flights):
        """
        Top 3 recommended dates should be the 3 dates with lowest average prices.
        """
        stats = DateOptimizer.calculate_date_statistics(date_flights)
        recommendations = DateOptimizer.recommend_cost_effective_dates(stats, top_n=3)
        
        # Get all valid prices sorted
        valid_stats = [s for s in stats.values() if s.get("average_price", 0) > 0]
        valid_stats.sort(key=lambda s: s.get("average_price", 0))
        
        # Verify recommendations match top 3 cheapest
        for i, rec in enumerate(recommendations):
            if i < len(valid_stats):
                assert rec["average_price"] == valid_stats[i]["average_price"]
    
    def test_recommendations_count(self):
        """Should return at most top_n recommendations."""
        stats = {
            "2024-06-15": {"average_price": 300, "day_of_week": "Friday", "flight_count": 5},
            "2024-06-16": {"average_price": 250, "day_of_week": "Saturday", "flight_count": 5},
            "2024-06-17": {"average_price": 400, "day_of_week": "Sunday", "flight_count": 5}
        }
        
        recommendations = DateOptimizer.recommend_cost_effective_dates(stats, top_n=2)
        assert len(recommendations) <= 2


class TestPriceTrendAnalysis:
    """Test price trend identification."""
    
    def test_increasing_trend(self):
        """Should identify increasing trend."""
        stats = {
            "2024-06-15": {"average_price": 200, "day_of_week": "Friday"},
            "2024-06-16": {"average_price": 250, "day_of_week": "Saturday"},
            "2024-06-17": {"average_price": 300, "day_of_week": "Sunday"},
            "2024-06-18": {"average_price": 350, "day_of_week": "Monday"}
        }
        
        trend = DateOptimizer.identify_price_trends(stats)
        assert trend == "increasing"
    
    def test_decreasing_trend(self):
        """Should identify decreasing trend."""
        stats = {
            "2024-06-15": {"average_price": 400, "day_of_week": "Friday"},
            "2024-06-16": {"average_price": 350, "day_of_week": "Saturday"},
            "2024-06-17": {"average_price": 300, "day_of_week": "Sunday"},
            "2024-06-18": {"average_price": 250, "day_of_week": "Monday"}
        }
        
        trend = DateOptimizer.identify_price_trends(stats)
        assert trend == "decreasing"
    
    def test_stable_trend(self):
        """Should identify stable trend."""
        stats = {
            "2024-06-15": {"average_price": 300, "day_of_week": "Friday"},
            "2024-06-16": {"average_price": 305, "day_of_week": "Saturday"},
            "2024-06-17": {"average_price": 302, "day_of_week": "Sunday"},
            "2024-06-18": {"average_price": 301, "day_of_week": "Monday"}
        }
        
        trend = DateOptimizer.identify_price_trends(stats)
        assert trend == "stable"


class TestDayOfWeekCalculation:
    """Test day of week calculation."""
    
    def test_day_of_week_calculation(self):
        """Should correctly calculate day of week."""
        # 2024-06-15 is a Saturday
        result = DateOptimizer._get_day_of_week("2024-06-15")
        assert result == "Saturday"
        
        # 2024-06-17 is a Monday
        result = DateOptimizer._get_day_of_week("2024-06-17")
        assert result == "Monday"
    
    def test_invalid_date_format(self):
        """Should handle invalid date format."""
        result = DateOptimizer._get_day_of_week("invalid")
        assert result == "Unknown"


class TestWithHighIterations:
    """Run tests with 100+ iterations for robustness."""
    
    @given(date_flights=date_flights_strategy())
    @settings(max_examples=100)
    def test_statistics_consistency(self, date_flights):
        """Statistics should be consistent across multiple calls."""
        stats1 = DateOptimizer.calculate_date_statistics(date_flights)
        stats2 = DateOptimizer.calculate_date_statistics(date_flights)
        
        for date in stats1.keys():
            assert stats1[date]["average_price"] == stats2[date]["average_price"]
            assert stats1[date]["min_price"] == stats2[date]["min_price"]
            assert stats1[date]["max_price"] == stats2[date]["max_price"]
