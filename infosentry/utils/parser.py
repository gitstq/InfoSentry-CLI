"""
Data parsing utilities
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional


class DataParser:
    """Generic data parser"""
    
    @staticmethod
    def parse_timestamp(ts: Any) -> Optional[datetime]:
        """Parse various timestamp formats"""
        if ts is None:
            return None
        
        if isinstance(ts, datetime):
            return ts
        
        if isinstance(ts, (int, float)):
            # Assume milliseconds if large number
            if ts > 1e10:
                ts = ts / 1000
            return datetime.fromtimestamp(ts)
        
        if isinstance(ts, str):
            formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y %H:%M:%S',
                '%m/%d/%Y %H:%M:%S'
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(ts, fmt)
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def extract_coordinates(text: str) -> Optional[tuple]:
        """Extract latitude/longitude from text"""
        # Pattern: lat, lon or lat lon
        patterns = [
            r'(-?\d+\.?\d*)[°,\s]+(-?\d+\.?\d*)',
            r'lat[:\s]+(-?\d+\.?\d*)[°,\s]+lon[:\s]+(-?\d+\.?\d*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return (float(match.group(1)), float(match.group(2)))
        return None
    
    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Sanitize string for use as filename"""
        return re.sub(r'[^\w\-_.]', '_', name)
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_number(num: float, precision: int = 2) -> str:
        """Format number with appropriate suffix"""
        if num >= 1e9:
            return f"{num/1e9:.{precision}f}B"
        if num >= 1e6:
            return f"{num/1e6:.{precision}f}M"
        if num >= 1e3:
            return f"{num/1e3:.{precision}f}K"
        return f"{num:.{precision}f}"
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        if seconds < 3600:
            return f"{int(seconds/60)}m"
        if seconds < 86400:
            return f"{int(seconds/3600)}h"
        return f"{int(seconds/86400)}d"


class GeoUtils:
    """Geographic utilities"""
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        import math
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    @staticmethod
    def get_cardinal_direction(degrees: float) -> str:
        """Convert degrees to cardinal direction"""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = round(degrees / 22.5) % 16
        return directions[index]
