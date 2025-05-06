import os
from redis.asyncio import Redis

# Redis configuration for PythonAnywhere
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True
}

# Create Redis connection
redis = Redis(**REDIS_CONFIG) 