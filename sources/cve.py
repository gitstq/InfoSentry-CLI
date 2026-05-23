"""
CVE (Common Vulnerabilities and Exposures) data source
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base import BaseSource
from ..utils.http import get


class CVESource(BaseSource):
    """CVE vulnerability data source"""
    
    name = "cve"
    description = "Latest cybersecurity vulnerabilities from NVD"
    
    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch recent CVE data"""
        if not self.enabled:
            return []
        
        try:
            # Get CVEs from last 7 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            params = {
                'pubStartDate': start_date.strftime('%Y-%m-%dT%H:%M:%S.000'),
                'pubEndDate': end_date.strftime('%Y-%m-%dT%H:%M:%S.000'),
                'resultsPerPage': 20
            }
            
            response = get(self.url, params=params, timeout=self.timeout)
            if response.ok:
                return self.parse(response.json())
        except Exception:
            pass
        return []
    
    def parse(self, raw_data: Dict) -> List[Dict[str, Any]]:
        """Parse CVE data"""
        items = []
        vulnerabilities = raw_data.get('vulnerabilities', [])
        
        for vuln in vulnerabilities:
            cve = vuln.get('cve', {})
            cve_id = cve.get('id', '')
            descriptions = cve.get('descriptions', [])
            
            # Get English description
            description = ''
            for desc in descriptions:
                if desc.get('lang') == 'en':
                    description = desc.get('value', '')
                    break
            
            # Get CVSS score
            metrics = cve.get('metrics', {})
            cvss_score = 0.0
            severity = 'info'
            
            if 'cvssMetricV31' in metrics:
                cvss_data = metrics['cvssMetricV31'][0].get('cvssData', {})
                cvss_score = cvss_data.get('baseScore', 0)
                severity = self._cvss_to_severity(cvss_score)
            elif 'cvssMetricV30' in metrics:
                cvss_data = metrics['cvssMetricV30'][0].get('cvssData', {})
                cvss_score = cvss_data.get('baseScore', 0)
                severity = self._cvss_to_severity(cvss_score)
            
            # Get published date
            published = cve.get('published', '')
            
            item = {
                'id': cve_id,
                'timestamp': published,
                'title': f"🔒 {cve_id} (CVSS: {cvss_score})",
                'description': description[:200] + '...' if len(description) > 200 else description,
                'location': {},
                'severity': severity,
                'cvss_score': cvss_score,
                'published': published,
                'references': [ref.get('url', '') for ref in cve.get('references', [])[:3]],
                'tags': ['cybersecurity', 'vulnerability', 'cve', severity]
            }
            items.append(self.standardize_item(item))
        
        # Sort by CVSS score
        items.sort(key=lambda x: x.get('cvss_score', 0), reverse=True)
        return items
    
    def _cvss_to_severity(self, score: float) -> str:
        """Convert CVSS score to severity level"""
        if score >= 9.0:
            return 'critical'
        elif score >= 7.0:
            return 'high'
        elif score >= 4.0:
            return 'medium'
        elif score > 0:
            return 'low'
        return 'info'
