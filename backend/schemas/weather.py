"""
Weather schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional



# Response Schema
class WeatherResponse(BaseModel):
    """Response schema for weather data"""
    temperature: Optional[float] = None
    humidity: Optional[int] = None
    pressure: Optional[float] = None
    description: Optional[str] = None
    icon_code: Optional[str] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[int] = None
    visibility: Optional[int] = None
    data_timestamp: str
    location: str
    units: str 