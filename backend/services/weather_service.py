"""
Weather service for direct API calls to Open-Meteo.
No database operations, just pure API integration.
"""

import logging
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.open_meteo_base_url = "https://api.open-meteo.com/v1"

    async def get_weather(self, lat: float, lon: float, units: str = "metric") -> Dict[str, Any]:
        """Get current weather for coordinates."""
        try:
            # Convert units to Open-Meteo format
            temperature_unit = "celsius" if units == "metric" else "fahrenheit"
            
            # Build Open-Meteo URL with current weather parameters
            url = f"{self.open_meteo_base_url}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,pressure_msl,weather_code,wind_speed_10m,wind_direction_10m,visibility",
                "temperature_unit": temperature_unit,
                "wind_speed_unit": "ms" if units == "metric" else "mph",
                "timezone": "auto"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_open_meteo_data(data, f"{lat},{lon}", units)
                    else:
                        logger.error(f"Open-Meteo API error: {response.status}")
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error fetching weather from Open-Meteo API: {e}")
            return {"error": f"Failed to fetch weather data: {str(e)}"}
    
    def _parse_open_meteo_data(self, api_data: Dict[str, Any], location: str, units: str) -> Dict[str, Any]:
        """Parse weather data from Open-Meteo API response."""
        try:
            current = api_data.get("current", {})
            
            # Convert weather code to description
            weather_code = current.get("weather_code", 0)
            description = self._get_weather_description(weather_code)
            
            return {
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "pressure": current.get("pressure_msl"),
                "description": description,
                "icon_code": str(weather_code),  # Open-Meteo uses numeric codes
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "visibility": current.get("visibility"),
                "data_timestamp": datetime.now().isoformat(),
                "location": location,
                "units": units
            }
        except Exception as e:
            logger.error(f"Error parsing Open-Meteo weather data: {e}")
            return {"error": f"Failed to parse weather data: {str(e)}"}
    
    def _get_weather_description(self, weather_code: int) -> str:
        """Convert Open-Meteo weather code to description."""
        # Open-Meteo weather codes: https://open-meteo.com/en/docs
        weather_descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_descriptions.get(weather_code, "Unknown") 