import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { DailyWidget, apiService } from '../../services/api';

interface WeatherData {
  temperature: number;
  humidity: number;
  pressure: number;
  description: string;
  icon_code: string;
  wind_speed: number;
  wind_direction: number;
  visibility: number;
  data_timestamp: string;
  location: string;
  units: string;
}

interface WeatherWidgetProps {
  widget: DailyWidget;
  onRemove: () => void;
}

const WeatherWidget: React.FC<WeatherWidgetProps> = ({ onRemove }) => {
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [location, setLocation] = useState<{ lat: number; lon: number } | null>(null);

  // Get weather icon based on icon code
  const getWeatherIcon = (iconCode: string, description: string): string => {
    const code = parseInt(iconCode);
    
    // Clear sky
    if (code === 0) return '☀️';
    
    // Partly cloudy
    if (code >= 1 && code <= 3) return '⛅️';
    
    // Cloudy
    if (code >= 4 && code <= 6) return '☁️';
    
    // Rain
    if (code >= 7 && code <= 19) return '🌧️';
    
    // Snow
    if (code >= 20 && code <= 29) return '❄️';
    
    // Thunderstorm
    if (code >= 30 && code <= 39) return '⛈️';
    
    // Fog
    if (code >= 40 && code <= 49) return '🌫️';
    
    // Default based on description
    const desc = description.toLowerCase();
    if (desc.includes('clear')) return '☀️';
    if (desc.includes('cloud')) return '☁️';
    if (desc.includes('rain')) return '🌧️';
    if (desc.includes('snow')) return '❄️';
    if (desc.includes('thunder')) return '⛈️';
    if (desc.includes('fog') || desc.includes('mist')) return '🌫️';
    
    return '🌤️';
  };

  // Get wind direction arrow
  const getWindDirection = (degrees: number): string => {
    const directions = ['↑', '↗️', '→', '↘️', '↓', '↙️', '←', '↖️'];
    const index = Math.round(degrees / 45) % 8;
    return directions[index];
  };

  // Format temperature
  const formatTemperature = (temp: number, units: string): string => {
    const rounded = Math.round(temp);
    return `${rounded}°${units === 'metric' ? 'C' : 'F'}`;
  };

  // Format wind speed
  const formatWindSpeed = (speed: number, units: string): string => {
    const rounded = Math.round(speed * 10) / 10;
    return `${rounded} ${units === 'metric' ? 'm/s' : 'mph'}`;
  };

  // Format visibility
  const formatVisibility = (visibility: number, units: string): string => {
    if (units === 'metric') {
      return visibility >= 1000 ? `${Math.round(visibility / 1000)} km` : `${visibility} m`;
    } else {
      const miles = visibility * 0.000621371;
      return miles >= 1 ? `${Math.round(miles * 10) / 10} mi` : `${Math.round(visibility * 3.28084)} ft`;
    }
  };

  // Get user location
  const getUserLocation = (): Promise<{ lat: number; lon: number }> => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser.'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lon: position.coords.longitude
          });
        },
        (_error) => {
          reject(new Error('Unable to retrieve your location.'));
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000 // 5 minutes
        }
      );
    });
  };

  // Fetch weather data
  const fetchWeatherData = async (lat: number, lon: number) => {
    try {
      setLoading(true);
      setError(null);
      
      const data: WeatherData = await apiService.getWeather(lat, lon, 'metric');
      setWeatherData(data);
    } catch (err) {
      console.error('Failed to fetch weather data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch weather data');
    } finally {
      setLoading(false);
    }
  };

  // Initialize location and fetch weather
  useEffect(() => {
    const initializeWeather = async () => {
      try {
        const userLocation = await getUserLocation();
        setLocation(userLocation);
        await fetchWeatherData(userLocation.lat, userLocation.lon);
      } catch (err) {
        console.error('Failed to get location:', err);
        setError('Unable to get your location. Please enable location services.');
        setLoading(false);
      }
    };

    initializeWeather();
  }, []);

  // Refresh weather data
  const handleRefresh = async () => {
    if (location) {
      await fetchWeatherData(location.lat, location.lon);
    }
  };

  return (
    <BaseWidget
      title="Weather"
      icon="⛅️"
      onRemove={onRemove}
      onRefresh={handleRefresh}
      loading={loading}
    >
      <div className="flex flex-col h-full p-4">
        {error ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="text-4xl mb-2">🌍</div>
            <p className="text-sm text-muted-foreground mb-2">Location Error</p>
            <p className="text-xs text-muted-foreground">{error}</p>
            <button
              onClick={handleRefresh}
              className="mt-2 px-3 py-1 text-xs bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Retry
            </button>
          </div>
        ) : weatherData ? (
          <div className="flex flex-col h-full">
            {/* Main weather display */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="text-4xl">
                  {getWeatherIcon(weatherData.icon_code, weatherData.description)}
                </div>
                <div>
                  <div className="text-2xl font-bold">
                    {formatTemperature(weatherData.temperature, weatherData.units)}
                  </div>
                  <div className="text-sm text-muted-foreground capitalize">
                    {weatherData.description}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-muted-foreground">
                  {new Date(weatherData.data_timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
            </div>

            {/* Weather details grid */}
            <div className="grid grid-cols-2 gap-3 flex-1">
              {/* Humidity */}
              <div className="bg-muted/50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">💧</span>
                  <span className="text-xs text-muted-foreground">Humidity</span>
                </div>
                <div className="text-sm font-medium">{weatherData.humidity}%</div>
              </div>

              {/* Wind */}
              <div className="bg-muted/50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">💨</span>
                  <span className="text-xs text-muted-foreground">Wind</span>
                </div>
                <div className="text-sm font-medium">
                  {getWindDirection(weatherData.wind_direction)} {formatWindSpeed(weatherData.wind_speed, weatherData.units)}
                </div>
              </div>

              {/* Pressure */}
              <div className="bg-muted/50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">📊</span>
                  <span className="text-xs text-muted-foreground">Pressure</span>
                </div>
                <div className="text-sm font-medium">{weatherData.pressure} hPa</div>
              </div>

              {/* Visibility */}
              <div className="bg-muted/50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg">👁️</span>
                  <span className="text-xs text-muted-foreground">Visibility</span>
                </div>
                <div className="text-sm font-medium">
                  {formatVisibility(weatherData.visibility, weatherData.units)}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
          </div>
        )}
      </div>
    </BaseWidget>
  );
};

export default WeatherWidget; 