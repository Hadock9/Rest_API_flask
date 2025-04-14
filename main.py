from fastapi import FastAPI
from .views import router

app = FastAPI(
    title="Library API",
    description="A simple library API built with FastAPI",
    version="1.0.0"
)

app.include_router(router)
