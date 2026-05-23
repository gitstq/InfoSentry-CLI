"""
Aviation tracking data source (OpenSky Network)
"""

from typing import Dict, Any, List
from datetime import datetime
from .base import BaseSource
from ..utils.http import get


class AviationSource(BaseSource):
    """Aviation tracking data source"""
    
    name = "aviation"
    description = "Real-time aviation tracking data"
    
    # OpenSky field mapping
    FIELD_MAP = {
        'icao24': 0,      # ICAO24 address
        'callsign': 1,    # Callsign
        'origin_country': 2,
        'time_position': 3,
        'last_contact': 4,
        'longitude': 5,
        'latitude': 6,
        'altitude': 7,    # Barometric altitude (m)
        'on_ground': 8,
        'velocity': 9,    # m/s
        'heading': 10,    # degrees
        'vertical_rate': 11,  # m/s
        'sensors': 12,
        'geo_altitude': 13,
        'squawk': 14,
        'spi': 15,
        'position_source': 16
    }
    
    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch aviation data"""
        if not self.enabled:
            return []
        
        try:
            response = get(self.url, timeout=self.timeout)
            if response.ok:
                return self.parse(response.json())
        except Exception:
            pass
        return []
    
    def parse(self, raw_data: Dict) -> List[Dict[str, Any]]:
        """Parse OpenSky states data"""
        items = []
        states = raw_data.get('states', []) or []
        
        for state in states:
            if not state:
                continue
            
            callsign = self._get_field(state, 'callsign', '').strip()
            icao24 = self._get_field(state, 'icao24', '')
            country = self._get_field(state, 'origin_country', 'Unknown')
            lat = self._get_field(state, 'latitude')
            lon = self._get_field(state, 'longitude')
            altitude = self._get_field(state, 'altitude', 0)
            velocity = self._get_field(state, 'velocity', 0)
            heading = self._get_field(state, 'heading', 0)
            
            if lat is None or lon is None:
                continue
            
            # Calculate severity based on unusual patterns
            severity = self._analyze_flight_pattern(state)
            
            item = {
                'id': icao24,
                'timestamp': datetime.now().isoformat(),
                'title': f"✈️ {callsign or icao24} ({country})",
                'description': f"Aircraft at {altitude:.0f}m, {velocity*3.6:.0f} km/h, heading {heading:.0f}°",
                'location': {
                    'latitude': lat,
                    'longitude': lon,
                    'altitude': altitude
                },
                'severity': severity,
                'callsign': callsign,
                'icao24': icao24,
                'country': country,
                'altitude': altitude,
                'velocity': velocity,
                'heading': heading,
                'on_ground': self._get_field(state, 'on_ground', False),
                'tags': ['aviation', 'tracking', 'aircraft']
            }
            items.append(self.standardize_item(item))
        
        # Limit to most interesting flights
        items.sort(key=lambda x: x.get('altitude', 0), reverse=True)
        return items[:50]
    
    def _get_field(self, state: List, field: str, default=None):
        """Get field from state array by name"""
        idx = self.FIELD_MAP.get(field)
        if idx is not None and idx < len(state):
            return state[idx] if state[idx] is not None else default
        return default
    
    def _analyze_flight_pattern(self, state: List) -> str:
        """Analyze flight pattern for anomalies"""
        altitude = self._get_field(state, 'altitude', 0)
        velocity = self._get_field(state, 'velocity', 0)
        vertical_rate = self._get_field(state, 'vertical_rate', 0)
        
        # Emergency descent
        if vertical_rate < -10 and altitude > 3000:
            return 'high'
        
        # Very low altitude for non-ground aircraft
        if altitude < 100 and not self._get_field(state, 'on_ground', False):
            return 'medium'
        
        # Unusual speed at low altitude
        if velocity > 150 and altitude < 500:
            return 'medium'
        
        return 'info'
