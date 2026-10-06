from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.routers import health, pdf, upload   # add upload

from contextlib import asynccontextmanager
from app.utils.scheduler import start_scheduler, stop_scheduler
from app.routers import health, pdf, upload, admin
from app.services.cleanup_service import cleanup_expired_files

from app.config import settings
from app.utils.errors import (
    FikrPDFException,
    fikrpdf_exception_handler,
    unhandled_exception_handler,
    RateLimitError,
)
from app.utils.logging import setup_logging, RequestIDMiddleware
from app.utils.security import limiter

from app.routers import health, pdf

# ---------- Logging ----------
setup_logging(settings.log_level)


start_scheduler(interval_minutes=settings.cleanup_interval_minutes)



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger_startup = "FikrPDF API starting..."
    from loguru import logger
    logger.info(logger_startup)

    # Initial sweep on boot
    summary = cleanup_expired_files()
    logger.info("startup_cleanup | {}", summary)

    # Background sweep every 15 min
    start_scheduler(interval_minutes=15)

    yield

    # Shutdown
    stop_scheduler()
    logger.info("FikrPDF API stopped")

# ---------- App ----------
app = FastAPI(
    title=f"{settings.app_name} API",
    description="Backend for FikrPDF platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------- Middleware order matters ----------
app.add_middleware(RequestIDMiddleware)  # outermost — generates ID first
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# ---------- Exception handlers ----------
app.add_exception_handler(FikrPDFException, fikrpdf_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return await fikrpdf_exception_handler(request, RateLimitError())


# ---------- Routers ----------
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["pdf"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["pdf"])

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["pdf"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} API is running",
        "docs": "/docs",
        "env": settings.app_env,
    }