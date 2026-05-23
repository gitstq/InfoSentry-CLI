"""
Base class for data sources
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class BaseSource(ABC):
    """Abstract base class for intelligence sources"""
    
    name: str = "base"
    description: str = "Base source"
    enabled: bool = True
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.url = config.get('url', '')
        self.timeout = config.get('timeout', 30)
        self.enabled = config.get('enabled', True)
    
    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch data from source"""
        pass
    
    @abstractmethod
    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """Parse raw data into standardized format"""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get source metadata"""
        return {
            'name': self.name,
            'description': self.description,
            'enabled': self.enabled,
            'url': self.url,
            'last_fetch': datetime.now().isoformat()
        }
    
    def standardize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize item to common format"""
        return {
            'source': self.name,
            'timestamp': item.get('timestamp', datetime.now().isoformat()),
            'title': item.get('title', 'Untitled'),
            'description': item.get('description', ''),
            'location': item.get('location', {}),
            'severity': item.get('severity', 'info'),
            'data': item,
            'tags': item.get('tags', [])
        }
