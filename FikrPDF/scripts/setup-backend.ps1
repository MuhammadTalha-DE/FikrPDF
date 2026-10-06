# ============================================================
# FikrPDF — Backend Setup (Phases 2 + 4 combined)
# Writes every backend file with real working code.
# Run from D:\FikrPDF
# ============================================================

$ErrorActionPreference = "Stop"
$root = "D:\FikrPDF"
Set-Location $root

# ---------- Helper ----------
function Write-Utf8File($relativePath, $content) {
  $full = Join-Path $root $relativePath
  $dir = Split-Path $full -Parent
  if (-not (Test-Path $dir)) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
  }
  [System.IO.File]::WriteAllText($full, $content, [System.Text.UTF8Encoding]::new($false))
  Write-Host "  OK  $relativePath" -ForegroundColor Green
}

Write-Host "`n=== FikrPDF Backend Setup ===" -ForegroundColor Cyan

# ---------- Create directory tree ----------
Write-Host "`n[1/6] Creating directories..." -ForegroundColor Cyan
$dirs = @(
  "backend\app\routers",
  "backend\app\services",
  "backend\app\models",
  "backend\app\schemas",
  "backend\app\utils",
  "backend\app\workers",
  "backend\storage\uploads",
  "backend\storage\processed",
  "backend\storage\tmp",
  "backend\tests"
)
foreach ($d in $dirs) {
  New-Item -ItemType Directory -Force -Path (Join-Path $root $d) | Out-Null
}

# ---------- Package markers ----------
Write-Host "`n[2/6] Writing package markers (__init__.py)..." -ForegroundColor Cyan
$initFiles = @(
  "backend\app\__init__.py",
  "backend\app\routers\__init__.py",
  "backend\app\services\__init__.py",
  "backend\app\models\__init__.py",
  "backend\app\schemas\__init__.py",
  "backend\app\utils\__init__.py",
  "backend\app\workers\__init__.py"
)
foreach ($f in $initFiles) {
  Write-Utf8File $f ""
}

# ---------- requirements ----------
Write-Host "`n[3/6] Writing requirements..." -ForegroundColor Cyan

Write-Utf8File "backend/requirements.txt" @'
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-dotenv==1.0.1
pydantic==2.9.2
pydantic-settings==2.5.2
loguru==0.7.2
slowapi==0.1.9
python-multipart==0.0.12
'@

Write-Utf8File "backend/requirements-dev.txt" @'
-r requirements.txt
pytest==8.3.3
httpx==0.27.2
ruff==0.6.9
'@

# ---------- env files ----------
Write-Host "`n[4/6] Writing .env files..." -ForegroundColor Cyan

Write-Utf8File "backend/.env.example" @'
# App
APP_NAME=FikrPDF
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000

# CORS — comma-separated origins
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Rate limiting
RATE_LIMIT_PER_MINUTE=30

# Logging
LOG_LEVEL=INFO

# Database (Phase 5)
DATABASE_URL=

# Storage
STORAGE_PATH=./storage
'@

Write-Utf8File "backend/.env" @'
APP_NAME=FikrPDF
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
RATE_LIMIT_PER_MINUTE=30
LOG_LEVEL=INFO
DATABASE_URL=
STORAGE_PATH=./storage
'@

Write-Utf8File "backend/.gitignore" @'
__pycache__/
*.py[cod]
venv/
.env
storage/
.pytest_cache/
.ruff_cache/
'@

Write-Utf8File "backend/pytest.ini" @'
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
'@

# ---------- Application code ----------
Write-Host "`n[5/6] Writing application code..." -ForegroundColor Cyan

# ---------- app/config.py ----------
Write-Utf8File "backend/app/config.py" @'
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "FikrPDF"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    cors_origins: str = "http://localhost:3000"
    rate_limit_per_minute: int = 30
    log_level: str = "INFO"

    database_url: str = ""
    storage_path: str = "./storage"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
'@

# ---------- app/utils/errors.py ----------
Write-Utf8File "backend/app/utils/errors.py" @'
from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


class FikrPDFException(Exception):
    """Base class for all FikrPDF domain errors."""

    code: str = "INTERNAL_ERROR"
    http_status: int = 500
    message: str = "Something went wrong."
    hint: str | None = None

    def __init__(self, message: str | None = None, hint: str | None = None):
        super().__init__(message or self.message)
        if message:
            self.message = message
        if hint:
            self.hint = hint


class ValidationError(FikrPDFException):
    code = "VALIDATION_ERROR"
    http_status = 422
    message = "The request is invalid."


class FileTooLargeError(FikrPDFException):
    code = "FILE_TOO_LARGE"
    http_status = 413
    message = "File exceeds the allowed size."
    hint = "Free tier: 25 MB. Upgrade to Pro for 200 MB."


class UnsupportedMimeError(FikrPDFException):
    code = "UNSUPPORTED_MIME"
    http_status = 415
    message = "File type not supported."


