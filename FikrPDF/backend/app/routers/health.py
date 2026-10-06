from fastapi import APIRouter, Request, Depends
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

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


@router.get("/health/db")
def health_db(request: Request, db: Session = Depends(get_db)):
    """Verify DB connectivity."""
    try:
        result = db.execute(text("SELECT 1")).scalar()
        ok = result == 1
        return {
            "db": "ok" if ok else "unexpected",
            "request_id": request.state.request_id,
        }
    except Exception as e:
        return {
            "db": "error",
            "detail": str(e),
            "request_id": request.state.request_id,
        }