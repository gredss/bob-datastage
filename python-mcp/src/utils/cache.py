"""
Simple in-memory cache implementation
"""

import time
from typing import Any, Optional, Dict
from ..utils.logger import logger


class CacheEntry:
    """Cache entry with data, timestamp, and TTL"""
    def __init__(self, data: Any, ttl: float):
        self.data = data
        self.timestamp = time.time()
        self.ttl = ttl


class SimpleCache:
    """Simple in-memory cache"""
    
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        entry = self.cache.get(key)
        
        if not entry:
            logger.debug(f'Cache miss for key: {key}')
            return None
        
        # Check if entry has expired
        now = time.time()
        if now > entry.timestamp + entry.ttl:
            logger.debug(f'Cache entry expired for key: {key}')
            del self.cache[key]
            return None
        
        logger.debug(f'Cache hit for key: {key}')
        return entry.data
    
    def set(self, key: str, data: Any, ttl: float) -> None:
        """Set a value in cache"""
        entry = CacheEntry(data, ttl)
        self.cache[key] = entry
        logger.debug(f'Cached data for key: {key} (TTL: {ttl}s)')
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f'Deleted cache entry for key: {key}')
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        size = len(self.cache)
        self.cache.clear()
        logger.debug(f'Cleared {size} cache entries')
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)
    
    def has(self, key: str) -> bool:
        """Check if key exists in cache"""
        entry = self.cache.get(key)
        if not entry:
            return False
        
        # Check if expired
        now = time.time()
        if now > entry.timestamp + entry.ttl:
            del self.cache[key]
            return False
        
        return True
    
    def cleanup(self) -> None:
        """Clean up expired entries"""
        now = time.time()
        cleaned = 0
        
        keys_to_delete = []
        for key, entry in self.cache.items():
            if now > entry.timestamp + entry.ttl:
                keys_to_delete.append(key)
                cleaned += 1
        
        for key in keys_to_delete:
            del self.cache[key]
        
        if cleaned > 0:
            logger.debug(f'Cleaned up {cleaned} expired cache entries')


# Made with Bob