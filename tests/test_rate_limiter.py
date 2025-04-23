import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.rate_limiter import RateLimiter, rate_limit_middleware

@pytest.fixture
def mock_redis():
    return Mock()

@pytest.fixture
def mock_request():
    request = Mock()
    request.client.host = "127.0.0.1"
    return request

@pytest.fixture
def mock_auth_request():
    request = Mock()
    request.user = Mock()
    request.user.username = "test_user"
    return request

@pytest.mark.asyncio
async def test_anonymous_rate_limit_not_exceeded(mock_redis, mock_request):
    # Mock Redis response for not exceeded limit
    mock_redis.lrange.return_value = []
    
    # Should not raise exception
    await rate_limit_middleware(mock_request, mock_redis)
    
    # Verify Redis was called
    mock_redis.lrange.assert_called_once()
    mock_redis.rpush.assert_called_once()

@pytest.mark.asyncio
async def test_anonymous_rate_limit_exceeded(mock_redis, mock_request):
    # Mock Redis response for exceeded limit
    mock_redis.lrange.return_value = [
        '{"timestamp": "' + (datetime.utcnow() - timedelta(seconds=30)).isoformat() + '"}',
        '{"timestamp": "' + (datetime.utcnow() - timedelta(seconds=20)).isoformat() + '"}',
        '{"timestamp": "' + (datetime.utcnow() - timedelta(seconds=10)).isoformat() + '"}'
    ]
    
    # Should raise 429 exception
    with pytest.raises(HTTPException) as exc_info:
        await rate_limit_middleware(mock_request, mock_redis)
    
    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_authenticated_rate_limit_not_exceeded(mock_redis, mock_auth_request):
    # Mock Redis response for not exceeded limit
    mock_redis.lrange.return_value = []
    
    # Should not raise exception
    await rate_limit_middleware(mock_auth_request, mock_redis)
    
    # Verify Redis was called
    mock_redis.lrange.assert_called_once()
    mock_redis.rpush.assert_called_once()

@pytest.mark.asyncio
async def test_authenticated_rate_limit_exceeded(mock_redis, mock_auth_request):
    # Mock Redis response for exceeded limit
    mock_redis.lrange.return_value = [
        '{"timestamp": "' + (datetime.utcnow() - timedelta(seconds=30)).isoformat() + '"}'
    ] * 11  # 11 requests > 10 limit
    
    # Should raise 429 exception
    with pytest.raises(HTTPException) as exc_info:
        await rate_limit_middleware(mock_auth_request, mock_redis)
    
    assert exc_info.value.status_code == 429
    assert "Rate limit exceeded" in str(exc_info.value.detail) 