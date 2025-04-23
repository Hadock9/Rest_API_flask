from fastapi import HTTPException, Request, status
from redis import Redis
from datetime import datetime, timedelta
from typing import Optional
import json

class RateLimiter:
    def __init__(self, redis: Redis, limit: int, window: int = 60):
        self.redis = redis
        self.limit = limit
        self.window = window

    async def is_rate_limited(self, key: str) -> bool:
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window)
        
        # Get all requests in the current window
        requests = self.redis.lrange(key, 0, -1)
        requests = [json.loads(r) for r in requests]
        
        # Remove requests outside the window
        valid_requests = [r for r in requests if datetime.fromisoformat(r['timestamp']) > window_start]
        
        # Update Redis with valid requests
        if len(valid_requests) != len(requests):
            self.redis.delete(key)
            for req in valid_requests:
                self.redis.rpush(key, json.dumps(req))
        
        # Check if limit is reached
        if len(valid_requests) >= self.limit:
            return True
        
        # Add new request
        self.redis.rpush(key, json.dumps({'timestamp': now.isoformat()}))
        self.redis.expire(key, self.window)
        
        return False

# Rate limits configuration
AUTHENTICATED_LIMIT = 10  # requests per minute
ANONYMOUS_LIMIT = 2      # requests per minute

async def rate_limit_middleware(request: Request, redis: Redis):
    # Get user identifier (username for authenticated users, IP for anonymous)
    user_id = request.user.username if hasattr(request, 'user') else request.client.host
    
    # Determine rate limit based on authentication status
    limit = AUTHENTICATED_LIMIT if hasattr(request, 'user') else ANONYMOUS_LIMIT
    limiter = RateLimiter(redis, limit)
    
    # Check if rate limit is exceeded
    if await limiter.is_rate_limited(f"rate_limit:{user_id}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        ) 