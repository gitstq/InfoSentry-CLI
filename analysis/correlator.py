"""
Data correlation engine for finding relationships between intelligence items
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime
from collections import defaultdict


class DataCorrelator:
    """Correlate data from multiple sources"""
    
    def __init__(self):
        self.correlations = []
    
    def correlate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find correlations between items"""
        correlations = []
        
        # Group by location proximity
        location_groups = self._group_by_location(items)
        for group in location_groups:
            if len(group) > 1:
                correlations.append({
                    'type': 'location_proximity',
                    'items': group,
                    'confidence': len(group) / 10,
                    'description': f"{len(group)} events in geographic proximity"
                })
        
        # Group by time proximity
        time_groups = self._group_by_time(items)
        for group in time_groups:
            if len(group) > 1:
                correlations.append({
                    'type': 'temporal_proximity',
                    'items': group,
                    'confidence': len(group) / 10,
                    'description': f"{len(group)} events within 1 hour"
                })
        
        # Cross-source correlations
        cross_source = self._find_cross_source(items)
        correlations.extend(cross_source)
        
        return correlations
    
    def _group_by_location(self, items: List[Dict], radius_km: float = 100) -> List[List[Dict]]:
        """Group items by geographic proximity"""
        from ..utils.parser import GeoUtils
        
        groups = []
        processed = set()
        
        for i, item1 in enumerate(items):
            if i in processed:
                continue
            
            loc1 = item1.get('location', {})
            lat1 = loc1.get('latitude')
            lon1 = loc1.get('longitude')
            
            if lat1 is None or lon1 is None:
                continue
            
            group = [item1]
            processed.add(i)
            
            for j, item2 in enumerate(items[i+1:], start=i+1):
                if j in processed:
                    continue
                
                loc2 = item2.get('location', {})
                lat2 = loc2.get('latitude')
                lon2 = loc2.get('longitude')
                
                if lat2 is None or lon2 is None:
                    continue
                
                distance = GeoUtils.haversine_distance(lat1, lon1, lat2, lon2)
                if distance <= radius_km:
                    group.append(item2)
                    processed.add(j)
            
            if len(group) > 1:
                groups.append(group)
        
        return groups
    
    def _group_by_time(self, items: List[Dict], hours: int = 1) -> List[List[Dict]]:
        """Group items by temporal proximity"""
        from ..utils.parser import DataParser
        
        groups = []
        processed = set()
        
        for i, item1 in enumerate(items):
            if i in processed:
                continue
            
            ts1 = DataParser.parse_timestamp(item1.get('timestamp'))
            if not ts1:
                continue
            
            group = [item1]
            processed.add(i)
            
            for j, item2 in enumerate(items[i+1:], start=i+1):
                if j in processed:
                    continue
                
                ts2 = DataParser.parse_timestamp(item2.get('timestamp'))
                if not ts2:
                    continue
                
                diff = abs((ts2 - ts1).total_seconds()) / 3600
                if diff <= hours:
                    group.append(item2)
                    processed.add(j)
            
            if len(group) > 1:
                groups.append(group)
        
        return groups
    
    def _find_cross_source(self, items: List[Dict]) -> List[Dict]:
        """Find correlations across different data sources"""
        correlations = []
        
        # Group by source
        by_source = defaultdict(list)
        for item in items:
            source = item.get('source', 'unknown')
            by_source[source].append(item)
        
        # Look for patterns across sources
        sources = list(by_source.keys())
        for i, s1 in enumerate(sources):
            for s2 in sources[i+1:]:
                # Check for geographic overlap
                loc_overlap = self._check_location_overlap(
                    by_source[s1], by_source[s2]
                )
                if loc_overlap:
                    correlations.append({
                        'type': 'cross_source_location',
                        'sources': [s1, s2],
                        'confidence': loc_overlap['confidence'],
                        'description': f"Geographic correlation between {s1} and {s2}",
                        'details': loc_overlap
                    })
        
        return correlations
    
    def _check_location_overlap(self, items1: List[Dict], items2: List[Dict]) -> Dict:
        """Check for location overlap between two item sets"""
        from ..utils.parser import GeoUtils
        
        overlaps = []
        for item1 in items1:
            loc1 = item1.get('location', {})
            lat1 = loc1.get('latitude')
            lon1 = loc1.get('longitude')
            
            if lat1 is None or lon1 is None:
                continue
            
            for item2 in items2:
                loc2 = item2.get('location', {})
                lat2 = loc2.get('latitude')
                lon2 = loc2.get('longitude')
                
                if lat2 is None or lon2 is None:
                    continue
                
                distance = GeoUtils.haversine_distance(lat1, lon1, lat2, lon2)
                if distance <= 200:  # 200km threshold
                    overlaps.append({
                        'item1': item1,
                        'item2': item2,
                        'distance': distance
                    })
        
        if overlaps:
            avg_distance = sum(o['distance'] for o in overlaps) / len(overlaps)
            confidence = max(0.1, 1 - (avg_distance / 200))
            return {
                'confidence': confidence,
                'count': len(overlaps),
                'avg_distance': avg_distance,
                'overlaps': overlaps
            }
        
        return None
