"""
Pattern recognition for intelligence data
"""

import re
from typing import Dict, Any, List
from collections import Counter


class PatternAnalyzer:
    """Analyze patterns in intelligence data"""
    
    def __init__(self):
        self.patterns = []
    
    def analyze(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze items for patterns"""
        findings = []
        
        # Severity distribution
        severity_dist = self._analyze_severity_distribution(items)
        if severity_dist:
            findings.append({
                'type': 'severity_distribution',
                'data': severity_dist,
                'description': f"Severity distribution: {severity_dist}"
            })
        
        # Source distribution
        source_dist = self._analyze_source_distribution(items)
        if source_dist:
            findings.append({
                'type': 'source_distribution',
                'data': source_dist,
                'description': f"Data from {len(source_dist)} sources"
            })
        
        # Geographic hotspots
        hotspots = self._find_geographic_hotspots(items)
        if hotspots:
            findings.append({
                'type': 'geographic_hotspots',
                'data': hotspots,
                'description': f"{len(hotspots)} geographic hotspots identified"
            })
        
        # Temporal patterns
        temporal = self._analyze_temporal_patterns(items)
        if temporal:
            findings.append({
                'type': 'temporal_patterns',
                'data': temporal,
                'description': temporal.get('description', '')
            })
        
        # Keyword extraction
        keywords = self._extract_keywords(items)
        if keywords:
            findings.append({
                'type': 'keywords',
                'data': keywords,
                'description': f"Top keywords: {', '.join([k[0] for k in keywords[:5]])}"
            })
        
        return findings
    
    def _analyze_severity_distribution(self, items: List[Dict]) -> Dict[str, int]:
        """Analyze severity distribution"""
        severities = [item.get('severity', 'info') for item in items]
        return dict(Counter(severities))
    
    def _analyze_source_distribution(self, items: List[Dict]) -> Dict[str, int]:
        """Analyze source distribution"""
        sources = [item.get('source', 'unknown') for item in items]
        return dict(Counter(sources))
    
    def _find_geographic_hotspots(self, items: List[Dict], grid_size: float = 5.0) -> List[Dict]:
        """Find geographic hotspots using grid-based clustering"""
        from collections import defaultdict
        
        grid = defaultdict(list)
        
        for item in items:
            loc = item.get('location', {})
            lat = loc.get('latitude')
            lon = loc.get('longitude')
            
            if lat is None or lon is None:
                continue
            
            # Assign to grid cell
            grid_lat = round(lat / grid_size) * grid_size
            grid_lon = round(lon / grid_size) * grid_size
            grid[(grid_lat, grid_lon)].append(item)
        
        # Find cells with multiple items
        hotspots = []
        for (grid_lat, grid_lon), cell_items in grid.items():
            if len(cell_items) >= 2:
                hotspots.append({
                    'center': {'lat': grid_lat, 'lon': grid_lon},
                    'count': len(cell_items),
                    'items': cell_items
                })
        
        # Sort by count
        hotspots.sort(key=lambda x: x['count'], reverse=True)
        return hotspots[:5]
    
    def _analyze_temporal_patterns(self, items: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal patterns"""
        from ..utils.parser import DataParser
        from datetime import datetime
        
        timestamps = []
        for item in items:
            ts = DataParser.parse_timestamp(item.get('timestamp'))
            if ts:
                timestamps.append(ts)
        
        if not timestamps:
            return None
        
        timestamps.sort()
        
        # Calculate time span
        time_span = timestamps[-1] - timestamps[0]
        hours = time_span.total_seconds() / 3600
        
        # Group by hour
        hour_dist = Counter(ts.hour for ts in timestamps)
        peak_hour = hour_dist.most_common(1)[0]
        
        return {
            'time_span_hours': hours,
            'event_count': len(timestamps),
            'peak_hour': peak_hour[0],
            'peak_hour_events': peak_hour[1],
            'hour_distribution': dict(hour_dist),
            'description': f"{len(timestamps)} events over {hours:.1f}h, peak at {peak_hour[0]}:00"
        }
    
    def _extract_keywords(self, items: List[Dict], top_n: int = 10) -> List[tuple]:
        """Extract keywords from item descriptions"""
        # Common stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                      'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                      'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                      'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                      'through', 'during', 'before', 'after', 'above', 'below',
                      'between', 'under', 'and', 'but', 'or', 'yet', 'so', 'if',
                      'because', 'although', 'though', 'while', 'where', 'when',
                      'that', 'which', 'who', 'whom', 'whose', 'what', 'this',
                      'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
        # Extract words
        word_counts = Counter()
        
        for item in items:
            text = item.get('title', '') + ' ' + item.get('description', '')
            # Extract words
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            for word in words:
                if word not in stop_words:
                    word_counts[word] += 1
        
        return word_counts.most_common(top_n)
