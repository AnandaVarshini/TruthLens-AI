"""TruthLens AI - FastAPI application entry point.

Run from the backend/ folder:

    uvicorn app.main:app --reload --port 8000

Interactive API documentation: http://localhost:8000/docs
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from . import config
from .database import init_db
from .ml_service import model_service
from .routers import auth, insights, predictions
from .schemas import HealthOut

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("truthlens")

app = FastAPI(
    title="TruthLens AI API",
    description=(
        "Fake news detection API for four-class claim reliability classification "
        "(Real, Misleading, Partially False, Fake) using TF-IDF and classical "
        "machine-learning models trained on the LIAR dataset."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(predictions.router)
app.include_router(insights.router)


@app.on_event("startup")
def startup() -> None:
    init_db()
    if config.DEV_SECRET_IN_USE:
        logger.warning(
            "TRUTHLENS_SECRET_KEY is not set - using the development fallback key. "
            "Set it in backend/.env before sharing the app."
        )
    if model_service.is_ready():
        logger.info("Model ready: %s", model_service.model_name())
    else:
        logger.error(
            "Model NOT ready. Run 'python scripts/train_models.py' from the project root, "
            "then restart the API."
        )


@app.get("/api/health", response_model=HealthOut, tags=["System"])
def health() -> HealthOut:
    ready = model_service.is_ready()
    return HealthOut(
        status="ok" if ready else "degraded",
        model_ready=ready,
        model_name=model_service.model_name() if ready else None,
        detail=None
        if ready
        else "Trained model artifacts are missing. Run scripts/train_models.py.",
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again."},
    )


# ---- Optional: serve a production frontend build if one exists --------------
if config.FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles

    assets_dir = config.FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        candidate = (config.FRONTEND_DIST / full_path).resolve()
        if (
            full_path
            and candidate.is_file()
            and config.FRONTEND_DIST.resolve() in candidate.parents
        ):
            return FileResponse(candidate)
        return FileResponse(config.FRONTEND_DIST / "index.html")
