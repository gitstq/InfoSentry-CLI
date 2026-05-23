"""
Local cache implementation using file system
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional


class Cache:
    """File-based cache with TTL support"""
    
    def __init__(self, cache_dir: Path, default_ttl: int = 300):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
    
    def _get_cache_key(self, key: str) -> str:
        """Generate safe cache key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path"""
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check expiration
            if data.get('expires', 0) < time.time():
                cache_path.unlink(missing_ok=True)
                return None
            
            return data.get('value')
        except (json.JSONDecodeError, IOError):
            cache_path.unlink(missing_ok=True)
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set cached value with TTL"""
        cache_path = self._get_cache_path(key)
        ttl = ttl or self.default_ttl
        
        data = {
            'expires': time.time() + ttl,
            'value': value
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except IOError:
            pass
    
    def delete(self, key: str):
        """Delete cached value"""
        cache_path = self._get_cache_path(key)
        cache_path.unlink(missing_ok=True)
    
    def clear(self):
        """Clear all cached values"""
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink(missing_ok=True)
    
    def cleanup(self):
        """Remove expired entries"""
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get('expires', 0) < time.time():
                    cache_file.unlink(missing_ok=True)
            except (json.JSONDecodeError, IOError):
                cache_file.unlink(missing_ok=True)
