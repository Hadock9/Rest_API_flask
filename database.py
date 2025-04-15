import motor.motor_asyncio
import os
from typing import AsyncGenerator

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongo_admin:password@mongo:27017")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.library

async def get_database() -> AsyncGenerator[motor.motor_asyncio.AsyncIOMotorDatabase, None]:
    yield db 