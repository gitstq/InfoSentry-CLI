"""
USGS Earthquake data source
"""

from typing import Dict, Any, List
from datetime import datetime
from .base import BaseSource
from ..utils.http import get


class EarthquakeSource(BaseSource):
    """USGS Earthquake data source"""
    
    name = "earthquake"
    description = "USGS Earthquake real-time data"
    
    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch earthquake data from USGS"""
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
        """Parse USGS GeoJSON data"""
        items = []
        features = raw_data.get('features', [])
        
        for feature in features:
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})
            coords = geom.get('coordinates', [0, 0])
            
            magnitude = props.get('mag', 0)
            severity = self._get_severity(magnitude)
            
            item = {
                'id': feature.get('id', ''),
                'timestamp': datetime.fromtimestamp(props.get('time', 0) / 1000).isoformat(),
                'title': f"M{magnitude:.1f} - {props.get('place', 'Unknown')}",
                'description': f"Earthquake magnitude {magnitude} at {props.get('place', 'Unknown')}",
                'location': {
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'depth': coords[2] if len(coords) > 2 else 0
                },
                'severity': severity,
                'magnitude': magnitude,
                'place': props.get('place', 'Unknown'),
                'url': props.get('url', ''),
                'felt': props.get('felt', 0),
                'tsunami': props.get('tsunami', 0),
                'tags': ['earthquake', 'natural_disaster', severity]
            }
            items.append(self.standardize_item(item))
        
        return items
    
    def _get_severity(self, magnitude: float) -> str:
        """Determine severity level from magnitude"""
        if magnitude >= 7.0:
            return 'critical'
        elif magnitude >= 6.0:
            return 'high'
        elif magnitude >= 5.0:
            return 'medium'
        elif magnitude >= 4.0:
            return 'low'
        return 'info'
