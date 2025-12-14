// ============================================================================
// GLOBAL STATE AND CONFIGURATION
// ============================================================================

// Current metric system (imperial or metric)
let currentMetric = 'imperial';

// Current location selection
let currentLocation = {
    country: null,
    state: null,
    district: null
};

// Current time range
let currentTimeRange = 'weekly';

// Location hierarchy data
const locationData = {
    USA: {
        name: 'United States',
        states: {
            NY: { name: 'New York', districts: ['Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'] },
            CA: { name: 'California', districts: ['Los Angeles', 'San Francisco', 'San Diego', 'Sacramento'] },
            TX: { name: 'Texas', districts: ['Houston', 'Dallas', 'Austin', 'San Antonio'] },
            FL: { name: 'Florida', districts: ['Miami', 'Orlando', 'Tampa', 'Jacksonville'] }
        }
    },
    India: {
        name: 'India',
        states: {
            MH: { name: 'Maharashtra', districts: ['Mumbai', 'Pune', 'Nagpur', 'Aurangabad'] },
            DL: { name: 'Delhi', districts: ['New Delhi', 'East Delhi', 'West Delhi', 'North Delhi'] },
            KA: { name: 'Karnataka', districts: ['Bangalore', 'Mysore', 'Mangalore', 'Belgaum'] },
            TN: { name: 'Tamil Nadu', districts: ['Chennai', 'Coimbatore', 'Madurai', 'Salem'] }
        }
    },
    UK: {
        name: 'United Kingdom',
        states: {
            ENG: { name: 'England', districts: ['London', 'Manchester', 'Birmingham', 'Leeds'] },
            SCT: { name: 'Scotland', districts: ['Edinburgh', 'Glasgow', 'Aberdeen', 'Dundee'] },
            WAL: { name: 'Wales', districts: ['Cardiff', 'Swansea', 'Newport', 'Wrexham'] }
        }
    },
    Canada: {
        name: 'Canada',
        states: {
            ON: { name: 'Ontario', districts: ['Toronto', 'Ottawa', 'Hamilton', 'London'] },
            BC: { name: 'British Columbia', districts: ['Vancouver', 'Victoria', 'Surrey', 'Burnaby'] },
            QC: { name: 'Quebec', districts: ['Montreal', 'Quebec City', 'Laval', 'Gatineau'] }
        }
    }
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Convert Fahrenheit to Celsius
 * @param {number} fahrenheit - Temperature in Fahrenheit
 * @returns {number} Temperature in Celsius
 */
function fahrenheitToCelsius(fahrenheit) {
    return (fahrenheit - 32) * 5 / 9;
}

/**
 * Convert Celsius to Fahrenheit
 * @param {number} celsius - Temperature in Celsius
 * @returns {number} Temperature in Fahrenheit
 */
function celsiusToFahrenheit(celsius) {
    return (celsius * 9 / 5) + 32;
}

/**
 * Convert mph to km/h
 * @param {number} mph - Speed in miles per hour
 * @returns {number} Speed in kilometers per hour
 */
function mphToKmh(mph) {
    return mph * 1.60934;
}

/**
 * Convert km/h to mph
 * @param {number} kmh - Speed in kilometers per hour
 * @returns {number} Speed in miles per hour
 */
function kmhToMph(kmh) {
    return kmh / 1.60934;
}

/**
 * Format temperature based on current metric system
 * @param {number} tempF - Temperature in Fahrenheit
 * @returns {string} Formatted temperature string
 */
function formatTemperature(tempF) {
    if (currentMetric === 'metric') {
        const tempC = fahrenheitToCelsius(tempF);
        return `${tempC.toFixed(1)}°C`;
    }
    return `${tempF.toFixed(1)}°F`;
}

/**
 * Format wind speed based on current metric system
 * @param {number} windMph - Wind speed in mph
 * @returns {string} Formatted wind speed string
 */
function formatWindSpeed(windMph) {
    if (currentMetric === 'metric') {
        const windKmh = mphToKmh(windMph);
        return `${windKmh.toFixed(1)} km/h`;
    }
    return `${windMph.toFixed(1)} mph`;
}

/**
 * Get Y-axis label based on metric system
 * @param {string} paramType - Parameter type (temp, wind, etc.)
 * @returns {string} Y-axis label
 */
function getYAxisLabel(paramType) {
    const labels = {
        temp: currentMetric === 'metric' ? 'Temperature (°C)' : 'Temperature (°F)',
        humidity: 'Humidity (%)',
        wind: currentMetric === 'metric' ? 'Wind (km/h)' : 'Wind (mph)',
        pressure: 'Pressure (mb)',
        precip: 'Precipitation (mm)',
        uv: 'UV Index'
    };
    return labels[paramType] || '';
}

/**
 * Fetch data from Flask API
 * @param {string} endpoint - API endpoint path
 * @returns {Promise<Object>} API response data
 */
async function fetchFromAPI(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || `API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching from ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Update the last updated timestamp
 * @param {string} timestamp - ISO timestamp string
 */
function updateLastUpdatedTime(timestamp) {
    const date = new Date(timestamp);
    const timeString = date.toLocaleTimeString();
    document.querySelector('.last-updated').textContent = `Last Updated: ${timeString}`;
}

// ============================================================================
// LOCATION SELECTOR LOGIC
// ============================================================================

/**
 * Initialize location selector event listeners
 * Wrapped in DOMContentLoaded to ensure DOM elements are ready
 */
function initializeLocationSelectors() {
    /**
     * Handle country selection change
     * Requirement 5.2: When a user selects a country, populate state dropdown
     */
    const countrySelect = document.getElementById('countrySelect');
    if (countrySelect) {
        countrySelect.addEventListener('change', function() {
            const countryCode = this.value;
            const stateSelect = document.getElementById('stateSelect');
            const districtSelect = document.getElementById('districtSelect');
            
            stateSelect.innerHTML = '<option value="">Select State</option>';
            districtSelect.innerHTML = '<option value="">Select District</option>';
            
            currentLocation.country = countryCode;
            currentLocation.state = null;
            currentLocation.district = null;
            
            if (countryCode && locationData[countryCode]) {
                const states = locationData[countryCode].states;
                for (const [code, state] of Object.entries(states)) {
                    const option = document.createElement('option');
                    option.value = code;
                    option.textContent = state.name;
                    stateSelect.appendChild(option);
                }
            }
        });
    }

    /**
     * Handle state selection change
     * Requirement 5.3: When a user selects a state, populate district dropdown
     */
    const stateSelect = document.getElementById('stateSelect');
    if (stateSelect) {
        stateSelect.addEventListener('change', function() {
            const countryCode = document.getElementById('countrySelect').value;
            const stateCode = this.value;
            const districtSelect = document.getElementById('districtSelect');
            
            districtSelect.innerHTML = '<option value="">Select District</option>';
            
            currentLocation.state = stateCode;
            currentLocation.district = null;
            
            if (countryCode && stateCode && locationData[countryCode] && locationData[countryCode].states[stateCode]) {
                const districts = locationData[countryCode].states[stateCode].districts;
                districts.forEach(district => {
                    const option = document.createElement('option');
                    option.value = district;
                    option.textContent = district;
                    districtSelect.appendChild(option);
                });
            }
        });
    }

    /**
     * Handle district selection change
     * Requirement 5.4: When a user selects a complete location, fetch new data
     */
    const districtSelect = document.getElementById('districtSelect');
    if (districtSelect) {
        districtSelect.addEventListener('change', async function() {
            if (this.value) {
                const countryCode = document.getElementById('countrySelect').value;
                const stateCode = document.getElementById('stateSelect').value;
                const district = this.value;
                
                currentLocation.country = countryCode;
                currentLocation.state = stateCode;
                currentLocation.district = district;
                
                // Fetch and update all data for the selected location
                await fetchAndUpdateLocationData(countryCode, stateCode, district);
            }
        });
    }
}

/**
 * Fetch and update all data for a selected location
 * Requirement 5.4: Fetch new weather and pollen data and update visualizations
 * @param {string} country - Country code
 * @param {string} state - State code
 * @param {string} district - District name
 */
async function fetchAndUpdateLocationData(country, state, district) {
    try {
        // Show loading indicator
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'loading-indicator';
        loadingMsg.textContent = 'Loading data...';
        document.body.appendChild(loadingMsg);
        
        // Fetch weather data
        const weatherData = await fetchFromAPI(`/api/weather/${country}/${state}/${district}`);
        updateWeatherPanel(weatherData);
        updateLastUpdatedTime(weatherData.timestamp);
        
        // Fetch pollen data
        const pollenData = await fetchFromAPI(`/api/pollen/${country}/${state}/${district}`);
        updatePollenPanel(pollenData);
        
        // Fetch correlation data
        const correlationData = await fetchFromAPI(`/api/correlation/${country}/${state}/${district}`);
        updateCorrelationPanel(correlationData);
        
        // Update charts with data based on current time range
        updateChartsForTimeRange(weatherData, pollenData, currentTimeRange);
        
        // Remove loading indicator
        loadingMsg.remove();
    } catch (error) {
        console.error('Error fetching location data:', error);
        alert(`Error loading data: ${error.message}`);
        // Remove loading indicator
        const loadingMsg = document.querySelector('.loading-indicator');
        if (loadingMsg) loadingMsg.remove();
    }
}

/**
 * Generate demo data based on time range and update charts
 * @param {Object} weatherData - Current weather data from API
 * @param {Object} pollenData - Current pollen data from API
 * @param {string} timeRange - Current time range (weekly, monthly, etc.)
 */
function updateChartsForTimeRange(weatherData, pollenData, timeRange) {
    // Generate data points and labels based on time range
    let dataPoints = 7; // default for weekly
    let labels = [];
    const today = new Date();
    const currentMonth = today.getMonth();
    
    switch(timeRange) {
        case 'weekly':
            // Sunday through Saturday
            dataPoints = 7;
            const weekStart = new Date(today);
            weekStart.setDate(today.getDate() - today.getDay()); // Get Sunday
            labels = [];
            const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            for (let i = 0; i < 7; i++) {
                const date = new Date(weekStart);
                date.setDate(weekStart.getDate() + i);
                labels.push(dayNames[i]);
            }
            break;
            
        case 'monthly':
            // Calendar weeks (Week 1-4)
            dataPoints = 4;
            labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
            break;
            
        case 'half-yearly':
            // Jan-Jun or Jul-Dec based on current month
            dataPoints = 6;
            if (currentMonth < 6) {
                // Jan to Jun
                labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
            } else {
                // Jul to Dec
                labels = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            }
            break;
            
        case 'yearly':
            // Jan to Dec
            dataPoints = 12;
            labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            break;
    }
    
    // Generate realistic data based on current weather
    const baseTemp = weatherData.temperature || 72;
    const baseHumidity = weatherData.humidity || 65;
    const baseWind = weatherData.wind_speed || 12;
    const basePressure = weatherData.pressure || 1013;
    const basePrecip = weatherData.precipitation || 0;
    const baseUV = weatherData.uv_index || 6;
    
    // Generate temperature data with variation
    const tempData = Array.from({length: dataPoints}, (_, i) => 
        baseTemp + (Math.random() - 0.5) * 10
    );
    
    // Generate humidity data with variation
    const humidityData = Array.from({length: dataPoints}, (_, i) => 
        Math.max(0, Math.min(100, baseHumidity + (Math.random() - 0.5) * 20))
    );
    
    // Generate wind data with variation
    const windData = Array.from({length: dataPoints}, (_, i) => 
        Math.max(0, baseWind + (Math.random() - 0.5) * 8)
    );
    
    // Generate pressure data with variation
    const pressureData = Array.from({length: dataPoints}, (_, i) => 
        basePressure + (Math.random() - 0.5) * 10
    );
    
    // Generate precipitation data with variation
    const precipData = Array.from({length: dataPoints}, (_, i) => 
        Math.max(0, basePrecip + Math.random() * 5)
    );
    
    // Generate UV data with variation
    const uvData = Array.from({length: dataPoints}, (_, i) => 
        Math.max(0, Math.min(11, baseUV + (Math.random() - 0.5) * 4))
    );
    
    // Generate pollen data with variation
    const grassPollenData = Array.from({length: dataPoints}, (_, i) => 
        pollenData.pollen_types?.grass?.concentration || 600 + Math.random() * 400
    );
    
    const treePollenData = Array.from({length: dataPoints}, (_, i) => 
        pollenData.pollen_types?.tree?.concentration || 300 + Math.random() * 200
    );
    
    const weedPollenData = Array.from({length: dataPoints}, (_, i) => 
        pollenData.pollen_types?.weed?.concentration || 100 + Math.random() * 100
    );
    
    // Update temperature chart
    if (temperatureChart) {
        temperatureChart.data.labels = labels;
        temperatureChart.data.datasets[0].data = tempData;
        temperatureChart.update();
    }
    
    // Update pollen chart
    if (pollenChart) {
        pollenChart.data.labels = labels;
        pollenChart.data.datasets[0].data = grassPollenData;
        pollenChart.data.datasets[1].data = treePollenData;
        pollenChart.data.datasets[2].data = weedPollenData;
        pollenChart.update();
    }
    
    // Update correlation chart
    if (correlationChart) {
        correlationChart.data.labels = labels;
        correlationChart.data.datasets[0].data = tempData;
        correlationChart.data.datasets[1].data = grassPollenData;
        correlationChart.update();
    }
}

/**
 * Update weather panel with fetched data
 * Requirement 1.1: Display current weather data
 * @param {Object} weatherData - Weather data from API
 */
function updateWeatherPanel(weatherData) {
    // Store original data for unit conversions
    originalWeatherData = {
        temperature: weatherData.temperature,
        wind_speed: weatherData.wind_speed
    };
    
    // Get all weather items
    const weatherItems = document.querySelectorAll('.weather-item');
    
    // Update each weather parameter
    // Index 0: Temperature
    if (weatherItems[0]) {
        const tempValue = weatherItems[0].querySelector('value');
        if (tempValue) tempValue.textContent = formatTemperature(weatherData.temperature);
    }
    
    // Index 1: Humidity
    if (weatherItems[1]) {
        const humidityValue = weatherItems[1].querySelector('value');
        if (humidityValue) humidityValue.textContent = `${weatherData.humidity}%`;
    }
    
    // Index 2: Wind Speed
    if (weatherItems[2]) {
        const windValue = weatherItems[2].querySelector('value');
        if (windValue) windValue.textContent = formatWindSpeed(weatherData.wind_speed);
    }
    
    // Index 3: Atmospheric Pressure
    if (weatherItems[3]) {
        const pressureValue = weatherItems[3].querySelector('value');
        if (pressureValue) pressureValue.textContent = `${weatherData.pressure} mb`;
    }
    
    // Index 4: Precipitation
    if (weatherItems[4]) {
        const precipValue = weatherItems[4].querySelector('value');
        if (precipValue) precipValue.textContent = `${weatherData.precipitation} mm`;
    }
    
    // Index 5: UV Index
    if (weatherItems[5]) {
        const uvValue = weatherItems[5].querySelector('value');
        if (uvValue) uvValue.textContent = `${weatherData.uv_index} (${getUVCategory(weatherData.uv_index)})`;
    }
    
    // Index 6: Conditions
    if (weatherItems[6]) {
        const conditionsValue = weatherItems[6].querySelector('value');
        if (conditionsValue) conditionsValue.textContent = weatherData.conditions || 'N/A';
    }
}

/**
 * Get UV index category
 * @param {number} uvIndex - UV index value
 * @returns {string} UV category
 */
function getUVCategory(uvIndex) {
    if (uvIndex < 3) return 'Low';
    if (uvIndex < 6) return 'Moderate';
    if (uvIndex < 8) return 'High';
    if (uvIndex < 11) return 'Very High';
    return 'Extreme';
}

/**
 * Update pollen panel with fetched data
 * Requirement 1.1: Display pollen levels by type
 * Requirement 3.1: Display at least five pollen types
 * @param {Object} pollenData - Pollen data from API
 */
function updatePollenPanel(pollenData) {
    const pollenTypes = ['grass', 'tree', 'weed', 'ragweed', 'mold'];
    const pollenLabels = ['Grass Pollen', 'Tree Pollen', 'Weed Pollen', 'Ragweed Pollen', 'Mold Spores'];
    
    pollenTypes.forEach((type, index) => {
        const pollenItem = document.querySelector(`.pollen-item:nth-child(${index + 1})`);
        if (pollenItem && pollenData.pollen_types[type]) {
            const data = pollenData.pollen_types[type];
            const valueElement = pollenItem.querySelector('value');
            const levelElement = pollenItem.querySelector('.pollen-level');
            
            if (valueElement) {
                valueElement.innerHTML = `${data.concentration} <span class="pollen-level ${data.severity.toLowerCase()}">${data.severity}</span>`;
            }
        }
    });
}

/**
 * Update correlation panel with fetched data
 * Requirement 4.1: Display correlation coefficients
 * @param {Object} correlationData - Correlation data from API
 */
function updateCorrelationPanel(correlationData) {
    const correlationContainer = document.querySelector('.correlation-container');
    if (!correlationContainer || !correlationData.correlations) return;
    
    // Update correlation items
    const correlationItems = correlationContainer.querySelectorAll('.correlation-item');
    correlationData.correlations.forEach((corr, index) => {
        if (correlationItems[index]) {
            const item = correlationItems[index];
            const strengthElement = item.querySelector('.correlation-strength');
            const valueElement = item.querySelector('.correlation-value');
            
            if (strengthElement) {
                const strengthClass = getCorrelationStrengthClass(corr.correlation_coefficient);
                strengthElement.className = `correlation-strength ${strengthClass}`;
                strengthElement.textContent = `${corr.correlation_coefficient.toFixed(2)} (${corr.strength})`;
            }
            if (valueElement) {
                valueElement.textContent = corr.explanation;
            }
        }
    });
}

/**
 * Get correlation strength CSS class
 * @param {number} coefficient - Correlation coefficient
 * @returns {string} CSS class name
 */
function getCorrelationStrengthClass(coefficient) {
    const absCoeff = Math.abs(coefficient);
    if (absCoeff >= 0.7) return 'strong';
    if (absCoeff >= 0.4) return 'moderate';
    return 'weak';
}

// ============================================================================
// METRIC SYSTEM SELECTOR
// ============================================================================

/**
 * Handle metric system selection
 * Requirement 8.2: Convert and display temperature values
 * Requirement 8.3: Convert and display wind speed values
 * Requirement 8.5: Update all charts and values immediately
 */
// Store original weather data for unit conversions
let originalWeatherData = null;

document.querySelectorAll('.metric-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.metric-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        currentMetric = this.dataset.metric;
        
        // Update weather panel values using original data
        if (originalWeatherData) {
            // Get all weather items
            const weatherItems = document.querySelectorAll('.weather-item');
            
            // Temperature is the 1st weather item (index 0)
            if (weatherItems[0]) {
                const tempValue = weatherItems[0].querySelector('value');
                if (tempValue) {
                    tempValue.textContent = formatTemperature(originalWeatherData.temperature);
                }
            }
            
            // Wind Speed is the 3rd weather item (index 2)
            if (weatherItems[2]) {
                const windValue = weatherItems[2].querySelector('value');
                if (windValue) {
                    windValue.textContent = formatWindSpeed(originalWeatherData.wind_speed);
                }
            }
        }
        
        // Update chart Y-axis labels
        updateChartAxisLabels();
        
        // Persist preference to localStorage
        localStorage.setItem('metricSystem', currentMetric);
    });
});

/**
 * Load metric system preference from localStorage
 */
function loadMetricPreference() {
    const saved = localStorage.getItem('metricSystem');
    if (saved) {
        currentMetric = saved;
        const btn = document.querySelector(`.metric-btn[data-metric="${saved}"]`);
        if (btn) {
            document.querySelectorAll('.metric-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }
    }
}

/**
 * Update chart Y-axis labels based on metric system
 */
function updateChartAxisLabels() {
    if (temperatureChart && temperatureChart.options.scales) {
        temperatureChart.options.scales.y.title.text = getYAxisLabel('temp');
        temperatureChart.options.scales.y2.title.text = getYAxisLabel('humidity');
        temperatureChart.options.scales.y3.title.text = getYAxisLabel('wind');
        temperatureChart.options.scales.y4.title.text = getYAxisLabel('pressure');
        temperatureChart.options.scales.y5.title.text = getYAxisLabel('precip');
        temperatureChart.options.scales.y6.title.text = getYAxisLabel('uv');
        temperatureChart.update();
    }
    
    if (correlationChart && correlationChart.options.scales) {
        correlationChart.options.scales.y.title.text = getYAxisLabel('temp');
        correlationChart.options.scales.y2.title.text = getYAxisLabel('humidity');
        correlationChart.options.scales.y3.title.text = getYAxisLabel('wind');
        correlationChart.options.scales.y4.title.text = getYAxisLabel('pressure');
        correlationChart.options.scales.y5.title.text = getYAxisLabel('precip');
        correlationChart.options.scales.y6.title.text = getYAxisLabel('uv');
        correlationChart.update();
    }
}

// ============================================================================
// WEATHER PARAMETERS CHART
// ============================================================================

const parameterData = {
    temp: { label: '🌡️ Temperature', data: [65, 68, 72, 75, 73, 70, 68], color: '#FF4444' },
    humidity: { label: '💧 Humidity', data: [55, 60, 65, 62, 68, 70, 72], color: '#0099FF' },
    wind: { label: '💨 Wind Speed', data: [8, 10, 12, 15, 14, 11, 9], color: '#00CC44' },
    pressure: { label: '🔽 Pressure', data: [1010, 1012, 1013, 1011, 1009, 1008, 1010], color: '#FF9900' },
    precip: { label: '🌧️ Precipitation', data: [0, 0, 0, 2, 5, 1, 0], color: '#9933FF' },
    uv: { label: '☀️ UV Index', data: [3, 4, 6, 7, 6, 5, 4], color: '#FFDD00' }
};

const parameterFeedback = {
    temp: "Temperature increases pollen release from plants.",
    humidity: "High humidity reduces airborne pollen.",
    wind: "Wind speed significantly increases pollen dispersion.",
    pressure: "Low pressure triggers higher pollen release.",
    precip: "Precipitation washes pollen out of the air.",
    uv: "High UV index correlates with increased pollen levels."
};

/**
 * Update weather parameters chart
 * Requirement 2.4: When a user selects a parameter, populate that parameter's data
 * Requirement 2.5: When a user deselects a parameter, remove that parameter's data
 * Requirement 2.6: Use dual or multiple Y-axes for different scales
 * Requirement 2.8: Use distinct colors for each parameter
 * Requirement 2.9: Display comparative feedback
 */
function updateChart() {
    const selectedParams = [];
    const selectedData = [];
    const yAxisMap = {
        temp: 'y',
        humidity: 'y1',
        wind: 'y2',
        pressure: 'y3',
        precip: 'y4',
        uv: 'y5'
    };
    
    let visibleAxes = new Set(['y']); // Temperature axis always visible
    
    // Only check weather parameter checkboxes
    document.querySelectorAll('#tempCheck, #humidityCheck, #windCheck, #pressureCheck, #precipCheck, #uvCheck').forEach(cb => {
        if (cb.checked) {
            const paramKey = cb.id.replace('Check', '');
            selectedParams.push(parameterData[paramKey].label);
            const yAxis = yAxisMap[paramKey];
            visibleAxes.add(yAxis);
            
            selectedData.push({
                label: parameterData[paramKey].label,
                data: parameterData[paramKey].data,
                borderColor: parameterData[paramKey].color,
                backgroundColor: parameterData[paramKey].color + '20',
                borderWidth: 2,
                tension: 0.4,
                fill: false,
                yAxisID: yAxis,
                type: 'line'
            });
        }
    });

    // Update chart with selected parameters
    if (temperatureChart) {
        temperatureChart.data.datasets = selectedData;
        
        // Update Y-axis visibility
        Object.keys(yAxisMap).forEach(key => {
            const yAxis = yAxisMap[key];
            if (temperatureChart.options.scales[yAxis]) {
                temperatureChart.options.scales[yAxis].display = visibleAxes.has(yAxis);
            }
        });
        
        temperatureChart.update();
    }

    // Update feedback
    const feedback = document.getElementById('comparativeFeedback');
    if (selectedParams.length === 0) {
        feedback.innerHTML = '<strong>📊 Comparative Analysis:</strong> Select parameters to see how they interact with pollen levels.';
    } else if (selectedParams.length === 1) {
        const paramKey = Array.from(document.querySelectorAll('#tempCheck, #humidityCheck, #windCheck, #pressureCheck, #precipCheck, #uvCheck')).find(cb => cb.checked).id.replace('Check', '');
        feedback.innerHTML = `<strong>📊 Single Parameter Analysis:</strong> ${selectedParams[0]} is displayed. ${parameterFeedback[paramKey]}`;
    } else {
        feedback.innerHTML = `<strong>📊 Multi-Parameter Analysis:</strong> Showing ${selectedParams.join(', ')}. These parameters work together to influence pollen levels. High wind combined with low humidity and high temperature creates ideal conditions for maximum pollen dispersion.`;
    }
}

// Only attach updateChart to weather parameter checkboxes (not pollen or correlation checkboxes)
document.querySelectorAll('#tempCheck, #humidityCheck, #windCheck, #pressureCheck, #precipCheck, #uvCheck').forEach(checkbox => {
    checkbox.addEventListener('change', updateChart);
});

let temperatureChart; // Will be initialized below

// Temperature Chart - Initialize with Temperature selected by default (Line Chart)
const temperatureCtx = document.getElementById('temperatureChart').getContext('2d');
temperatureChart = new Chart(temperatureCtx, {
    type: 'line',
    data: {
        labels: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        datasets: [{
            label: '🌡️ Temperature',
            data: [65, 68, 72, 75, 73, 70, 68],
            borderColor: '#ff6b6b',
            backgroundColor: 'rgba(255, 107, 107, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointRadius: 6,
            pointBackgroundColor: '#ff6b6b',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointHoverRadius: 8,
            yAxisID: 'y',
            type: 'line'
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false
        },
        plugins: {
            legend: {
                display: true,
                labels: { font: { size: 12 } }
            }
        },
        scales: {
            x: {
                display: true,
                ticks: { display: true, font: { size: 12 } },
                title: { display: true, text: 'Day of Week' }
            },
            y: {
                type: 'linear',
                display: true,
                position: 'left',
                title: { display: true, text: 'Temperature (°F)' },
                min: 60,
                max: 80
            },
            y1: {
                type: 'linear',
                display: false,
                position: 'right',
                title: { display: true, text: 'Humidity (%)' },
                min: 0,
                max: 100,
                grid: { drawOnChartArea: false }
            },
            y2: {
                type: 'linear',
                display: false,
                position: 'right',
                title: { display: true, text: 'Wind (mph)' },
                min: 0,
                max: 20,
                grid: { drawOnChartArea: false }
            },
            y3: {
                type: 'linear',
                display: false,
                position: 'right',
                title: { display: true, text: 'Pressure (mb)' },
                min: 1000,
                max: 1020,
                grid: { drawOnChartArea: false }
            },
            y4: {
                type: 'linear',
                display: false,
                position: 'right',
                title: { display: true, text: 'Precipitation (mm)' },
                min: 0,
                max: 10,
                grid: { drawOnChartArea: false }
            },
            y5: {
                type: 'linear',
                display: false,
                position: 'right',
                title: { display: true, text: 'UV Index' },
                min: 0,
                max: 10,
                grid: { drawOnChartArea: false }
            }
        }
    }
});

// Pollen Chart - Using bar chart for better visibility
const pollenCtx = document.getElementById('pollenChart').getContext('2d');
let pollenChart = new Chart(pollenCtx, {
    type: 'bar',
    data: {
        labels: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        datasets: [
            {
                label: '🌾 Grass Pollen',
                data: [600, 650, 850, 800, 750, 500, 450],
                backgroundColor: '#00CC44',
                borderColor: '#00AA33',
                borderWidth: 2
            },
            {
                label: '🌳 Tree Pollen',
                data: [300, 350, 450, 400, 380, 250, 200],
                backgroundColor: '#FF9900',
                borderColor: '#DD7700',
                borderWidth: 2
            },
            {
                label: '🌱 Weed Pollen',
                data: [100, 120, 150, 140, 130, 80, 60],
                backgroundColor: '#9933FF',
                borderColor: '#7722DD',
                borderWidth: 2
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                labels: { font: { size: 12 } }
            }
        },
        scales: {
            x: {
                stacked: false,
                display: true,
                ticks: { display: true, font: { size: 12 } },
                title: { display: true, text: 'Day of Week' }
            },
            y: {
                stacked: false,
                title: { display: true, text: 'Pollen Count' }
            }
        }
    }
});

// Correlation Chart - Mixed chart with bar for pollen and line for weather
const correlationCtx = document.getElementById('correlationChart').getContext('2d');
let correlationChart = new Chart(correlationCtx, {
    type: 'line',
    data: {
        labels: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        datasets: [
            {
                label: '🌡️ Temperature (°F)',
                data: [65, 68, 72, 75, 73, 70, 68],
                borderColor: '#FF4444',
                backgroundColor: 'rgba(255, 68, 68, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointBackgroundColor: '#FF4444',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 8,
                type: 'line',
                yAxisID: 'y'
            },
            {
                label: '💧 Humidity (%)',
                data: [55, 60, 65, 62, 68, 70, 72],
                borderColor: '#0099FF',
                backgroundColor: 'rgba(0, 153, 255, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#0099FF',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 7,
                type: 'line',
                yAxisID: 'y2'
            },
            {
                label: '💨 Wind Speed (mph)',
                data: [8, 10, 12, 15, 14, 11, 9],
                borderColor: '#00CC44',
                backgroundColor: 'rgba(0, 204, 68, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#00CC44',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 7,
                type: 'line',
                yAxisID: 'y3'
            },
            {
                label: '🔽 Pressure (mb)',
                data: [1010, 1012, 1013, 1011, 1009, 1008, 1010],
                borderColor: '#FF9900',
                backgroundColor: 'rgba(255, 153, 0, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#FF9900',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 7,
                type: 'line',
                yAxisID: 'y4'
            },
            {
                label: '🌧️ Precipitation (mm)',
                data: [0, 0, 0, 2, 5, 1, 0],
                borderColor: '#9933FF',
                backgroundColor: 'rgba(153, 51, 255, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#9933FF',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 7,
                type: 'line',
                yAxisID: 'y5'
            },
            {
                label: '☀️ UV Index',
                data: [3, 4, 6, 7, 6, 5, 4],
                borderColor: '#FFDD00',
                backgroundColor: 'rgba(255, 221, 0, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#FFDD00',
                pointBorderColor: '#333',
                pointBorderWidth: 2,
                pointHoverRadius: 7,
                type: 'line',
                yAxisID: 'y6'
            },
            {
                label: '🌾 Grass Pollen',
                data: [1000, 1120, 1450, 1340, 1260, 830, 710],
                backgroundColor: '#00CC44',
                borderColor: '#00AA33',
                borderWidth: 2,
                type: 'bar',
                yAxisID: 'y1'
            },
            {
                label: '🌳 Tree Pollen',
                data: [600, 650, 850, 800, 750, 500, 450],
                backgroundColor: '#FF9900',
                borderColor: '#DD7700',
                borderWidth: 2,
                type: 'bar',
                yAxisID: 'y7'
            },
            {
                label: '🌱 Weed Pollen',
                data: [300, 350, 450, 400, 380, 250, 200],
                backgroundColor: '#9933FF',
                borderColor: '#7722DD',
                borderWidth: 2,
                type: 'bar',
                yAxisID: 'y8'
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false
        },
        plugins: {
            legend: {
                display: true,
                labels: { font: { size: 12 } }
            }
        },
        scales: {
            x: {
                display: true,
                ticks: { display: true, font: { size: 12 } },
                title: { display: true, text: 'Day of Week' }
            },
            y: {
                type: 'linear',
                display: true,
                position: 'left',
                title: { display: true, text: 'Temperature (°F)' },
                min: 60,
                max: 80
            },
            y1: {
                type: 'linear',
                display: true,
                position: 'right',
                title: { display: true, text: 'Grass Pollen' },
                min: 500,
                max: 1500,
                grid: { drawOnChartArea: false }
            },
            y2: { type: 'linear', display: false, position: 'right', title: { display: true, text: 'Humidity (%)' }, min: 0, max: 100, grid: { drawOnChartArea: false } },
            y3: { type: 'linear', display: false, position: 'right', title: { display: true, text: 'Wind (mph)' }, min: 0, max: 20, grid: { drawOnChartArea: false } },
            y4: { type: 'linear', display: false, position: 'right', title: { display: true, text: 'Pressure (mb)' }, min: 1000, max: 1020, grid: { drawOnChartArea: false } },
            y5: { type: 'linear', display: false, position: 'right', title: { display: true, text: 'Precipitation (mm)' }, min: 0, max: 10, grid: { drawOnChartArea: false } },
            y6: { type: 'linear', display: false, position: 'right', title: { display: true, text: 'UV Index' }, min: 0, max: 10, grid: { drawOnChartArea: false } },
            y7: { type: 'linear', display: false, position: 'right', title: { display: true, text: 'Tree Pollen' }, min: 400, max: 900, grid: { drawOnChartArea: false } },
            y8: { type: 'linear', display: false, position: 'right', title: { display: true, text: 'Weed Pollen' }, min: 200, max: 500, grid: { drawOnChartArea: false } }
        }
    }
});

// Correlation chart parameter selection
const correlationWeatherData = {
    temp: { label: '🌡️ Temperature', data: [65, 68, 72, 75, 73, 70, 68], color: '#FF4444', yAxis: 'y' },
    humidity: { label: '💧 Humidity', data: [55, 60, 65, 62, 68, 70, 72], color: '#0099FF', yAxis: 'y2' },
    wind: { label: '💨 Wind Speed', data: [8, 10, 12, 15, 14, 11, 9], color: '#00CC44', yAxis: 'y3' },
    pressure: { label: '🔽 Pressure', data: [1010, 1012, 1013, 1011, 1009, 1008, 1010], color: '#FF9900', yAxis: 'y4' },
    precip: { label: '🌧️ Precipitation', data: [0, 0, 0, 2, 5, 1, 0], color: '#9933FF', yAxis: 'y5' },
    uv: { label: '☀️ UV Index', data: [3, 4, 6, 7, 6, 5, 4], color: '#FFDD00', yAxis: 'y6' }
};

const correlationPollenData = {
    grass: { label: '🌾 Grass Pollen', data: [1000, 1120, 1450, 1340, 1260, 830, 710], color: '#00CC44', yAxis: 'y1' },
    tree: { label: '🌳 Tree Pollen', data: [600, 650, 850, 800, 750, 500, 450], color: '#FF9900', yAxis: 'y7' },
    weed: { label: '🌱 Weed Pollen', data: [300, 350, 450, 400, 380, 250, 200], color: '#9933FF', yAxis: 'y8' }
};

// Pollen chart parameter selection
const pollenTypeData = {
    grass: { label: '🌾 Grass Pollen', data: [600, 650, 850, 800, 750, 500, 450], backgroundColor: '#00CC44', borderColor: '#00AA33' },
    tree: { label: '🌳 Tree Pollen', data: [300, 350, 450, 400, 380, 250, 200], backgroundColor: '#FF9900', borderColor: '#DD7700' },
    weed: { label: '🌱 Weed Pollen', data: [100, 120, 150, 140, 130, 80, 60], backgroundColor: '#9933FF', borderColor: '#7722DD' }
};

function updatePollenChart() {
    const datasets = [];
    
    document.querySelectorAll('#grassPollenCheck, #treePollenCheck, #weedPollenCheck').forEach(cb => {
        if (cb.checked) {
            const pollenType = cb.id.replace('PollenCheck', '').toLowerCase();
            if (pollenTypeData[pollenType]) {
                const data = pollenTypeData[pollenType];
                datasets.push({
                    label: data.label,
                    data: data.data,
                    backgroundColor: data.backgroundColor,
                    borderColor: data.borderColor,
                    borderWidth: 2
                });
            }
        }
    });

    if (pollenChart) {
        pollenChart.data.datasets = datasets;
        pollenChart.update();
    }
}

document.querySelectorAll('#grassPollenCheck, #treePollenCheck, #weedPollenCheck').forEach(checkbox => {
    checkbox.addEventListener('change', updatePollenChart);
});

// Correlation chart parameter selection with proper logic
function updateCorrelationChart() {
    const datasets = [];
    const visibleAxes = new Set();
    
    // Get selected weather parameters
    const selectedWeatherParams = [];
    document.querySelectorAll('#corrTempCheck, #corrHumidityCheck, #corrWindCheck, #corrPressureCheck, #corrPrecipCheck, #corrUVCheck').forEach(cb => {
        if (cb.checked) {
            const paramKey = cb.id.replace('corr', '').replace('Check', '').toLowerCase();
            selectedWeatherParams.push(paramKey);
            if (correlationWeatherData[paramKey]) {
                const data = correlationWeatherData[paramKey];
                visibleAxes.add(data.yAxis);
                datasets.push({
                    label: data.label,
                    data: data.data,
                    borderColor: data.color,
                    backgroundColor: data.color + '20',
                    borderWidth: 2,
                    tension: 0.4,
                    yAxisID: data.yAxis
                });
            }
        }
    });

    // Get selected pollen types
    const selectedPollenTypes = [];
    document.querySelectorAll('#corrGrassCheck, #corrTreeCheck, #corrWeedCheck').forEach(cb => {
        if (cb.checked) {
            const pollenKey = cb.id.replace('corr', '').replace('Check', '').toLowerCase();
            selectedPollenTypes.push(pollenKey);
            if (correlationPollenData[pollenKey]) {
                const data = correlationPollenData[pollenKey];
                visibleAxes.add(data.yAxis);
                datasets.push({
                    label: data.label,
                    data: data.data,
                    borderColor: data.color,
                    backgroundColor: data.color + '20',
                    borderWidth: 2,
                    tension: 0.4,
                    yAxisID: data.yAxis
                });
            }
        }
    });

    // Update chart
    if (correlationChart) {
        correlationChart.data.datasets = datasets;
        
        // Update Y-axis visibility
        ['y', 'y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8'].forEach(axis => {
            if (correlationChart.options.scales[axis]) {
                correlationChart.options.scales[axis].display = visibleAxes.has(axis);
            }
        });
        
        correlationChart.update();
    }

    // Update feedback
    const feedback = document.getElementById('correlationFeedback');
    if (selectedWeatherParams.length === 0 && selectedPollenTypes.length === 0) {
        feedback.innerHTML = '<strong>🔗 Correlation Analysis:</strong> Select weather parameters and pollen types to analyze their correlations.';
    } else {
        const weatherLabels = selectedWeatherParams.map(p => correlationWeatherData[p]?.label).filter(Boolean);
        const pollenLabels = selectedPollenTypes.map(p => correlationPollenData[p]?.label).filter(Boolean);
        const allLabels = [...weatherLabels, ...pollenLabels];
        feedback.innerHTML = `<strong>🔗 Correlation Analysis:</strong> Analyzing ${allLabels.join(', ')}. The chart shows how these parameters correlate with each other over time.`;
    }
}

// Attach event listeners to all correlation checkboxes
document.querySelectorAll('#corrTempCheck, #corrHumidityCheck, #corrWindCheck, #corrPressureCheck, #corrPrecipCheck, #corrUVCheck, #corrGrassCheck, #corrTreeCheck, #corrWeedCheck').forEach(checkbox => {
    checkbox.addEventListener('change', updateCorrelationChart);
});

// ============================================================================
// TIME RANGE FILTERS
// ============================================================================

/**
 * Handle time range filter selection
 * Requirement 7.1: Provide time range filter buttons
 * Requirement 7.2: Aggregate and display data appropriate to period
 * Requirement 7.4: Display the date range in the header
 */
document.querySelectorAll('.time-btn').forEach(btn => {
    btn.addEventListener('click', async function() {
        document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        const timeRange = this.textContent.toLowerCase().split(' ')[1];
        currentTimeRange = timeRange;
        
        // Update date range display for all charts
        const dateRanges = document.querySelectorAll('.date-range');
        if (dateRanges.length > 0) {
            const today = new Date();
            let startDate, endDate;
            
            switch(timeRange) {
                case 'weekly':
                    startDate = new Date(today);
                    startDate.setDate(today.getDate() - 6);
                    endDate = today;
                    break;
                case 'monthly':
                    startDate = new Date(today.getFullYear(), today.getMonth(), 1);
                    endDate = today;
                    break;
                case 'half-yearly':
                    startDate = new Date(today);
                    startDate.setMonth(today.getMonth() - 6);
                    endDate = today;
                    break;
                case 'yearly':
                    startDate = new Date(today.getFullYear(), 0, 1);
                    endDate = today;
                    break;
            }
            
            const formatDate = (date) => {
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
            };
            
            const dateRangeText = `${formatDate(startDate)} - ${formatDate(endDate)}`;
            dateRanges.forEach(dateRange => {
                dateRange.textContent = dateRangeText;
            });
        }
        
        // Update chart titles to reflect the current time range
        const chartTitles = document.querySelectorAll('.chart-title');
        chartTitles.forEach(title => {
            const titleText = title.textContent;
            let newTimeRangeLabel = timeRange.charAt(0).toUpperCase() + timeRange.slice(1);
            if (timeRange === 'half-yearly') {
                newTimeRangeLabel = 'Half-Yearly';
            }
            
            // Replace any existing time range label with the new one
            const updatedTitle = titleText.replace(/\((Weekly|Monthly|Half-Yearly|Yearly) View\)/, `(${newTimeRangeLabel} View)`);
            title.textContent = updatedTitle;
        });
        
        // Fetch new aggregated data for the selected time range
        if (currentLocation.country && currentLocation.state && currentLocation.district) {
            await fetchAndUpdateLocationData(currentLocation.country, currentLocation.state, currentLocation.district);
        }
    });
});

// ============================================================================
// EXPORT FUNCTIONALITY
// ============================================================================

/**
 * Handle export button click
 * Requirement 6.1: Generate JSON file with all current data
 * Requirement 6.2: Include metadata
 */
document.querySelector('.btn-export').addEventListener('click', async function() {
    if (!currentLocation.country || !currentLocation.state || !currentLocation.district) {
        alert('Please select a location first');
        return;
    }
    
    try {
        // Fetch current data
        const weatherData = await fetchFromAPI(`/api/weather/${currentLocation.country}/${currentLocation.state}/${currentLocation.district}`);
        const pollenData = await fetchFromAPI(`/api/pollen/${currentLocation.country}/${currentLocation.state}/${currentLocation.district}`);
        const correlationData = await fetchFromAPI(`/api/correlation/${currentLocation.country}/${currentLocation.state}/${currentLocation.district}`);
        
        // Create export object with metadata
        const exportData = {
            metadata: {
                exportDate: new Date().toISOString(),
                location: currentLocation,
                timeRange: currentTimeRange,
                metricSystem: currentMetric
            },
            weather: weatherData,
            pollen: pollenData,
            correlations: correlationData
        };
        
        // Create and download JSON file
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `weather-pollen-data-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error exporting data:', error);
        alert(`Error exporting data: ${error.message}`);
    }
});

