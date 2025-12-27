#!/usr/bin/env python3
"""
Property-based tests for Cost_Analyzer component.

Tests validate correctness properties for cost analysis functionality.
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cost_analyzer import CostAnalyzer, PriceTier


# Strategies for generating test data
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


class TestPriceTierCategorization:
    """Test Property 2: Price Tier Categorization Accuracy."""
    
    @given(price=st.floats(min_value=0, max_value=3000))
    def test_price_tier_categorization_accuracy(self, price):
        """
        For any flight with price P, it should be categorized correctly.
        
        Budget: P < $300
        Economy: $300 ≤ P ≤ $600
        Premium: P > $600
        """
        flight = {"price": price, "duration_minutes": 300}
        categorized = CostAnalyzer.categorize_by_price_tier([flight])
        
        assert len(categorized) == 1
        tier = categorized[0]["price_tier"]
        
        if price < 300:
            assert tier == PriceTier.BUDGET.value
        elif price <= 600:
            assert tier == PriceTier.ECONOMY.value
        else:
            assert tier == PriceTier.PREMIUM.value
    
    @given(flights=flights_list_strategy())
    def test_all_flights_categorized(self, flights):
        """All flights should be categorized into a valid tier."""
        categorized = CostAnalyzer.categorize_by_price_tier(flights)
        
        assert len(categorized) == len(flights)
        valid_tiers = {PriceTier.BUDGET.value, PriceTier.ECONOMY.value, PriceTier.PREMIUM.value}
        
        for flight in categorized:
            assert flight["price_tier"] in valid_tiers


class TestCostEffectivenessScore:
    """Test Property 3: Cost Effectiveness Score Calculation."""
    
    @given(
        price1=st.floats(min_value=50, max_value=500),
        duration1=st.integers(min_value=30, max_value=600),
        price2=st.floats(min_value=50, max_value=500),
        duration2=st.integers(min_value=30, max_value=600)
    )
    def test_cost_effectiveness_comparison(self, price1, duration1, price2, duration2):
        """
        For any two flights, if F1 has lower score than F2,
        then F1.price/F1.duration < F2.price/F2.duration.
        """
        flight1 = {"price": price1, "duration_minutes": duration1}
        flight2 = {"price": price2, "duration_minutes": duration2}
        
        score1 = CostAnalyzer.calculate_cost_effectiveness_score(flight1)
        score2 = CostAnalyzer.calculate_cost_effectiveness_score(flight2)
        
        # Verify calculation
        expected_score1 = price1 / (duration1 / 60)
        expected_score2 = price2 / (duration2 / 60)
        
        assert abs(score1 - expected_score1) < 0.01
        assert abs(score2 - expected_score2) < 0.01
        
        # Verify comparison
        if score1 < score2:
            assert (price1 / duration1) < (price2 / duration2)
    
    @given(flights=flights_list_strategy())
    def test_cost_effectiveness_scores_positive(self, flights):
        """All cost effectiveness scores should be positive."""
        for flight in flights:
            score = CostAnalyzer.calculate_cost_effectiveness_score(flight)
            assert score > 0


class TestCheapestFlightIdentification:
    """Test Property 4: Cheapest Flight Identification."""
    
    @given(flights=flights_list_strategy())
    def test_cheapest_flight_has_minimum_price(self, flights):
        """
        The cheapest flight should have price ≤ all other flights.
        """
        cheapest = CostAnalyzer.identify_cheapest_flight(flights)
        
        assert cheapest is not None
        cheapest_price = cheapest.get("price", 0)
        
        for flight in flights:
            assert cheapest_price <= flight.get("price", 0)
    
    def test_cheapest_flight_empty_list(self):
        """Cheapest flight should return None for empty list."""
        result = CostAnalyzer.identify_cheapest_flight([])
        assert result is None


class TestBestValueFlightIdentification:
    """Test Property 5: Best Value Flight Identification."""
    
    @given(flights=flights_list_strategy())
    def test_best_value_flight_has_lowest_score(self, flights):
        """
        The best value flight should have lowest cost effectiveness score.
        """
        best_value = CostAnalyzer.identify_best_value_flight(flights)
        
        assert best_value is not None
        best_score = CostAnalyzer.calculate_cost_effectiveness_score(best_value)
        
        for flight in flights:
            score = CostAnalyzer.calculate_cost_effectiveness_score(flight)
            assert best_score <= score
    
    def test_best_value_flight_empty_list(self):
        """Best value flight should return None for empty list."""
        result = CostAnalyzer.identify_best_value_flight([])
        assert result is None


class TestAveragePriceCalculation:
    """Test average price calculation."""
    
    @given(flights=flights_list_strategy())
    def test_average_price_calculation(self, flights):
        """Average price should be sum of prices divided by count."""
        avg = CostAnalyzer.calculate_average_price(flights)
        
        prices = [f.get("price", 0) for f in flights]
        expected_avg = sum(prices) / len(prices)
        
        assert abs(avg - expected_avg) < 0.01
    
    def test_average_price_empty_list(self):
        """Average price of empty list should be 0."""
        result = CostAnalyzer.calculate_average_price([])
        assert result == 0


class TestCostMetricsAddition:
    """Test adding cost metrics to flights."""
    
    @given(flights=flights_list_strategy())
    def test_all_metrics_added(self, flights):
        """All required metrics should be added to each flight."""
        result = CostAnalyzer.add_cost_metrics(flights)
        
        assert len(result) == len(flights)
        
        required_fields = {
            "price_tier",
            "cost_effectiveness_score",
            "savings_vs_average",
            "is_great_deal",
            "is_exceptional_savings",
            "is_cheapest",
            "is_best_value",
            "deal_indicator"
        }
        
        for flight in result:
            for field in required_fields:
                assert field in flight
    
    @given(flights=flights_list_strategy())
    def test_exactly_one_cheapest(self, flights):
        """Exactly one flight should be marked as cheapest."""
        result = CostAnalyzer.add_cost_metrics(flights)
        
        cheapest_count = sum(1 for f in result if f.get("is_cheapest", False))
        assert cheapest_count == 1
    
    @given(flights=flights_list_strategy())
    def test_exactly_one_best_value(self, flights):
        """Exactly one flight should be marked as best value."""
        result = CostAnalyzer.add_cost_metrics(flights)
        
        best_value_count = sum(1 for f in result if f.get("is_best_value", False))
        assert best_value_count == 1


class TestDealFlagging:
    """Test Property 14 & 15: Deal Flagging Thresholds."""
    
    @given(savings_pct=st.floats(min_value=-50, max_value=50))
    def test_great_deal_threshold(self, savings_pct):
        """
        Flight should be flagged as Great Deal if savings > 20%.
        """
        avg_price = 500
        flight_price = avg_price * (1 - savings_pct / 100)
        
        flight = {"price": flight_price, "duration_minutes": 300}
        flights = [flight]
        
        result = CostAnalyzer.add_cost_metrics(flights, average_price=avg_price)
        
        is_great_deal = result[0].get("is_great_deal", False)
        
        if savings_pct > 20:
            assert is_great_deal
        else:
            assert not is_great_deal
    
    @given(savings_pct=st.floats(min_value=-50, max_value=50))
    def test_exceptional_savings_threshold(self, savings_pct):
        """
        Flight should be flagged as Exceptional Savings if savings > 30%.
        """
        avg_price = 500
        flight_price = avg_price * (1 - savings_pct / 100)
        
        flight = {"price": flight_price, "duration_minutes": 300}
        flights = [flight]
        
        result = CostAnalyzer.add_cost_metrics(flights, average_price=avg_price)
        
        is_exceptional = result[0].get("is_exceptional_savings", False)
        
        if savings_pct > 30:
            assert is_exceptional
        else:
            assert not is_exceptional


class TestWithHighIterations:
    """Run tests with 100+ iterations for robustness."""
    
    @given(flights=flights_list_strategy())
    @settings(max_examples=100)
    def test_categorization_consistency(self, flights):
        """Categorization should be consistent across multiple calls."""
        result1 = CostAnalyzer.categorize_by_price_tier(flights)
        result2 = CostAnalyzer.categorize_by_price_tier(flights)
        
        for f1, f2 in zip(result1, result2):
            assert f1["price_tier"] == f2["price_tier"]
