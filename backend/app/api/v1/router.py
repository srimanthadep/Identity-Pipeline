from fastapi import APIRouter
from app.api.v1.characters import router as characters_router
from app.api.v1.generations import router as generations_router
from app.api.v1.pipeline import router as pipeline_router

api_router = APIRouter()
api_router.include_router(characters_router)
api_router.include_router(generations_router)
api_router.include_router(pipeline_router)
