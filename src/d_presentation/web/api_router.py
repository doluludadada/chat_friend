from fastapi import APIRouter
from src.c_infrastructure.platforms.line import line_router

# The main router that aggregates all webhook routes.
api_router = APIRouter(
    prefix="/webhook",
)

# Include routers from specific platforms
api_router.include_router(line_router.router)
