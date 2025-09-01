"""
Weather Data Scheduler
Automatically fetches weather data for specified cities at regular intervals.
"""

import asyncio
import schedule
import time
from datetime import datetime
from typing import List
from weather_logger import WeatherLogger

class WeatherScheduler:
    def __init__(self, api_key: str, cities: List[str], interval_minutes: int = 1):
        # Initialize WeatherScheduler with API key, list of cities, and fetch interval
        self.logger = WeatherLogger(api_key)
        self.cities = cities
        self.interval_minutes = interval_minutes
        self.is_running = False
    
    async def scheduled_fetch(self):
        print(f"\n Scheduled fetch at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await self.logger.fetch_and_log_weather(self.cities, force_update=True)
    
    def start_scheduler(self):
        # Start the scheduling loop and run the fetch task at defined intervals
        print("Starting weather scheduler...")
        print(f" Cities: {', '.join(self.cities)}")
        print(f" Interval: Every {self.interval_minutes} minutes")
        print("Press Ctrl+C to stop the scheduler")
        
        schedule.every(self.interval_minutes).minutes.do(
            lambda: asyncio.run(self.scheduled_fetch())
        )
        
        self.is_running = True
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n Scheduler stopped by user")
            self.is_running = False
    
    def stop_scheduler(self):
        # Method to stop the scheduler manually if needed
        self.is_running = False
        print(" Scheduler stopped")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Weather Data Scheduler")
    parser.add_argument("--api-key", default="1ad12a39d23d5f727c101cae5ca4321f", help="OpenWeatherMap API key")
    parser.add_argument("--cities", required=True, help="Comma-separated list of cities")
    parser.add_argument("--interval", type=int, default=1, help="Fetch interval in minutes (default: 1)")
    
    args = parser.parse_args()
    # Parse and clean city names into a list
    cities = [city.strip() for city in args.cities.split(",")]
    
    scheduler = WeatherScheduler(args.api_key, cities, args.interval)
    scheduler.start_scheduler()

if __name__ == "__main__":
    main()