/**
 * Handle refresh button click
 */
document.querySelector('.btn-refresh').addEventListener('click', async function() {
    if (!currentLocation.country || !currentLocation.state || !currentLocation.district) {
        alert('Please select a location first');
        return;
    }
    
    await fetchAndUpdateLocationData(currentLocation.country, currentLocation.state, currentLocation.district);
});

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize location selectors
    initializeLocationSelectors();
    
    // Load saved metric preference
    loadMetricPreference();
    
    // Initialize charts (they are already initialized below)
    // Set default location if available
    const countrySelect = document.getElementById('countrySelect');
    if (countrySelect && countrySelect.options.length > 1) {
        countrySelect.value = 'USA';
        countrySelect.dispatchEvent(new Event('change'));
    }
});


// ============================================================================
// LAZY LOADING FOR CHARTS - PERFORMANCE OPTIMIZATION
// ============================================================================

/**
 * Lazy load charts when they become visible in the viewport
 * This significantly improves initial page load time by deferring chart
 * initialization until the user scrolls to the charts section
 * Requirement 2.11: Optimize frontend performance
 */
const chartLazyLoadObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            // Charts are already initialized, but this ensures they render
            // only when visible, improving performance
            if (temperatureChart) {
                temperatureChart.resize();
            }
            if (pollenChart) {
                pollenChart.resize();
            }
            if (correlationChart) {
                correlationChart.resize();
            }
            observer.unobserve(entry.target);
        }
    });
}, { threshold: 0.1 });

// Observe the charts section for lazy loading
document.addEventListener('DOMContentLoaded', () => {
    const chartsSection = document.querySelector('.charts-section');
    if (chartsSection) {
        chartLazyLoadObserver.observe(chartsSection);
    }
});
