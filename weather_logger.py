"""
Asynchronous Weather Logger & Analyzer
A comprehensive CLI tool for fetching, logging, and analyzing weather data.
"""

import asyncio
import aiohttp
import json
import argparse
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
from tabulate import tabulate
import sqlite3
from pathlib import Path

class WeatherLogger:
    def __init__(self, api_key: str, data_file: str = "weather_data.json", db_file: str = "weather_data.db"):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.data_file = data_file
        self.db_file = db_file
        # Create directory to save plots if it doesn't exist
        self.plots_dir = Path("plots")
        self.plots_dir.mkdir(exist_ok=True)
        # Initialize SQLite database and create table if it doesn't exist
        self.init_database()
    
    def init_database(self):
        """
        Create SQLite database and weather_logs table if it doesn't exist.
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                temperature REAL NOT NULL,
                description TEXT NOT NULL,
                humidity INTEGER NOT NULL,
                utc_timestamp TEXT NOT NULL,
                local_timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    async def fetch_weather_data(self, session: aiohttp.ClientSession, city: str) -> Optional[Dict[str, Any]]:
        """
        Asynchronously fetch weather data for a given city from OpenWeatherMap API.
        Returns a dictionary with relevant weather info or None if error occurs.
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # Get temperature in Celsius
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'city': city,
                        'temperature': data['main']['temp'],
                        'description': data['weather'][0]['description'],
                        'humidity': data['main']['humidity'],
                        'utc_timestamp': datetime.now(timezone.utc).isoformat(),
                        'local_timestamp': datetime.now().isoformat()
                    }
                else:
                    print(f"Error fetching data for {city}: HTTP {response.status}")
                    return None
        except Exception as e:
            print(f"Error fetching data for {city}: {e}")
            return None
    
    def is_duplicate_entry(self, city: str, data: List[Dict[str, Any]]) -> bool:
        """
        Checks if there is a recent (within 2 hours) entry for the city in the existing data.
        Prevents redundant API calls for fresh data.
        """
        if not data:
            return False
        
        current_time = datetime.now()
        two_hours_ago = current_time - timedelta(hours=2)
        
        for entry in reversed(data):
            if entry['city'].lower() == city.lower():
                entry_time = datetime.fromisoformat(entry['local_timestamp'])
                if entry_time > two_hours_ago:
                    return True
        return False
    
    async def fetch_and_log_weather(self, cities: List[str], force_update: bool = False) -> None:
        """
        Fetches weather data asynchronously for a list of cities and logs them to JSON.
        Skips cities with recent data unless force_update=True.
        """
        print(f"Fetching weather data for: {', '.join(cities)}")
        
        data = self.load_data()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for city in cities:
                if force_update or not self.is_duplicate_entry(city, data):
                    tasks.append(self.fetch_weather_data(session, city))
                else:
                    print(f"Skipping {city}: Recent data exists (within 2 hours)")
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, dict) and result:
                        data.append(result)
                        print(f" Logged data for {result['city']}: {result['temperature']}°C, {result['description']}")                        
                        self.view_all_logs(city=result['city'])
                    elif isinstance(result, Exception):
                        print(f"Error: {result}")
                
                self.save_data(data)
                print(f"\nTotal entries in database: {len(data)}")
            else:
                print("No new data to fetch (all cities have recent entries)")
    
    def load_data(self) -> List[Dict[str, Any]]:
        """
        Loads weather data from the JSON file.
        Returns an empty list if file doesn't exist or is corrupted.
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Warning: Corrupted JSON file, starting fresh")
                return []
        return []
    
    def save_data(self, data: List[Dict[str, Any]]) -> None:
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def view_all_logs(self, city=None) -> None:
        """
        Displays the last 20 weather log entries in a formatted table using tabulate.
        Shows city, temperature, description, humidity, and local timestamp.
        """
        data = self.load_data()
        if not data:
            print("No weather data available.")
            return
        
        table_data = []
        for entry in data[-20:]:
            if city and entry['city'] == city:
                table_data.append([
                entry['city'],
                f"{entry['temperature']:.1f}°C",
                entry['description'],
                f"{entry['humidity']}%",
                datetime.fromisoformat(entry['local_timestamp']).strftime('%Y-%m-%d %H:%M')
            ])
                   
            # table_data.append([
            #     entry['city'],
            #     f"{entry['temperature']:.1f}°C",
            #     entry['description'],
            #     f"{entry['humidity']}%",
            #     datetime.fromisoformat(entry['local_timestamp']).strftime('%Y-%m-%d %H:%M')
            # ])
        
        headers = ["City", "Temperature", "Description", "Humidity", "Local Time"]
        print("\n" + "="*80)
        print("RECENT WEATHER LOGS (Last 20 entries)")
        print("="*80)
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\nTotal entries: {len(data)}")
    
    def get_city_averages(self) -> None:
        """
        Calculates and displays average temperature and count of data points per city.
        Sorted by average temperature ascending.
        """
        data = self.load_data()
        if not data:
            print("No weather data available.")
            return
        
        city_data = {}
        for entry in data:
            city = entry['city']
            if city not in city_data:
                city_data[city] = []
            city_data[city].append(entry['temperature'])
        
        averages = []
        for city, temps in city_data.items():
            avg_temp = sum(temps) / len(temps)
            count = len(temps)
            averages.append([city, f"{avg_temp:.1f}°C", count])
        
        averages.sort(key=lambda x: float(x[1].replace('°C', '')))
        
        print("\n" + "="*60)
        print("CITY-WISE AVERAGE TEMPERATURES")
        print("="*60)
        headers = ["City", "Average Temperature", "Data Points"]
        print(tabulate(averages, headers=headers, tablefmt="grid"))
    
    def get_extremes(self) -> None:
        """
        Finds and displays hottest and coldest cities overall and in the last 24 hours.
        """
        data = self.load_data()
        if not data:
            print("No weather data available.")
            return
        
        all_temps = [(entry['city'], entry['temperature']) for entry in data]
        hottest_overall = max(all_temps, key=lambda x: x[1])
        coldest_overall = min(all_temps, key=lambda x: x[1])
        
        current_time = datetime.now()
        one_day_ago = current_time - timedelta(hours=24)
        
        recent_data = [
            (entry['city'], entry['temperature']) 
            for entry in data 
            if datetime.fromisoformat(entry['local_timestamp']) > one_day_ago
        ]
        
        if recent_data:
            hottest_24h = max(recent_data, key=lambda x: x[1])
            coldest_24h = min(recent_data, key=lambda x: x[1])
        else:
            hottest_24h = coldest_24h = ("No data", 0)
        
        print("\n" + "="*70)
        print("TEMPERATURE EXTREMES")
        print("="*70)
        print(f" Hottest city (overall): {hottest_overall[0]} ({hottest_overall[1]:.1f}°C)")
        print(f" Coldest city (overall): {coldest_overall[0]} ({coldest_overall[1]:.1f}°C)")
        print(f" Hottest city (last 24h): {hottest_24h[0]} ({hottest_24h[1]:.1f}°C)")
        print(f" Coldest city (last 24h): {coldest_24h[0]} ({coldest_24h[1]:.1f}°C)")
    
    def plot_temperature_trend(self, city: str) -> None:
        """
        Plots temperature trend over time for a specific city using matplotlib.
        Saves plot to 'plots' directory and displays it.
        """
        data = self.load_data()
        if not data:
            print("No weather data available.")
            return
        
        city_data = [
            entry for entry in data 
            if entry['city'].lower() == city.lower()
        ]
        
        if not city_data:
            print(f"No data available for {city}")
            return
        
        dates = [datetime.fromisoformat(entry['local_timestamp']) for entry in city_data]
        temperatures = [entry['temperature'] for entry in city_data]
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, temperatures, marker='o', linewidth=2, markersize=6)
        plt.title(f'Temperature Trend for {city}', fontsize=16, fontweight='bold')
        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Temperature (°C)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plot_filename = f"plots/{city.lower().replace(' ', '_')}_temp_trend.png"
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f" Temperature trend plot saved as: {plot_filename}")
    
    def export_to_sqlite(self) -> None:
        """
        Exports all weather data from JSON file to SQLite database.
        Uses INSERT OR IGNORE to prevent duplicate entries.
        """
        data = self.load_data()
        if not data:
            print("No data to export.")
            return
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        for entry in data:
            cursor.execute('''
                INSERT OR IGNORE INTO weather_logs 
                (city, temperature, description, humidity, utc_timestamp, local_timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                entry['city'],
                entry['temperature'],
                entry['description'],
                entry['humidity'],
                entry['utc_timestamp'],
                entry['local_timestamp']
            ))
        
        conn.commit()
        conn.close()
        print(f" Data exported to SQLite database: {self.db_file}")

def main():
    parser = argparse.ArgumentParser(description="Asynchronous Weather Logger & Analyzer")
    parser.add_argument("--api-key", default="1ad12a39d23d5f727c101cae5ca4321f", help="OpenWeatherMap API key")
    parser.add_argument("--cities", help="Comma-separated list of cities")
    parser.add_argument("--plot", help="Plot temperature trend for a specific city")
    parser.add_argument("--export-sqlite", action="store_true", help="Export data to SQLite")
    
    args = parser.parse_args()
    
    logger = WeatherLogger(args.api_key)
    
    if args.cities:
        cities = [city.strip() for city in args.cities.split(",")]
        asyncio.run(logger.fetch_and_log_weather(cities))
        return
    
    if args.plot:
        logger.plot_temperature_trend(args.plot)
        return
    
    if args.export_sqlite:
        logger.export_to_sqlite()
        return
    
    while True:
        print("\n" + "="*50)
        print("=== Weather Analyzer CLI ===")
        print("="*50)
        print("1. Fetch and log weather for cities")
        print("2. View all logs (as table)")
        print("3. Get city-wise average temperature")
        print("4. Show hottest and coldest cities")
        print("5. Plot temperature trend for a city")
        print("6. Export data to SQLite")
        print("7. Exit")
        print("-"*50)
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            cities_input = input("Enter comma-separated city names: ").strip()
            if cities_input:
                cities = [city.strip() for city in cities_input.split(",")]
                asyncio.run(logger.fetch_and_log_weather(cities))
            else:
                print("No cities entered.")
        
        elif choice == "2":
            logger.view_all_logs()
        
        elif choice == "3":
            logger.get_city_averages()
        
        elif choice == "4":
            logger.get_extremes()
        
        elif choice == "5":
            city = input("Enter city name: ").strip()
            if city:
                logger.plot_temperature_trend(city)
            else:
                print("No city entered.")
        
        elif choice == "6":
            logger.export_to_sqlite()
        
        elif choice == "7":
            print("Goodbye! ")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1-7.")

if __name__ == "__main__":
    main()
