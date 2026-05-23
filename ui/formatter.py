"""
Output formatting utilities
"""

import json
import csv
from typing import Dict, Any, List
from datetime import datetime
from io import StringIO


class OutputFormatter:
    """Format data for various output types"""
    
    # ANSI color codes
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'italic': '\033[3m',
        'underline': '\033[4m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
        'bg_red': '\033[41m',
        'bg_green': '\033[42m',
        'bg_yellow': '\033[43m',
        'bg_blue': '\033[44m'
    }
    
    # Severity colors
    SEVERITY_COLORS = {
        'critical': 'bright_red',
        'high': 'red',
        'medium': 'yellow',
        'low': 'blue',
        'info': 'dim'
    }
    
    # Severity icons
    SEVERITY_ICONS = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🔵',
        'info': '⚪'
    }
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
    
    def colorize(self, text: str, color: str) -> str:
        """Apply color to text"""
        if not self.use_colors:
            return text
        code = self.COLORS.get(color, '')
        reset = self.COLORS['reset']
        return f"{code}{text}{reset}"
    
    def format_item(self, item: Dict[str, Any], compact: bool = False) -> str:
        """Format a single item for display"""
        severity = item.get('severity', 'info')
        color = self.SEVERITY_COLORS.get(severity, 'white')
        icon = self.SEVERITY_ICONS.get(severity, '⚪')
        
        source = item.get('source', 'unknown').upper()
        title = item.get('title', 'Untitled')
        timestamp = item.get('timestamp', '')
        description = item.get('description', '')
        
        if compact:
            return f"{icon} [{self.colorize(source, 'cyan')}] {self.colorize(title, color)}"
        
        lines = [
            f"{icon} {self.colorize(title, 'bold')}",
            f"   Source: {self.colorize(source, 'cyan')} | Severity: {self.colorize(severity.upper(), color)} | Time: {self.colorize(timestamp, 'dim')}",
        ]
        
        if description:
            lines.append(f"   {description}")
        
        # Add location if available
        location = item.get('location', {})
        if location.get('latitude') and location.get('longitude'):
            lat = location['latitude']
            lon = location['longitude']
            loc_str = f"📍 {lat:.4f}, {lon:.4f}"
            if location.get('city'):
                loc_str += f" ({location['city']})"
            lines.append(f"   {self.colorize(loc_str, 'dim')}")
        
        lines.append('')
        return '\n'.join(lines)
    
    def format_list(self, items: List[Dict[str, Any]], compact: bool = False) -> str:
        """Format a list of items"""
        if not items:
            return self.colorize("No data available.", 'dim')
        
        formatted = []
        for item in items:
            formatted.append(self.format_item(item, compact))
        
        return '\n'.join(formatted)
    
    def format_summary(self, items: List[Dict[str, Any]], correlations: List[Dict] = None, patterns: List[Dict] = None) -> str:
        """Format a summary view"""
        lines = []
        
        # Header
        lines.append(self.colorize("═" * 70, 'dim'))
        lines.append(self.colorize("  📡 INFOSENTRY INTELLIGENCE SUMMARY", 'bold'))
        lines.append(self.colorize("═" * 70, 'dim'))
        lines.append('')
        
        # Stats
        total = len(items)
        severities = {}
        sources = {}
        for item in items:
            sev = item.get('severity', 'info')
            severities[sev] = severities.get(sev, 0) + 1
            src = item.get('source', 'unknown')
            sources[src] = sources.get(src, 0) + 1
        
        lines.append(self.colorize("📊 STATISTICS", 'bold'))
        lines.append(f"   Total Events: {self.colorize(str(total), 'bright_cyan')}")
        
        if severities:
            sev_str = ' | '.join([f"{self.SEVERITY_ICONS.get(k, '⚪')} {k}: {v}" for k, v in sorted(severities.items())])
            lines.append(f"   Severity: {sev_str}")
        
        if sources:
            src_str = ' | '.join([f"{k}: {v}" for k, v in sorted(sources.items())])
            lines.append(f"   Sources: {self.colorize(src_str, 'dim')}")
        
        lines.append('')
        
        # Patterns
        if patterns:
            lines.append(self.colorize("🔍 PATTERNS DETECTED", 'bold'))
            for pattern in patterns[:5]:
                desc = pattern.get('description', '')
                lines.append(f"   • {desc}")
            lines.append('')
        
        # Correlations
        if correlations:
            lines.append(self.colorize("🔗 CORRELATIONS", 'bold'))
            for corr in correlations[:5]:
                desc = corr.get('description', '')
                conf = corr.get('confidence', 0)
                conf_str = f"({conf*100:.0f}% confidence)"
                lines.append(f"   • {desc} {self.colorize(conf_str, 'dim')}")
            lines.append('')
        
        lines.append(self.colorize("═" * 70, 'dim'))
        
        return '\n'.join(lines)
    
    def format_json(self, data: Any, pretty: bool = True) -> str:
        """Format data as JSON"""
        indent = 2 if pretty else None
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    
    def format_csv(self, items: List[Dict[str, Any]]) -> str:
        """Format items as CSV"""
        if not items:
            return ""
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['source', 'timestamp', 'title', 'description', 'severity', 'latitude', 'longitude'])
        
        # Write rows
        for item in items:
            location = item.get('location', {})
            writer.writerow([
                item.get('source', ''),
                item.get('timestamp', ''),
                item.get('title', ''),
                item.get('description', ''),
                item.get('severity', ''),
                location.get('latitude', ''),
                location.get('longitude', '')
            ])
        
        return output.getvalue()
    
    def format_markdown(self, items: List[Dict[str, Any]], title: str = "Intelligence Report") -> str:
        """Format items as Markdown report"""
        lines = []
        
        lines.append(f"# {title}")
        lines.append('')
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append('')
        
        # Summary
        lines.append("## Summary")
        lines.append('')
        lines.append(f"- Total Events: {len(items)}")
        
        severities = {}
        sources = {}
        for item in items:
            sev = item.get('severity', 'info')
            severities[sev] = severities.get(sev, 0) + 1
            src = item.get('source', 'unknown')
            sources[src] = sources.get(src, 0) + 1
        
        lines.append(f"- Severity Distribution: {dict(severities)}")
        lines.append(f"- Sources: {dict(sources)}")
        lines.append('')
        
        # Events
        lines.append("## Events")
        lines.append('')
        
        for item in items:
            severity = item.get('severity', 'info')
            title_text = item.get('title', 'Untitled')
            lines.append(f"### {title_text}")
            lines.append('')
            lines.append(f"- **Source:** {item.get('source', 'unknown')}")
            lines.append(f"- **Severity:** {severity}")
            lines.append(f"- **Time:** {item.get('timestamp', '')}")
            
            location = item.get('location', {})
            if location.get('latitude') and location.get('longitude'):
                lines.append(f"- **Location:** {location['latitude']}, {location['longitude']}")
            
            description = item.get('description', '')
            if description:
                lines.append(f"- **Description:** {description}")
            
            lines.append('')
        
        return '\n'.join(lines)
    
    def clear_screen(self) -> str:
        """Return ANSI clear screen sequence"""
        return '\033[2J\033[H' if self.use_colors else '\n' * 50
