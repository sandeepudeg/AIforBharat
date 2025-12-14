"""
Correlation Calculator module for Weather & Pollen Dashboard.

This module provides functionality to calculate statistical correlations between
weather factors and pollen levels, classify correlation strength, and provide
explanations for the relationships.

Key responsibilities:
- Calculate Pearson correlation coefficients
- Calculate correlations for all weather factors vs pollen types
- Classify correlation strength
- Provide explanations for correlations
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class CorrelationCalculatorError(Exception):
    """Base exception for correlation calculator errors."""
    pass


class CorrelationCalculator:
    """
    Calculator for weather-pollen correlations.
    
    This class provides methods to:
    - Calculate Pearson correlation coefficients
    - Calculate correlations between all weather factors and pollen types
    - Classify correlation strength
    - Generate explanations for correlations
    """
    
    # Weather factors to analyze
    WEATHER_FACTORS = [
        'temperature',
        'humidity',
        'wind_speed',
        'pressure',
        'precipitation',
        'uv_index'
    ]
    
    # Pollen types to analyze
    POLLEN_TYPES = [
        'grass',
        'tree',
        'weed',
        'ragweed',
        'mold'
    ]
    
    # Correlation strength thresholds
    CORRELATION_THRESHOLDS = {
        'very_strong': 0.8,
        'strong': 0.6,
        'moderate': 0.4,
        'weak': 0.2,
        'very_weak': 0.0
    }
    
    # Explanations for correlations
    CORRELATION_EXPLANATIONS = {
        ('temperature', 'grass'): "Higher temperatures increase grass pollen production and release during growing season",
        ('temperature', 'tree'): "Temperature fluctuations trigger tree pollen release during spring",
        ('temperature', 'weed'): "Warm temperatures accelerate weed pollen production and dispersal",
        ('temperature', 'ragweed'): "Higher temperatures extend ragweed pollen season and increase production",
        ('temperature', 'mold'): "Warm, humid conditions promote mold spore growth and release",
        
        ('humidity', 'grass'): "High humidity can suppress grass pollen release but increases mold growth",
        ('humidity', 'tree'): "Moderate humidity levels favor tree pollen dispersal",
        ('humidity', 'weed'): "High humidity reduces weed pollen dispersal but increases mold",
        ('humidity', 'ragweed'): "Humidity affects ragweed pollen release and dispersal patterns",
        ('humidity', 'mold'): "High humidity significantly increases mold spore production and release",
        
        ('wind_speed', 'grass'): "Higher wind speeds increase grass pollen dispersal and airborne concentration",
        ('wind_speed', 'tree'): "Wind is essential for tree pollen dispersal; higher winds increase airborne pollen",
        ('wind_speed', 'weed'): "Strong winds dramatically increase weed pollen dispersal",
        ('wind_speed', 'ragweed'): "Wind is the primary dispersal mechanism for ragweed pollen",
        ('wind_speed', 'mold'): "Wind increases mold spore dispersal and airborne concentration",
        
        ('pressure', 'grass'): "Low pressure systems can trigger grass pollen release",
        ('pressure', 'tree'): "Pressure changes can stimulate tree pollen release",
        ('pressure', 'weed'): "Low atmospheric pressure increases weed pollen release",
        ('pressure', 'ragweed'): "Pressure drops trigger ragweed pollen release",
        ('pressure', 'mold'): "Low pressure systems increase mold spore release",
        
        ('precipitation', 'grass'): "Rain washes pollen from air but increases moisture for future growth",
        ('precipitation', 'tree'): "Rain temporarily reduces airborne tree pollen",
        ('precipitation', 'weed'): "Precipitation reduces airborne weed pollen but increases soil moisture",
        ('precipitation', 'ragweed'): "Rain temporarily clears ragweed pollen from air",
        ('precipitation', 'mold'): "Rain increases moisture, promoting mold growth and spore release",
        
        ('uv_index', 'grass'): "High UV index indicates sunny conditions favorable for pollen dispersal",
        ('uv_index', 'tree'): "Sunny conditions (high UV) favor tree pollen dispersal",
        ('uv_index', 'weed'): "High UV index correlates with sunny, dry conditions favoring pollen dispersal",
        ('uv_index', 'ragweed'): "Sunny conditions increase ragweed pollen production and dispersal",
        ('uv_index', 'mold'): "UV radiation can affect mold spore viability and dispersal"
    }
    
    def __init__(self):
        """Initialize the CorrelationCalculator."""
        logger.info("CorrelationCalculator initialized")
    
    def calculate_pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """
        Calculate Pearson correlation coefficient between two variables.
        
        The Pearson correlation coefficient measures the linear relationship
        between two variables, ranging from -1 (perfect negative correlation)
        to +1 (perfect positive correlation), with 0 indicating no correlation.
        
        Args:
            x (List[float]): First variable values
            y (List[float]): Second variable values
        
        Returns:
            float: Pearson correlation coefficient between -1 and +1
        
        Raises:
            CorrelationCalculatorError: If inputs are invalid or calculation fails
        
        Example:
            >>> calc = CorrelationCalculator()
            >>> x = [1, 2, 3, 4, 5]
            >>> y = [2, 4, 6, 8, 10]
            >>> corr = calc.calculate_pearson_correlation(x, y)
            >>> print(corr)  # Output: 1.0 (perfect positive correlation)
        """
        logger.debug(f"Calculating Pearson correlation for {len(x)} data points")
        
        try:
            # Validate inputs
            if not x or not y:
                raise CorrelationCalculatorError("Input lists cannot be empty")
            
            if len(x) != len(y):
                raise CorrelationCalculatorError("Input lists must have the same length")
            
            if len(x) < 2:
                raise CorrelationCalculatorError("At least 2 data points required for correlation")
            
            # Convert to numpy arrays
            x_arr = np.array(x, dtype=float)
            y_arr = np.array(y, dtype=float)
            
            # Remove NaN values
            mask = ~(np.isnan(x_arr) | np.isnan(y_arr))
            x_clean = x_arr[mask]
            y_clean = y_arr[mask]
            
            # Check if we have enough data after cleaning
            if len(x_clean) < 2:
                logger.warning("Insufficient data points after removing NaN values")
                return 0.0
            
            # Calculate correlation
            correlation = np.corrcoef(x_clean, y_clean)[0, 1]
            
            # Handle NaN result (e.g., when one variable has no variance)
            if np.isnan(correlation):
                logger.warning("Correlation calculation resulted in NaN")
                return 0.0
            
            # Ensure result is within [-1, 1]
            correlation = np.clip(correlation, -1.0, 1.0)
            
            logger.debug(f"Calculated correlation: {correlation}")
            return float(correlation)
        
        except (ValueError, TypeError) as e:
            error_msg = f"Error calculating Pearson correlation: {str(e)}"
            logger.error(error_msg)
            raise CorrelationCalculatorError(error_msg) from e
    
    def calculate_all_correlations(
        self,
        weather_data: List[Dict[str, Any]],
        pollen_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate correlations between all weather factors and pollen types.
        
        Args:
            weather_data (List[Dict[str, Any]]): List of weather data points with
                                                 temperature, humidity, wind_speed, etc.
            pollen_data (List[Dict[str, Any]]): List of pollen data points with
                                                pollen_types containing concentrations
        
        Returns:
            List[Dict[str, Any]]: List of correlation results with coefficients,
                                  strength classifications, and explanations
        
        Raises:
            CorrelationCalculatorError: If data is invalid or calculation fails
        
        Example response:
            [
                {
                    "weather_factor": "temperature",
                    "pollen_type": "grass",
                    "correlation_coefficient": 0.78,
                    "strength": "Strong Positive",
                    "explanation": "Higher temperatures increase grass pollen production..."
                },
                ...
            ]
        """
        logger.info(f"Calculating correlations for {len(weather_data)} weather and {len(pollen_data)} pollen data points")
        
        try:
            # Validate inputs
            if not weather_data or not pollen_data:
                raise CorrelationCalculatorError("Weather and pollen data cannot be empty")
            
            if len(weather_data) != len(pollen_data):
                raise CorrelationCalculatorError("Weather and pollen data must have the same length")
            
            # Extract weather factor values
            weather_values = {}
            for factor in self.WEATHER_FACTORS:
                values = []
                for data_point in weather_data:
                    value = data_point.get(factor)
                    values.append(value if value is not None else np.nan)
                weather_values[factor] = values
            
            # Extract pollen concentration values
            pollen_values = {}
            for pollen_type in self.POLLEN_TYPES:
                values = []
                for data_point in pollen_data:
                    pollen_types = data_point.get('pollen_types', {})
                    pollen_info = pollen_types.get(pollen_type, {})
                    concentration = pollen_info.get('concentration')
                    values.append(concentration if concentration is not None else np.nan)
                pollen_values[pollen_type] = values
            
            # Calculate correlations
            correlations = []
            for weather_factor in self.WEATHER_FACTORS:
                for pollen_type in self.POLLEN_TYPES:
                    try:
                        coefficient = self.calculate_pearson_correlation(
                            weather_values[weather_factor],
                            pollen_values[pollen_type]
                        )
                        
                        strength = self.get_correlation_strength(coefficient)
                        explanation = self.get_correlation_explanation(weather_factor, pollen_type)
                        
                        correlations.append({
                            'weather_factor': weather_factor,
                            'pollen_type': pollen_type,
                            'correlation_coefficient': round(coefficient, 3),
                            'strength': strength,
                            'explanation': explanation
                        })
                    
                    except CorrelationCalculatorError as e:
                        logger.warning(f"Failed to calculate correlation for {weather_factor} vs {pollen_type}: {e}")
                        continue
            
            logger.info(f"Successfully calculated {len(correlations)} correlations")
            return correlations
        
        except (ValueError, TypeError, KeyError) as e:
            error_msg = f"Error calculating all correlations: {str(e)}"
            logger.error(error_msg)
            raise CorrelationCalculatorError(error_msg) from e
    
    def get_correlation_strength(self, coefficient: float) -> str:
        """
        Classify correlation strength based on coefficient value.
        
        Classification:
        - Very Strong: |r| >= 0.8
        - Strong: 0.6 <= |r| < 0.8
        - Moderate: 0.4 <= |r| < 0.6
        - Weak: 0.2 <= |r| < 0.4
        - Very Weak: |r| < 0.2
        
        Direction:
        - Positive: r > 0
        - Negative: r < 0
        - Neutral: r = 0
        
        Args:
            coefficient (float): Pearson correlation coefficient
        
        Returns:
            str: Strength classification with direction (e.g., "Strong Positive")
        
        Raises:
            CorrelationCalculatorError: If coefficient is outside [-1, 1]
        
        Example:
            >>> calc = CorrelationCalculator()
            >>> strength = calc.get_correlation_strength(0.85)
            >>> print(strength)  # Output: "Very Strong Positive"
        """
        logger.debug(f"Classifying correlation strength for coefficient: {coefficient}")
        
        try:
            # Validate coefficient
            if coefficient < -1 or coefficient > 1:
                raise CorrelationCalculatorError(f"Coefficient must be between -1 and 1, got {coefficient}")
            
            # Determine direction
            if coefficient > 0:
                direction = "Positive"
            elif coefficient < 0:
                direction = "Negative"
            else:
                direction = "Neutral"
            
            # Determine strength
            abs_coeff = abs(coefficient)
            
            if abs_coeff >= self.CORRELATION_THRESHOLDS['very_strong']:
                strength = "Very Strong"
            elif abs_coeff >= self.CORRELATION_THRESHOLDS['strong']:
                strength = "Strong"
            elif abs_coeff >= self.CORRELATION_THRESHOLDS['moderate']:
                strength = "Moderate"
            elif abs_coeff >= self.CORRELATION_THRESHOLDS['weak']:
                strength = "Weak"
            else:
                strength = "Very Weak"
            
            result = f"{strength} {direction}"
            logger.debug(f"Classified as: {result}")
            return result
        
        except (ValueError, TypeError) as e:
            error_msg = f"Error classifying correlation strength: {str(e)}"
            logger.error(error_msg)
            raise CorrelationCalculatorError(error_msg) from e
    
    def get_correlation_explanation(self, weather_factor: str, pollen_type: str) -> str:
        """
        Get explanation for a weather-pollen correlation.
        
        Args:
            weather_factor (str): Weather factor name (e.g., 'temperature')
            pollen_type (str): Pollen type name (e.g., 'grass')
        
        Returns:
            str: Explanation of the correlation relationship
        
        Raises:
            CorrelationCalculatorError: If factor or pollen type is invalid
        
        Example:
            >>> calc = CorrelationCalculator()
            >>> explanation = calc.get_correlation_explanation('wind_speed', 'grass')
            >>> print(explanation)
            # Output: "Higher wind speeds increase grass pollen dispersal..."
        """
        logger.debug(f"Getting explanation for {weather_factor} vs {pollen_type}")
        
        try:
            # Validate inputs
            if weather_factor not in self.WEATHER_FACTORS:
                raise CorrelationCalculatorError(f"Invalid weather factor: {weather_factor}")
            
            if pollen_type not in self.POLLEN_TYPES:
                raise CorrelationCalculatorError(f"Invalid pollen type: {pollen_type}")
            
            # Get explanation
            key = (weather_factor, pollen_type)
            explanation = self.CORRELATION_EXPLANATIONS.get(
                key,
                f"Relationship between {weather_factor} and {pollen_type} pollen"
            )
            
            logger.debug(f"Retrieved explanation: {explanation[:50]}...")
            return explanation
        
        except (ValueError, TypeError) as e:
            error_msg = f"Error getting correlation explanation: {str(e)}"
            logger.error(error_msg)
            raise CorrelationCalculatorError(error_msg) from e
    
    def filter_correlations(
        self,
        correlations: List[Dict[str, Any]],
        weather_factors: Optional[List[str]] = None,
        pollen_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter correlations by weather factors and/or pollen types.
        
        Args:
            correlations (List[Dict[str, Any]]): List of correlation results
            weather_factors (Optional[List[str]]): List of weather factors to include
            pollen_types (Optional[List[str]]): List of pollen types to include
        
        Returns:
            List[Dict[str, Any]]: Filtered correlation results
        
        Raises:
            CorrelationCalculatorError: If inputs are invalid
        
        Example:
            >>> calc = CorrelationCalculator()
            >>> filtered = calc.filter_correlations(
            ...     correlations,
            ...     weather_factors=['temperature', 'humidity'],
            ...     pollen_types=['grass', 'tree']
            ... )
        """
        logger.info(f"Filtering {len(correlations)} correlations")
        
        try:
            if not correlations:
                return []
            
            filtered = correlations
            
            # Filter by weather factors
            if weather_factors:
                filtered = [
                    c for c in filtered
                    if c.get('weather_factor') in weather_factors
                ]
            
            # Filter by pollen types
            if pollen_types:
                filtered = [
                    c for c in filtered
                    if c.get('pollen_type') in pollen_types
                ]
            
            logger.info(f"Filtered to {len(filtered)} correlations")
            return filtered
        
        except (ValueError, TypeError) as e:
            error_msg = f"Error filtering correlations: {str(e)}"
            logger.error(error_msg)
            raise CorrelationCalculatorError(error_msg) from e
    
    def sort_correlations_by_strength(
        self,
        correlations: List[Dict[str, Any]],
        descending: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Sort correlations by absolute coefficient value (strength).
        
        Args:
            correlations (List[Dict[str, Any]]): List of correlation results
            descending (bool): If True, sort strongest first; if False, weakest first
        
        Returns:
            List[Dict[str, Any]]: Sorted correlation results
        
        Example:
            >>> calc = CorrelationCalculator()
            >>> sorted_corr = calc.sort_correlations_by_strength(correlations)
        """
        logger.info(f"Sorting {len(correlations)} correlations by strength")
        
        try:
            sorted_corr = sorted(
                correlations,
                key=lambda x: abs(x.get('correlation_coefficient', 0)),
                reverse=descending
            )
            
            logger.info(f"Sorted {len(sorted_corr)} correlations")
            return sorted_corr
        
        except (ValueError, TypeError, KeyError) as e:
            error_msg = f"Error sorting correlations: {str(e)}"
            logger.error(error_msg)
            raise CorrelationCalculatorError(error_msg) from e
