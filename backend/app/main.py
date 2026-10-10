from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Persistent Character Identity Pipeline for India-centric AI video generation, inspired by Higgsfield Soul ID.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static File Mounts
app.mount("/assets", StaticFiles(directory=str(settings.ASSETS_DIR)), name="assets")
app.mount("/outputs", StaticFiles(directory=str(settings.OUTPUTS_DIR)), name="outputs")

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "default_adapter": settings.DEFAULT_ADAPTER,
        "database": "sqlite"
    }
