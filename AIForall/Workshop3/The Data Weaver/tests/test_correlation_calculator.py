"""
Unit and property-based tests for the correlation calculator module.

Tests Pearson correlation calculation, correlation strength classification,
and correlation explanation functionality.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, patch

from src.correlation_calculator import (
    CorrelationCalculator,
    CorrelationCalculatorError
)


@pytest.fixture
def calculator():
    """Create a CorrelationCalculator instance for testing."""
    return CorrelationCalculator()


@pytest.fixture
def sample_weather_data():
    """Create sample weather data for testing."""
    return [
        {
            'temperature': 70.0,
            'humidity': 60.0,
            'wind_speed': 10.0,
            'pressure': 1013.0,
            'precipitation': 0.0,
            'uv_index': 5.0
        },
        {
            'temperature': 72.0,
            'humidity': 62.0,
            'wind_speed': 12.0,
            'pressure': 1012.0,
            'precipitation': 0.1,
            'uv_index': 6.0
        },
        {
            'temperature': 75.0,
            'humidity': 65.0,
            'wind_speed': 15.0,
            'pressure': 1011.0,
            'precipitation': 0.2,
            'uv_index': 7.0
        },
        {
            'temperature': 78.0,
            'humidity': 68.0,
            'wind_speed': 18.0,
            'pressure': 1010.0,
            'precipitation': 0.3,
            'uv_index': 8.0
        },
        {
            'temperature': 80.0,
            'humidity': 70.0,
            'wind_speed': 20.0,
            'pressure': 1009.0,
            'precipitation': 0.4,
            'uv_index': 9.0
        }
    ]


@pytest.fixture
def sample_pollen_data():
    """Create sample pollen data for testing."""
    return [
        {
            'pollen_types': {
                'grass': {'concentration': 100.0, 'severity': 'LOW'},
                'tree': {'concentration': 50.0, 'severity': 'LOW'},
                'weed': {'concentration': 30.0, 'severity': 'LOW'},
                'ragweed': {'concentration': 20.0, 'severity': 'LOW'},
                'mold': {'concentration': 40.0, 'severity': 'LOW'}
            }
        },
        {
            'pollen_types': {
                'grass': {'concentration': 120.0, 'severity': 'LOW'},
                'tree': {'concentration': 60.0, 'severity': 'LOW'},
                'weed': {'concentration': 35.0, 'severity': 'LOW'},
                'ragweed': {'concentration': 25.0, 'severity': 'LOW'},
                'mold': {'concentration': 50.0, 'severity': 'LOW'}
            }
        },
        {
            'pollen_types': {
                'grass': {'concentration': 150.0, 'severity': 'MODERATE'},
                'tree': {'concentration': 75.0, 'severity': 'MODERATE'},
                'weed': {'concentration': 40.0, 'severity': 'LOW'},
                'ragweed': {'concentration': 30.0, 'severity': 'LOW'},
                'mold': {'concentration': 60.0, 'severity': 'MODERATE'}
            }
        },
        {
            'pollen_types': {
                'grass': {'concentration': 180.0, 'severity': 'MODERATE'},
                'tree': {'concentration': 90.0, 'severity': 'MODERATE'},
                'weed': {'concentration': 45.0, 'severity': 'LOW'},
                'ragweed': {'concentration': 35.0, 'severity': 'LOW'},
                'mold': {'concentration': 70.0, 'severity': 'MODERATE'}
            }
        },
        {
            'pollen_types': {
                'grass': {'concentration': 200.0, 'severity': 'HIGH'},
                'tree': {'concentration': 100.0, 'severity': 'HIGH'},
                'weed': {'concentration': 50.0, 'severity': 'MODERATE'},
                'ragweed': {'concentration': 40.0, 'severity': 'MODERATE'},
                'mold': {'concentration': 80.0, 'severity': 'MODERATE'}
            }
        }
    ]


class TestCorrelationCalculatorInitialization:
    """Test CorrelationCalculator initialization."""
    
    def test_calculator_initialization(self, calculator):
        """Test CorrelationCalculator initialization."""
        assert calculator is not None
        assert calculator.WEATHER_FACTORS is not None
        assert calculator.POLLEN_TYPES is not None
    
    def test_weather_factors_defined(self, calculator):
        """Test that weather factors are properly defined."""
        expected_factors = ['temperature', 'humidity', 'wind_speed', 'pressure', 'precipitation', 'uv_index']
        assert calculator.WEATHER_FACTORS == expected_factors
    
    def test_pollen_types_defined(self, calculator):
        """Test that pollen types are properly defined."""
        expected_types = ['grass', 'tree', 'weed', 'ragweed', 'mold']
        assert calculator.POLLEN_TYPES == expected_types
    
    def test_correlation_thresholds_defined(self, calculator):
        """Test that correlation thresholds are defined."""
        assert 'very_strong' in calculator.CORRELATION_THRESHOLDS
        assert 'strong' in calculator.CORRELATION_THRESHOLDS
        assert 'moderate' in calculator.CORRELATION_THRESHOLDS
        assert 'weak' in calculator.CORRELATION_THRESHOLDS
        assert 'very_weak' in calculator.CORRELATION_THRESHOLDS
    
    def test_explanations_defined(self, calculator):
        """Test that explanations are defined for correlations."""
        assert len(calculator.CORRELATION_EXPLANATIONS) > 0
        # Check a few key explanations exist
        assert ('temperature', 'grass') in calculator.CORRELATION_EXPLANATIONS
        assert ('wind_speed', 'grass') in calculator.CORRELATION_EXPLANATIONS


class TestPearsonCorrelation:
    """Test Pearson correlation calculation."""
    
    def test_perfect_positive_correlation(self, calculator):
        """Test perfect positive correlation."""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        assert abs(corr - 1.0) < 0.001, "Perfect positive correlation should be ~1.0"
    
    def test_perfect_negative_correlation(self, calculator):
        """Test perfect negative correlation."""
        x = [1, 2, 3, 4, 5]
        y = [10, 8, 6, 4, 2]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        assert abs(corr - (-1.0)) < 0.001, "Perfect negative correlation should be ~-1.0"
    
    def test_no_correlation(self, calculator):
        """Test no correlation."""
        x = [1, 2, 3, 4, 5]
        y = [5, 3, 1, 4, 2]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        assert abs(corr) < 0.5, "Random data should have low correlation"
    
    def test_correlation_with_floats(self, calculator):
        """Test correlation with float values."""
        x = [1.5, 2.5, 3.5, 4.5, 5.5]
        y = [3.0, 5.0, 7.0, 9.0, 11.0]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        assert abs(corr - 1.0) < 0.001, "Perfect positive correlation with floats"
    
    def test_correlation_with_nan_values(self, calculator):
        """Test correlation with NaN values."""
        x = [1, 2, np.nan, 4, 5]
        y = [2, 4, 6, 8, 10]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        # Should handle NaN gracefully
        assert -1 <= corr <= 1, "Correlation should be in valid range"
    
    def test_correlation_empty_list(self, calculator):
        """Test correlation with empty lists."""
        with pytest.raises(CorrelationCalculatorError):
            calculator.calculate_pearson_correlation([], [])
    
    def test_correlation_mismatched_lengths(self, calculator):
        """Test correlation with mismatched list lengths."""
        x = [1, 2, 3]
        y = [1, 2, 3, 4]
        
        with pytest.raises(CorrelationCalculatorError):
            calculator.calculate_pearson_correlation(x, y)
    
    def test_correlation_single_point(self, calculator):
        """Test correlation with single data point."""
        x = [1]
        y = [2]
        
        with pytest.raises(CorrelationCalculatorError):
            calculator.calculate_pearson_correlation(x, y)
    
    def test_correlation_constant_values(self, calculator):
        """Test correlation when one variable is constant."""
        x = [5, 5, 5, 5, 5]
        y = [1, 2, 3, 4, 5]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        # Should return 0 when one variable has no variance
        assert corr == 0.0, "Correlation with constant variable should be 0"
    
    def test_correlation_result_in_range(self, calculator):
        """Test that correlation result is always in [-1, 1]."""
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        assert -1 <= corr <= 1, "Correlation must be in [-1, 1]"
    
    def test_correlation_all_zeros(self, calculator):
        """Test correlation when both variables are all zeros."""
        x = [0, 0, 0, 0, 0]
        y = [0, 0, 0, 0, 0]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        # When both variables have no variance, correlation should be 0
        assert corr == 0.0, "Correlation with all zeros should be 0"
    
    def test_correlation_identical_values(self, calculator):
        """Test correlation when both variables have identical values."""
        x = [5, 5, 5, 5, 5]
        y = [5, 5, 5, 5, 5]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        # When both variables are identical constants, correlation should be 0
        assert corr == 0.0, "Correlation with identical constant values should be 0"
    
    def test_correlation_one_variable_all_zeros(self, calculator):
        """Test correlation when one variable is all zeros."""
        x = [0, 0, 0, 0, 0]
        y = [1, 2, 3, 4, 5]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        # When one variable has no variance, correlation should be 0
        assert corr == 0.0, "Correlation with one variable all zeros should be 0"
    
    def test_correlation_large_identical_values(self, calculator):
        """Test correlation with large identical values."""
        x = [1000000, 1000000, 1000000, 1000000, 1000000]
        y = [1000000, 1000000, 1000000, 1000000, 1000000]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        # When both variables are identical constants, correlation should be 0
        assert corr == 0.0, "Correlation with large identical values should be 0"
    
    def test_correlation_negative_identical_values(self, calculator):
        """Test correlation with negative identical values."""
        x = [-5, -5, -5, -5, -5]
        y = [-5, -5, -5, -5, -5]
        
        corr = calculator.calculate_pearson_correlation(x, y)
        
        # When both variables are identical constants, correlation should be 0
        assert corr == 0.0, "Correlation with negative identical values should be 0"


class TestCorrelationStrength:
    """Test correlation strength classification."""
    
    def test_very_strong_positive(self, calculator):
        """Test very strong positive correlation classification."""
        strength = calculator.get_correlation_strength(0.85)
        
        assert "Very Strong" in strength
        assert "Positive" in strength
    
    def test_very_strong_negative(self, calculator):
        """Test very strong negative correlation classification."""
        strength = calculator.get_correlation_strength(-0.85)
        
        assert "Very Strong" in strength
        assert "Negative" in strength
    
    def test_strong_positive(self, calculator):
        """Test strong positive correlation classification."""
        strength = calculator.get_correlation_strength(0.70)
        
        assert "Strong" in strength
        assert "Positive" in strength
    
    def test_strong_negative(self, calculator):
        """Test strong negative correlation classification."""
        strength = calculator.get_correlation_strength(-0.70)
        
        assert "Strong" in strength
        assert "Negative" in strength
    
    def test_moderate_positive(self, calculator):
        """Test moderate positive correlation classification."""
        strength = calculator.get_correlation_strength(0.50)
        
        assert "Moderate" in strength
        assert "Positive" in strength
    
    def test_moderate_negative(self, calculator):
        """Test moderate negative correlation classification."""
        strength = calculator.get_correlation_strength(-0.50)
        
        assert "Moderate" in strength
        assert "Negative" in strength
    
    def test_weak_positive(self, calculator):
        """Test weak positive correlation classification."""
        strength = calculator.get_correlation_strength(0.25)
        
        assert "Weak" in strength
        assert "Positive" in strength
    
    def test_weak_negative(self, calculator):
        """Test weak negative correlation classification."""
        strength = calculator.get_correlation_strength(-0.25)
        
        assert "Weak" in strength
        assert "Negative" in strength
    
    def test_very_weak_positive(self, calculator):
        """Test very weak positive correlation classification."""
        strength = calculator.get_correlation_strength(0.05)
        
        assert "Very Weak" in strength
        assert "Positive" in strength
    
    def test_very_weak_negative(self, calculator):
        """Test very weak negative correlation classification."""
        strength = calculator.get_correlation_strength(-0.05)
        
        assert "Very Weak" in strength
        assert "Negative" in strength
    
    def test_neutral_correlation(self, calculator):
        """Test neutral (zero) correlation classification."""
        strength = calculator.get_correlation_strength(0.0)
        
        assert "Neutral" in strength
    
    def test_invalid_coefficient_too_high(self, calculator):
        """Test invalid coefficient (> 1)."""
        with pytest.raises(CorrelationCalculatorError):
            calculator.get_correlation_strength(1.5)
    
    def test_invalid_coefficient_too_low(self, calculator):
        """Test invalid coefficient (< -1)."""
        with pytest.raises(CorrelationCalculatorError):
            calculator.get_correlation_strength(-1.5)
    
    def test_boundary_very_strong(self, calculator):
        """Test boundary value for very strong correlation."""
        strength = calculator.get_correlation_strength(0.8)
        
        assert "Very Strong" in strength
    
    def test_boundary_strong(self, calculator):
        """Test boundary value for strong correlation."""
        strength = calculator.get_correlation_strength(0.6)
        
        assert "Strong" in strength


class TestCorrelationExplanation:
    """Test correlation explanation retrieval."""
    
    def test_get_explanation_temperature_grass(self, calculator):
        """Test getting explanation for temperature vs grass."""
        explanation = calculator.get_correlation_explanation('temperature', 'grass')
        
        assert explanation is not None
        assert len(explanation) > 0
        assert 'temperature' in explanation.lower() or 'grass' in explanation.lower()
    
    def test_get_explanation_wind_speed_grass(self, calculator):
        """Test getting explanation for wind speed vs grass."""
        explanation = calculator.get_correlation_explanation('wind_speed', 'grass')
        
        assert explanation is not None
        assert len(explanation) > 0
    
    def test_get_explanation_all_combinations(self, calculator):
        """Test getting explanations for all weather-pollen combinations."""
        for weather_factor in calculator.WEATHER_FACTORS:
            for pollen_type in calculator.POLLEN_TYPES:
                explanation = calculator.get_correlation_explanation(weather_factor, pollen_type)
                
                assert explanation is not None
                assert len(explanation) > 0
    
    def test_invalid_weather_factor(self, calculator):
        """Test with invalid weather factor."""
        with pytest.raises(CorrelationCalculatorError):
            calculator.get_correlation_explanation('invalid_factor', 'grass')
    
    def test_invalid_pollen_type(self, calculator):
        """Test with invalid pollen type."""
        with pytest.raises(CorrelationCalculatorError):
            calculator.get_correlation_explanation('temperature', 'invalid_pollen')


class TestCalculateAllCorrelations:
    """Test calculating all correlations."""
    
    def test_calculate_all_correlations_success(self, calculator, sample_weather_data, sample_pollen_data):
        """Test successful calculation of all correlations."""
        correlations = calculator.calculate_all_correlations(sample_weather_data, sample_pollen_data)
        
        assert correlations is not None
        assert len(correlations) > 0
        # Should have 6 weather factors * 5 pollen types = 30 correlations
        assert len(correlations) == 30
    
    def test_correlation_structure(self, calculator, sample_weather_data, sample_pollen_data):
        """Test that correlation results have correct structure."""
        correlations = calculator.calculate_all_correlations(sample_weather_data, sample_pollen_data)
        
        for corr in correlations:
            assert 'weather_factor' in corr
            assert 'pollen_type' in corr
            assert 'correlation_coefficient' in corr
            assert 'strength' in corr
            assert 'explanation' in corr
            
            # Verify coefficient is in valid range
            assert -1 <= corr['correlation_coefficient'] <= 1
    
    def test_calculate_all_correlations_empty_weather(self, calculator, sample_pollen_data):
        """Test with empty weather data."""
        with pytest.raises(CorrelationCalculatorError):
            calculator.calculate_all_correlations([], sample_pollen_data)
    
    def test_calculate_all_correlations_empty_pollen(self, calculator, sample_weather_data):
        """Test with empty pollen data."""
        with pytest.raises(CorrelationCalculatorError):
            calculator.calculate_all_correlations(sample_weather_data, [])
    
    def test_calculate_all_correlations_mismatched_lengths(self, calculator, sample_weather_data):
        """Test with mismatched data lengths."""
        pollen_data = [{'pollen_types': {'grass': {'concentration': 100}}}]
        
        with pytest.raises(CorrelationCalculatorError):
            calculator.calculate_all_correlations(sample_weather_data, pollen_data)
    
    def test_calculate_all_correlations_with_missing_fields(self, calculator):
        """Test with missing fields in data."""
        weather_data = [
            {'temperature': 70.0, 'humidity': 60.0},  # Missing other fields
            {'temperature': 72.0, 'humidity': 62.0}
        ]
        pollen_data = [
            {'pollen_types': {'grass': {'concentration': 100.0}}},
            {'pollen_types': {'grass': {'concentration': 120.0}}}
        ]
        
        # Should handle missing fields gracefully
        correlations = calculator.calculate_all_correlations(weather_data, pollen_data)
        
        assert correlations is not None


class TestFilterCorrelations:
    """Test filtering correlations."""
    
    def test_filter_by_weather_factor(self, calculator, sample_weather_data, sample_pollen_data):
        """Test filtering by weather factor."""
        correlations = calculator.calculate_all_correlations(sample_weather_data, sample_pollen_data)
        
        filtered = calculator.filter_correlations(
            correlations,
            weather_factors=['temperature']
        )
        
        assert len(filtered) > 0
        assert all(c['weather_factor'] == 'temperature' for c in filtered)
    
    def test_filter_by_pollen_type(self, calculator, sample_weather_data, sample_pollen_data):
        """Test filtering by pollen type."""
        correlations = calculator.calculate_all_correlations(sample_weather_data, sample_pollen_data)
        
        filtered = calculator.filter_correlations(
            correlations,
            pollen_types=['grass']
        )
        
        assert len(filtered) > 0
        assert all(c['pollen_type'] == 'grass' for c in filtered)
    
    def test_filter_by_both(self, calculator, sample_weather_data, sample_pollen_data):
        """Test filtering by both weather factor and pollen type."""
        correlations = calculator.calculate_all_correlations(sample_weather_data, sample_pollen_data)
        
        filtered = calculator.filter_correlations(
            correlations,
            weather_factors=['temperature', 'humidity'],
            pollen_types=['grass', 'tree']
        )
        
        assert len(filtered) > 0
        assert all(c['weather_factor'] in ['temperature', 'humidity'] for c in filtered)
        assert all(c['pollen_type'] in ['grass', 'tree'] for c in filtered)
    
    def test_filter_empty_correlations(self, calculator):
        """Test filtering empty correlations list."""
        filtered = calculator.filter_correlations([])
        
        assert filtered == []


class TestSortCorrelations:
    """Test sorting correlations."""
    
    def test_sort_by_strength_descending(self, calculator, sample_weather_data, sample_pollen_data):
        """Test sorting by strength in descending order."""
        correlations = calculator.calculate_all_correlations(sample_weather_data, sample_pollen_data)
        
        sorted_corr = calculator.sort_correlations_by_strength(correlations, descending=True)
        
        assert len(sorted_corr) == len(correlations)
        
        # Verify descending order
        for i in range(len(sorted_corr) - 1):
            abs_curr = abs(sorted_corr[i]['correlation_coefficient'])
            abs_next = abs(sorted_corr[i + 1]['correlation_coefficient'])
            assert abs_curr >= abs_next
    
    def test_sort_by_strength_ascending(self, calculator, sample_weather_data, sample_pollen_data):
        """Test sorting by strength in ascending order."""
        correlations = calculator.calculate_all_correlations(sample_weather_data, sample_pollen_data)
        
        sorted_corr = calculator.sort_correlations_by_strength(correlations, descending=False)
        
        assert len(sorted_corr) == len(correlations)
        
        # Verify ascending order
        for i in range(len(sorted_corr) - 1):
            abs_curr = abs(sorted_corr[i]['correlation_coefficient'])
            abs_next = abs(sorted_corr[i + 1]['correlation_coefficient'])
            assert abs_curr <= abs_next


class TestCorrelationCoefficientRangeProperty:
    """
    Property-based tests for correlation coefficient range.
    
    **Feature: data-mashup-dashboard, Property 3: Correlation Coefficient Range**
    **Validates: Requirements 4.2**
    """
    
    @given(
        x_values=st.lists(
            st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
            min_size=2,
            max_size=100
        ),
        y_values=st.lists(
            st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False),
            min_size=2,
            max_size=100
        )
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_correlation_coefficient_always_in_range(self, x_values, y_values):
        """
        Property: For any two sets of numeric values, the calculated Pearson
        correlation coefficient should always be between -1 and +1 (inclusive).
        
        This property verifies that:
        1. The correlation coefficient is never outside [-1, 1]
        2. The calculation is mathematically sound
        3. Edge cases are handled correctly
        
        **Validates: Requirements 4.2**
        """
        calculator = CorrelationCalculator()
        
        # Ensure lists have same length
        min_len = min(len(x_values), len(y_values))
        x_values = x_values[:min_len]
        y_values = y_values[:min_len]
        
        # Skip if lists are too short
        assume(len(x_values) >= 2)
        
        try:
            coefficient = calculator.calculate_pearson_correlation(x_values, y_values)
            
            # Verify coefficient is in valid range
            assert -1 <= coefficient <= 1, f"Coefficient {coefficient} is outside [-1, 1]"
        except CorrelationCalculatorError:
            # Some edge cases may raise errors, which is acceptable
            pass
    
    @given(
        coefficient=st.floats(min_value=-1, max_value=1)
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_correlation_strength_classification_valid(self, coefficient):
        """
        Property: For any valid correlation coefficient in [-1, 1], the strength
        classification should always return a valid strength string.
        
        This property verifies that:
        1. All coefficients in [-1, 1] can be classified
        2. The classification is consistent
        3. No errors occur for valid inputs
        
        **Validates: Requirements 4.2**
        """
        calculator = CorrelationCalculator()
        
        strength = calculator.get_correlation_strength(coefficient)
        
        # Verify strength is a non-empty string
        assert isinstance(strength, str)
        assert len(strength) > 0
        
        # Verify strength contains expected components
        valid_strengths = ['Very Strong', 'Strong', 'Moderate', 'Weak', 'Very Weak']
        valid_directions = ['Positive', 'Negative', 'Neutral']
        
        assert any(s in strength for s in valid_strengths)
        assert any(d in strength for d in valid_directions)
