from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "fikrpdf-backend",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }