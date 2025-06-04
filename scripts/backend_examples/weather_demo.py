#!/usr/bin/env python3
"""
Weather System Demo for Visual DM

This script demonstrates the usage of the time and weather system in Visual DM.
It manually creates instances of the time manager and weather service, then
simulates time passage to observe weather changes.

Run this script to see weather transitions as time advances.
"""

import sys
import os
import time
import random
from pathlib import Path

# Add parent directory to path so we can import from backend
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

try:
    from backend.systems.game_time.services.time_manager import TimeManager
    from backend.systems.game_time.models.calendar_model import Season
    from backend.systems.game_time.models.weather_model import WeatherState
except ImportError:
    print("Error: Could not import required modules.")
    print("Make sure you are running this script from the project root directory.")
    sys.exit(1)

def display_weather(weather_data):
    """Display weather information in a formatted way"""
    weather_emoji = {
        WeatherState.CLEAR: "☀️",
        WeatherState.PARTLY_CLOUDY: "⛅",
        WeatherState.OVERCAST: "☁️",
        WeatherState.LIGHT_RAIN: "🌦️",
        WeatherState.HEAVY_RAIN: "🌧️",
        WeatherState.STORM: "⛈️",
        WeatherState.SNOW: "❄️",
        WeatherState.BLIZZARD: "🌨️",
        WeatherState.FOG: "🌫️",
        WeatherState.WINDY: "💨"
    }
    
    emoji = weather_emoji.get(weather_data.weather_state, "❓")
    
    print(f"\n{emoji} Current Weather: {weather_data.weather_state.value}")
    print(f"🌡️ Temperature: {weather_data.temperature}°C")
    print(f"🏞️ Season: {weather_data.season.value}")
    
    if weather_data.humidity is not None:
        print(f"💧 Humidity: {weather_data.humidity}%")
    if weather_data.wind_speed is not None:
        print(f"💨 Wind Speed: {weather_data.wind_speed} km/h")
    if weather_data.precipitation_chance is not None:
        print(f"🌧️ Precipitation Chance: {weather_data.precipitation_chance}%")
    
    print("-" * 40)

def display_calendar(calendar_data):
    """Display calendar information in a formatted way"""
    print(f"📅 Date: {calendar_data.current_day} {calendar_data.current_month.value} {calendar_data.current_year}")
    print(f"🕒 Time: {calendar_data.current_hour:02d}:{calendar_data.current_minute:02d}")
    print(f"🌞 Day of Week: {calendar_data.get_current_day_of_week().value}")
    print(f"🍂 Season: {calendar_data.current_season.value}")

def main():
    """Run the weather system demo"""
    print("\n=== Visual DM Weather System Demo ===\n")
    
    # Create a time manager instance
    time_manager = TimeManager()
    
    # Display initial state
    print("Initial State:")
    display_calendar(time_manager.calendar)
    display_weather(time_manager.weather_service.get_current_weather())
    
    # Ask user how many days to simulate
    try:
        days_to_simulate = int(input("\nHow many days would you like to simulate? (1-30): "))
        days_to_simulate = max(1, min(days_to_simulate, 30))  # Clamp between 1 and 30
    except ValueError:
        days_to_simulate = 7  # Default to 7 days
        print("Invalid input. Using default of 7 days.")
    
    print(f"\nSimulating {days_to_simulate} days of weather...\n")
    
    # Simulate specified number of days
    for day in range(1, days_to_simulate + 1):
        print(f"\n--- Day {day} of {days_to_simulate} ---")
        
        # Advance time by 24 hours (1440 minutes)
        changes = time_manager.advance_time(1440)
        
        # Display calendar information
        display_calendar(time_manager.calendar)
        
        # Display weather information
        display_weather(time_manager.weather_service.get_current_weather())
        
        # List any significant changes
        if changes:
            print("\nSignificant changes:")
            for change_type, change_data in changes.items():
                if change_type != "weather_changed":  # We already display weather separately
                    print(f"- {change_type}: {change_data}")
        
        # Pause between days
        if day < days_to_simulate:
            time.sleep(1)
    
    print("\n=== Simulation Complete ===\n")

if __name__ == "__main__":
    main() 