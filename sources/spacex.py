"""
SpaceX launch data source
"""

from typing import Dict, Any, List
from datetime import datetime
from .base import BaseSource
from ..utils.http import get


class SpaceXSource(BaseSource):
    """SpaceX launch data source"""
    
    name = "spacex"
    description = "SpaceX upcoming launches and missions"
    
    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch SpaceX launch data"""
        if not self.enabled:
            return []
        
        try:
            response = get(self.url, timeout=self.timeout)
            if response.ok:
                return self.parse(response.json())
        except Exception:
            pass
        return []
    
    def parse(self, raw_data: List) -> List[Dict[str, Any]]:
        """Parse SpaceX launch data"""
        items = []
        
        for launch in raw_data[:5]:  # Get next 5 launches
            launch_id = launch.get('id', '')
            name = launch.get('name', 'Unknown Mission')
            date_str = launch.get('date_utc', '')
            details = launch.get('details', '')
            rocket = launch.get('rocket', '')
            launchpad = launch.get('launchpad', '')
            
            # Parse date
            try:
                launch_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                days_until = (launch_date - datetime.now(launch_date.tzinfo)).days
            except Exception:
                launch_date = datetime.now()
                days_until = 0
            
            # Determine severity based on proximity
            if days_until <= 1:
                severity = 'high'
            elif days_until <= 7:
                severity = 'medium'
            else:
                severity = 'info'
            
            # Get launchpad info
            pad_name = self._get_launchpad_name(launchpad)
            
            item = {
                'id': launch_id,
                'timestamp': launch_date.isoformat(),
                'title': f"🚀 SpaceX: {name}",
                'description': details or f"Upcoming SpaceX launch from {pad_name}",
                'location': {
                    'launchpad': pad_name
                },
                'severity': severity,
                'mission_name': name,
                'launch_date': date_str,
                'days_until': days_until,
                'rocket': rocket,
                'launchpad': pad_name,
                'links': launch.get('links', {}),
                'tags': ['spacex', 'launch', 'space', severity]
            }
            items.append(self.standardize_item(item))
        
        return items
    
    def _get_launchpad_name(self, launchpad_id: str) -> str:
        """Get launchpad name from ID"""
        # Known launchpads
        pads = {
            '5e9e4502f509094188566f88': 'CCAFS SLC 40',
            '5e9e4501f509094ba4566f84': 'KSC LC 39A',
            '5e9e4502f509092b78566f87': 'VAFB SLC 4E',
            '5e9e4502f5090995de566f86': 'Kwajalein Atoll',
            '5e9e4502f509094188566f89': 'CCAFS SLC 40 (old)',
            '5e9e4502f5090927f8566f85': 'STLS'
        }
        return pads.get(launchpad_id, launchpad_id)