class CorruptPDFError(FikrPDFException):
    code = "PDF_CORRUPT"
    http_status = 400
    message = "The PDF could not be read."
    hint = "Try re-saving the file or check if it is password-protected."


class PasswordProtectedError(FikrPDFException):
    code = "PDF_PASSWORD_PROTECTED"
    http_status = 400
    message = "PDF is password-protected."
    hint = "Provide the password or unlock it first."


class NotFoundError(FikrPDFException):
    code = "NOT_FOUND"
    http_status = 404
    message = "Resource not found."


class RateLimitError(FikrPDFException):
    code = "RATE_LIMITED"
    http_status = 429
    message = "Too many requests."
    hint = "Wait a moment and try again."


class NotImplementedYetError(FikrPDFException):
    code = "NOT_IMPLEMENTED"
    http_status = 501
    message = "This feature is not implemented yet."


async def fikrpdf_exception_handler(request: Request, exc: FikrPDFException):
    request_id = getattr(request.state, "request_id", None)
    logger.warning(
        "domain_error | id={} | code={} | path={} | msg={}",
        request_id, exc.code, request.url.path, exc.message,
    )
    body = {
        "error": {
            "code": exc.code,
            "message": exc.message,
        }
    }
    if exc.hint:
        body["error"]["hint"] = exc.hint
    return JSONResponse(status_code=exc.http_status, content=body)


async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.exception("unhandled_error | id={} | path={}", request_id, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Something went wrong on our side.",
                "hint": "Please try again. If it persists, contact support.",
            }
        },
    )
'@

# ---------- app/utils/logging.py ----------
Write-Utf8File "backend/app/utils/logging.py" @'
import sys
import uuid
import time
from contextvars import ContextVar
from loguru import logger
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


def setup_logging(level: str = "INFO"):
    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "req=<cyan>{extra[request_id]}</cyan> | "
            "<level>{message}</level>"
        ),
        filter=lambda record: record["extra"].setdefault(
            "request_id", request_id_ctx.get()
        ),
    )


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        request.state.request_id = rid
        token = request_id_ctx.set(rid)
        start = time.perf_counter()
        status = "-"
        try:
            response = await call_next(request)
            status = response.status_code
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.info(
                "{} {} -> {} ({} ms)",
                request.method, request.url.path, status, duration_ms,
            )
            request_id_ctx.reset(token)
        response.headers["X-Request-ID"] = rid
        return response
'@

# ---------- app/utils/security.py ----------
Write-Utf8File "backend/app/utils/security.py" @'
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=[])
'@

# ---------- app/routers/health.py ----------
Write-Utf8File "backend/app/routers/health.py" @'
from fastapi import APIRouter, Request
from datetime import datetime, timezone

router = APIRouter()


@router.get("/health")
def health_check(request: Request):
    return {
        "status": "ok",
        "service": "fikrpdf-backend",
        "version": "0.1.0",
        "env": "development",
        "request_id": request.state.request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
'@

# ---------- app/routers/pdf.py ----------
Write-Utf8File "backend/app/routers/pdf.py" @'
from fastapi import APIRouter, Request, UploadFile, File
from app.utils.errors import NotImplementedYetError
from app.utils.security import limiter

router = APIRouter()


@router.post("/merge")
@limiter.limit("30/minute")
async def merge_pdf(request: Request, files: list[UploadFile] = File(...)):
    """Merge multiple PDFs into one. Implemented in Phase 8."""
    raise NotImplementedYetError(hint="Merge arrives in Phase 8.")


@router.post("/split")
@limiter.limit("30/minute")
async def split_pdf(request: Request, file: UploadFile = File(...)):
    """Split a PDF into parts. Implemented in Phase 9."""
    raise NotImplementedYetError(hint="Split arrives in Phase 9.")


@router.post("/compress")
@limiter.limit("30/minute")
async def compress_pdf(request: Request, file: UploadFile = File(...)):
    """Compress a PDF. Implemented in Phase 10."""
    raise NotImplementedYetError(hint="Compress arrives in Phase 10.")
'@

# ---------- app/main.py ----------
Write-Utf8File "backend/app/main.py" @'
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

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

# ---------- App ----------
app = FastAPI(
    title=f"{settings.app_name} API",
    description="Backend for FikrPDF platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------- Middleware ----------
app.add_middleware(RequestIDMiddleware)
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


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} API is running",
        "docs": "/docs",
        "env": settings.app_env,
    }
'@

# ---------- docs/API.md ----------
Write-Host "`n[6/6] Writing docs/API.md..." -ForegroundColor Cyan
Write-Utf8File "docs/API.md" @'
# FikrPDF API Contract — v1

**Base URL (dev):** http://localhost:8000
**Base URL (prod):** https://api.fikrpdf.com
**Content-Type:** application/json (uploads use multipart/form-data)

## Standard Error Envelope

```json
{
  "error": {
    "code": "PDF_CORRUPT",
    "message": "The PDF could not be read.",
    "hint": "Try re-saving the file or check if it is password-protected."
  }
}