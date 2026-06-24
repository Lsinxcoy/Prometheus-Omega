"""Rate limiter safety component — prevents request flooding."""
from collections import deque
from prometheus_z.schema import ZConfig


class RateLimiter:
    """Rate limiter to prevent system overload.
    
    Tracks request frequency per key and enforces rate limits.
    """
    
    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        # Rate limit: max requests per time window
        self._max_requests = getattr(config, 'rate_limit_max', 100)
        self._window_seconds = getattr(config, 'rate_limit_window', 60)
        
        # Track requests: key -> deque of timestamps
        self._request_history: dict[str, deque[float]] = {}
        self._history_maxlen = 1000  # Max keys to track
        
    def check_rate(self, key: str) -> tuple[bool, dict]:
        """Check if request is within rate limits.
        
        Returns:
            (allowed: bool, info: dict)
        """
        import time
        now = time.time()
        
        # Initialize history for key
        if key not in self._request_history:
            self._request_history[key] = deque(maxlen=self._max_requests)
            
        history = self._request_history[key]
        
        # Remove old requests outside window
        cutoff = now - self._window_seconds
        while history and history[0] < cutoff:
            history.popleft()
        
        # Check rate limit
        request_count = len(history)
        allowed = request_count < self._max_requests
        
        info = {
            "key": key,
            "request_count": request_count,
            "max_allowed": self._max_requests,
            "window_seconds": self._window_seconds,
            "allowed": allowed,
            "reset_at": now + self._window_seconds if not allowed else None
        }
        
        if allowed:
            history.append(now)
        
        return allowed, info
    
    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        if key in self._request_history:
            self._request_history[key].clear()
        # Also remove key if empty to allow fresh start
        if key in self._request_history and not self._request_history[key]:
            del self._request_history[key]
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        total_keys = len(self._request_history)
        total_requests = sum(len(h) for h in self._request_history.values())
        
        return {
            "total_keys_tracked": total_keys,
            "total_requests": total_requests,
            "max_requests_per_window": self._max_requests,
            "window_seconds": self._window_seconds
        }