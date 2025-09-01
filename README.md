# Asynchronous Weather Logger & Analyzer

A comprehensive Python CLI tool that fetches real-time weather data for multiple cities using the OpenWeatherMap API. Features asynchronous data fetching, local JSON storage, SQLite database support, data visualization, and automated scheduling.

# Features

- Asynchronous API Calls: Fast, concurrent weather data fetching using aiohttp
- Data Visualization: Temperature trend plots using matplotlib
- Dual Storage: JSON file and SQLite database support
- Smart Caching: Prevents duplicate entries within 2-hour windows
- Analytics: City-wise averages, temperature extremes, and trends
- Automated Scheduling: Background data collection at configurable intervals
- CLI Interface: Interactive menu and command-line arguments

# Quick Start

# 1. API Key Setup

1. Register at OpenWeatherMap(https://home.openweathermap.org/users/sign_up)
2. Generate your free API key from the dashboard
3. Use the key in your requests (already configured in the code)

# 2. Installation

The project uses a virtual environment with all dependencies already installed:

weather_env\Scripts\activate

# All dependencies are already installed in requirements.txt

# 3. Basic Usage

# Interactive CLI Mode
python weather_logger.py

# Command Line Arguments
# Fetch weather for specific cities
python weather_logger.py --cities "Delhi,Mumbai,Bangalore"

# Plot temperature trend for a city
python weather_logger.py --plot "Delhi"

# Export data to SQLite
python weather_logger.py --export-sqlite

# Automated Scheduling
# Schedule weather fetching every 30 minutes(i have kept by default as 1 minute)
python weather_scheduler.py --cities "Delhi,Mumbai,Bangalore" --interval 30


# CLI Menu Options
=== Weather Analyzer CLI ===
1. Fetch and log weather for cities
2. View all logs (as table)
3. Get city-wise average temperature
4. Show hottest and coldest cities
5. Plot temperature trend for a city
6. Export data to SQLite
7. Exit

# Data Structure

Each weather entry contains:
- City: City name
- Temperature : Temperature in Celsius
- Description: Weather description (e.g., "clear sky")
- Humidity: Humidity percentage
- UTC Timestamp: UTC timestamp
- Local Timestamp: Local timestamp

# File Structure

weather_analysis/
weather_logger.py == Main weather logger application
weather_scheduler.py == Automated scheduling module
weather_data.json == JSON data storage
weather_data.db == SQLite database
plots/city_temp_trend.png == generated temperature plot

# Data Analysis
- City-wise Averages: Calculate average temperatures for each city
- Temperature Extremes: Find hottest/coldest cities (overall and last 24h)
- Trend Analysis: Visualize temperature changes over time

# Storage Options
- JSON Storage: Human-readable data format
- SQLite Database: Structured database for complex queries
- Automatic Export: Convert between storage formats

# Visualization
- Temperature Trends: Line plots showing temperature changes
- High-Quality Output: 300 DPI plots saved as PNG files
- Customizable: Easy to modify plot styles and formats

# Dependencies
- aiohttp: Asynchronous HTTP client
- matplotlib: Data visualization
- pandas: Data manipulation
- tabulate: Formatted table output
- schedule: Task scheduling
- sqlite3: Database operations

# API Integration
- Endpoint: `https://api.openweathermap.org/data/2.5/weather`
- Units: Metric (Celsius)
- Response Format: JSON

# Error Handling
- Network Errors: Graceful handling of API failures
- Invalid Cities: Clear error messages for unknown locations
- Data Corruption: Automatic recovery from corrupted JSON files
- Duplicate Prevention: Smart caching to avoid redundant API calls

# Use Cases

1. Weather Monitoring: Track temperature trends for multiple cities
2. Data Analysis: Analyze historical weather patterns
3. Research: Collect weather data for academic projects
4. Automation: Set up automated weather logging systems
5. Visualization: Create weather trend reports and presentations

# Security Notes

- API key is hardcoded for demonstration (use environment variables in production)
- No sensitive data is logged or transmitted
- All data is stored locally