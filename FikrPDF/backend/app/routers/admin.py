"""
Admin endpoints — protected in Phase 35.
For now: manual cleanup trigger for dev/testing.
"""

from fastapi import APIRouter, Request
from app.services.cleanup_service import cleanup_expired_files

router = APIRouter()


@router.post("/cleanup")
def trigger_cleanup(request: Request):
    """
    Manually run the cleanup sweep. Idempotent.
    Phase 35 will require admin auth.
    """
    summary = cleanup_expired_files()
    return {**summary, "request_id": request.state.request_id}