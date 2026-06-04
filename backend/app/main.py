import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging_config import configure_logging
from app.routes.admin import router as admin_router
from app.routes.ai import router as ai_router
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.routes.lessons import router as lessons_router
from app.routes.uploads import router as uploads_router


configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

    Path(settings.upload_path).mkdir(parents=True, exist_ok=True)
    Path(settings.audio_path).mkdir(parents=True, exist_ok=True)
    logger.info("Application startup complete.")


app.mount("/uploads", StaticFiles(directory=str(settings.upload_path)), name="uploads")
app.mount("/audio", StaticFiles(directory=str(settings.audio_path)), name="audio")

app.include_router(auth_router)
app.include_router(uploads_router)
app.include_router(ai_router)
app.include_router(dashboard_router)
app.include_router(admin_router)
app.include_router(lessons_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})
