from fastapi import FastAPI
from .views import router

app = FastAPI(title="Library API")

app.include_router(router)
