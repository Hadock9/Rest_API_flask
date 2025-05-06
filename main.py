from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from .views import router
from .rate_limiter import rate_limit
from .redis_config import redis

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Library API",
    description="A simple library API built with FastAPI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiter middleware
@app.middleware("http")
async def rate_limiter_middleware(request: Request, call_next):
    # Get user_id from request if authenticated
    user_id = None
    if hasattr(request, 'user'):
        user_id = request.user.username
    
    # Apply rate limiting
    await rate_limit(request, user_id, redis)
    
    # Process request
    response = await call_next(request)
    return response

app.include_router(router)
