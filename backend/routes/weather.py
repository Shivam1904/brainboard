"""
Weather routes for direct weather data retrieval.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from services.weather_service import WeatherService
from schemas.weather import WeatherResponse

router = APIRouter()

@router.get("/", response_model=WeatherResponse)
async def get_weather(
    lat: float,
    lon: float,
    units: str = "metric"
):
    """Get current weather for coordinates."""
    try:
        service = WeatherService()
        result = await service.get_weather(lat, lon, units)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather: {str(e)}")

 