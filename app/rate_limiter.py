from fastapi import HTTPException, Request, status
from redis.asyncio import Redis
import time
from typing import Optional

# Rate limits configuration
RATE_LIMITS = {
    "authenticated": (10, 60),  # 10 requests per minute
    "anonymous": (2, 60)        # 2 requests per minute
}

async def rate_limit(request: Request, user_id: Optional[str] = None, redis: Redis = None):
    """
    Rate limiter middleware using sliding window approach
    """
    if not redis:
        return  # Skip rate limiting if Redis is not available

    # Get user identity (username for authenticated users, IP for anonymous)
    identity = user_id or request.client.host
    
    # Determine rate limit based on authentication status
    limit_type = "authenticated" if user_id else "anonymous"
    limit, period = RATE_LIMITS[limit_type]
    
    # Create Redis key for the user
    key = f"rate_limit:{identity}"
    
    # Get current timestamp
    now = int(time.time())
    window_start = now - period
    
    # Remove old requests outside the window
    await redis.zremrangebyscore(key, 0, window_start)
    
    # Get current request count
    request_count = await redis.zcard(key)
    
    # Check if limit is exceeded
    if request_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Add current request to the window
    await redis.zadd(key, {str(now): now})
    
    # Set expiration for the key
    await redis.expire(key, period) 