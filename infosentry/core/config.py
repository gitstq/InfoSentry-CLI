"""
Configuration management for InfoSentry-CLI
"""

import os
import json
from pathlib import Path


class Config:
    """Configuration manager"""
    
    DEFAULT_CONFIG = {
        "cache_dir": "~/.infosentry/cache",
        "cache_ttl": 300,  # 5 minutes
        "timeout": 30,
        "max_retries": 3,
        "sources": {
            "earthquake": {"enabled": True, "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"},
            "aviation": {"enabled": True, "url": "https://opensky-network.org/api/states/all"},
            "weather": {"enabled": True, "url": "https://api.open-meteo.com/v1/forecast"},
            "spacex": {"enabled": True, "url": "https://api.spacexdata.com/v4/launches/upcoming"},
            "cve": {"enabled": True, "url": "https://services.nvd.nist.gov/rest/json/cves/2.0"},
            "news": {"enabled": True, "url": "https://newsapi.org/v2/top-headlines"}
        },
        "analysis": {
            "correlation_enabled": True,
            "anomaly_detection": True,
            "pattern_recognition": True
        },
        "ui": {
            "theme": "dark",
            "refresh_interval": 60,
            "max_items_display": 50
        }
    }
    
    def __init__(self):
        self.config_dir = Path.home() / ".infosentry"
        self.config_file = self.config_dir / "config.json"
        self._config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults
                    return self._merge_config(self.DEFAULT_CONFIG, config)
            except (json.JSONDecodeError, IOError):
                pass
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_config(self, default, user):
        """Recursively merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def save(self):
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def get(self, key, default=None):
        """Get configuration value by key (dot notation supported)"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        """Set configuration value by key (dot notation supported)"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    @property
    def cache_dir(self):
        """Get cache directory path"""
        return Path(self.get("cache_dir", "~/.infosentry/cache")).expanduser()
    
    @property
    def cache_ttl(self):
        """Get cache TTL in seconds"""
        return self.get("cache_ttl", 300)
