"""
Core intelligence engine
"""

from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import Config
from .cache import Cache
from ..sources import (
    EarthquakeSource, AviationSource, WeatherSource,
    SpaceXSource, CVESource
)
from ..analysis.correlator import DataCorrelator
from ..analysis.pattern import PatternAnalyzer


class InfoEngine:
    """Main intelligence engine"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.cache = Cache(self.config.cache_dir, self.config.cache_ttl)
        
        # Initialize sources
        self.sources = self._init_sources()
        
        # Initialize analyzers
        self.correlator = DataCorrelator()
        self.pattern_analyzer = PatternAnalyzer()
    
    def _init_sources(self) -> Dict[str, Any]:
        """Initialize data sources"""
        sources = {}
        source_config = self.config.get('sources', {})
        
        source_classes = {
            'earthquake': EarthquakeSource,
            'aviation': AviationSource,
            'weather': WeatherSource,
            'spacex': SpaceXSource,
            'cve': CVESource
        }
        
        for name, SourceClass in source_classes.items():
            config = source_config.get(name, {'enabled': True})
            if config.get('enabled', True):
                sources[name] = SourceClass(config)
        
        return sources
    
    def fetch_all(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Fetch data from all enabled sources"""
        all_items = []
        
        # Check cache first
        cache_key = "all_sources"
        if use_cache:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
        
        # Fetch from sources in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {
                executor.submit(source.fetch): name 
                for name, source in self.sources.items()
            }
            
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    items = future.result(timeout=30)
                    all_items.extend(items)
                except Exception as e:
                    # Source failed, continue with others
                    pass
        
        # Sort by timestamp (newest first)
        all_items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Cache results
        if use_cache:
            self.cache.set(cache_key, all_items)
        
        return all_items
    
    def fetch_source(self, source_name: str) -> List[Dict[str, Any]]:
        """Fetch data from a specific source"""
        source = self.sources.get(source_name)
        if not source:
            return []
        
        # Check cache
        cache_key = f"source_{source_name}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            items = source.fetch()
            self.cache.set(cache_key, items)
            return items
        except Exception:
            return []
    
    def analyze(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze items for correlations and patterns"""
        return {
            'correlations': self.correlator.correlate(items),
            'patterns': self.pattern_analyzer.analyze(items)
        }
    
    def get_stats(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about items"""
        from collections import Counter
        
        if not items:
            return {
                'total': 0,
                'by_source': {},
                'by_severity': {},
                'sources_active': len(self.sources)
            }
        
        sources = Counter(item.get('source', 'unknown') for item in items)
        severities = Counter(item.get('severity', 'info') for item in items)
        
        return {
            'total': len(items),
            'by_source': dict(sources),
            'by_severity': dict(severities),
            'sources_active': len(self.sources)
        }
    
    def filter_items(self, items: List[Dict[str, Any]], 
                     source: Optional[str] = None,
                     severity: Optional[str] = None,
                     keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """Filter items by criteria"""
        filtered = items
        
        if source:
            filtered = [i for i in filtered if i.get('source') == source]
        
        if severity:
            filtered = [i for i in filtered if i.get('severity') == severity]
        
        if keyword:
            keyword_lower = keyword.lower()
            filtered = [
                i for i in filtered 
                if keyword_lower in i.get('title', '').lower() 
                or keyword_lower in i.get('description', '').lower()
            ]
        
        return filtered
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
    
    def get_source_info(self) -> List[Dict[str, Any]]:
        """Get information about all sources"""
        return [source.get_metadata() for source in self.sources.values()]
