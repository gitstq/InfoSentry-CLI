"""
Weather data source (Open-Meteo)
"""

from typing import Dict, Any, List
from datetime import datetime
from .base import BaseSource
from ..utils.http import get


class WeatherSource(BaseSource):
    """Weather data source"""
    
    name = "weather"
    description = "Global weather alerts and conditions"
    
    # Major cities for monitoring
    CITIES = [
        {'name': 'Beijing', 'lat': 39.9042, 'lon': 116.4074},
        {'name': 'Shanghai', 'lat': 31.2304, 'lon': 121.4737},
        {'name': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503},
        {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060},
        {'name': 'London', 'lat': 51.5074, 'lon': -0.1278},
        {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522},
        {'name': 'Sydney', 'lat': -33.8688, 'lon': 151.2093},
        {'name': 'Moscow', 'lat': 55.7558, 'lon': 37.6173},
        {'name': 'Dubai', 'lat': 25.2048, 'lon': 55.2708},
        {'name': 'Singapore', 'lat': 1.3521, 'lon': 103.8198}
    ]
    
    # WMO Weather interpretation codes
    WEATHER_CODES = {
        0: ('Clear sky', '☀️'),
        1: ('Mainly clear', '🌤️'),
        2: ('Partly cloudy', '⛅'),
        3: ('Overcast', '☁️'),
        45: ('Fog', '🌫️'),
        48: ('Depositing rime fog', '🌫️'),
        51: ('Light drizzle', '🌦️'),
        53: ('Moderate drizzle', '🌧️'),
        55: ('Dense drizzle', '🌧️'),
        61: ('Slight rain', '🌧️'),
        63: ('Moderate rain', '🌧️'),
        65: ('Heavy rain', '🌧️'),
        71: ('Slight snow', '🌨️'),
        73: ('Moderate snow', '🌨️'),
        75: ('Heavy snow', '🌨️'),
        77: ('Snow grains', '🌨️'),
        80: ('Slight rain showers', '🌦️'),
        81: ('Moderate rain showers', '🌧️'),
        82: ('Violent rain showers', '⛈️'),
        85: ('Slight snow showers', '🌨️'),
        86: ('Heavy snow showers', '🌨️'),
        95: ('Thunderstorm', '⛈️'),
        96: ('Thunderstorm with hail', '⛈️'),
        99: ('Thunderstorm with heavy hail', '⛈️')
    }
    
    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch weather data for major cities"""
        if not self.enabled:
            return []
        
        items = []
        for city in self.CITIES:
            try:
                url = f"{self.url}?latitude={city['lat']}&longitude={city['lon']}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m"
                response = get(url, timeout=self.timeout)
                if response.ok:
                    data = response.json()
                    item = self._parse_city_data(city, data)
                    if item:
                        items.append(item)
            except Exception:
                continue
        
        return items
    
    def parse(self, raw_data: Dict) -> List[Dict[str, Any]]:
        """Parse weather data (not used directly)"""
        return []
    
    def _parse_city_data(self, city: Dict, data: Dict) -> Dict[str, Any]:
        """Parse weather data for a city"""
        current = data.get('current', {})
        if not current:
            return None
        
        temp = current.get('temperature_2m', 0)
        humidity = current.get('relative_humidity_2m', 0)
        weather_code = current.get('weather_code', 0)
        wind_speed = current.get('wind_speed_10m', 0)
        
        weather_desc, weather_icon = self.WEATHER_CODES.get(weather_code, ('Unknown', '❓'))
        severity = self._get_severity(weather_code, temp, wind_speed)
        
        item = {
            'id': f"weather_{city['name'].lower()}",
            'timestamp': datetime.now().isoformat(),
            'title': f"{weather_icon} {city['name']}: {temp}°C, {weather_desc}",
            'description': f"Temperature: {temp}°C, Humidity: {humidity}%, Wind: {wind_speed} km/h",
            'location': {
                'latitude': city['lat'],
                'longitude': city['lon'],
                'city': city['name']
            },
            'severity': severity,
            'temperature': temp,
            'humidity': humidity,
            'weather_code': weather_code,
            'weather_description': weather_desc,
            'wind_speed': wind_speed,
            'tags': ['weather', city['name'].lower(), severity]
        }
        
        return self.standardize_item(item)
    
    def _get_severity(self, code: int, temp: float, wind: float) -> str:
        """Determine weather severity"""
        # Extreme temperatures
        if temp > 40 or temp < -20:
            return 'high'
        if temp > 35 or temp < -10:
            return 'medium'
        
        # Severe weather codes
        if code in [95, 96, 99]:  # Thunderstorms
            return 'high'
        if code in [82, 86]:  # Violent showers
            return 'medium'
        
        # High winds
        if wind > 50:
            return 'high'
        if wind > 30:
            return 'medium'
        
        return 'info'
