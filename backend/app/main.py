"""Merchant DNA - Merchant Risk Intelligence Platform FastAPI Application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.data.store import store
from app.ml.behavioral_model import behavioral_scorer
from app.ml.network_detector import network_detector

# API Routers
from app.api.system import router as system_router
from app.api.merchants import router as merchants_router
from app.api.trust import router as trust_router
from app.api.alerts import router as alerts_router
from app.api.graph import router as graph_router
from app.api.investigations import router as investigations_router
from app.api.feedback import router as feedback_router
from app.api.evaluation import router as evaluation_router
from app.api.simulation import router as simulation_router

logger = logging.getLogger("merchant_dna")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes synthetic world, ML model, and network graph on startup with graceful fallbacks."""
    try:
        # Ensure behavioral model is fitted on startup
        if not behavioral_scorer.is_trained:
            logger.info("Fitting behavioral model baseline from datastore...")
            behavioral_scorer.fit_from_datastore(store)
            logger.info("Behavioral baseline successfully fitted.")
    except Exception as e:
        logger.error(f"Startup initialization warning: ML model fitting failed ({e}). Running in deterministic fallback mode.")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Merchant Risk Intelligence Platform identifying merchant mule/shell behavior and cross-merchant coordinated fraud rings via behavior and entity graph intelligence.",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Global Exception Handlers — Zero Raw Tracebacks Leak to Clients
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Formats all standard HTTP exceptions into clean, uniform JSON envelopes."""
    detail = exc.detail
    if isinstance(detail, dict):
        error_code = detail.get("error", "HTTP_ERROR")
        message = detail.get("message", str(detail))
        detail_payload = detail
    else:
        error_code = "HTTP_ERROR"
        message = str(detail)
        detail_payload = message

    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "error": error_code,
            "message": message,
            "detail": detail_payload,
            "status_code": exc.status_code,
            "path": request.url.path,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats Pydantic / FastAPI schema validation errors into readable JSON."""
    formatted_errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        formatted_errors.append(f"{loc}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Invalid request parameters or payload format.",
            "details": formatted_errors,
            "status_code": 422,
            "path": request.url.path,
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Catches business logic ValueError exceptions and returns clean 400 Bad Request."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "BAD_REQUEST",
            "message": str(exc),
            "status_code": 400,
            "path": request.url.path,
        },
    )


@app.exception_handler(Exception)
async def global_catch_all_exception_handler(request: Request, exc: Exception):
    """Safety net: catches all unhandled exceptions, logs traceback, returns safe 500 JSON."""
    logger.exception(f"Unhandled server error processing request to {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred. Please verify backend service status.",
            "status_code": 500,
            "path": request.url.path,
        },
    )


# Include API Routers
app.include_router(system_router)
app.include_router(merchants_router)
app.include_router(trust_router)
app.include_router(alerts_router)
app.include_router(graph_router)
app.include_router(investigations_router)
app.include_router(feedback_router)
app.include_router(evaluation_router)
app.include_router(simulation_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

