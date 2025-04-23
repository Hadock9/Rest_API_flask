from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from .views import router
from .rate_limiter import rate_limit_middleware

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

# Initialize Redis
redis = Redis(host="localhost", port=6379, db=0)

# Add rate limiter middleware
@app.middleware("http")
async def rate_limiter_middleware(request: Request, call_next):
    await rate_limit_middleware(request, redis)
    response = await call_next(request)
    return response

app.include_router(router)
