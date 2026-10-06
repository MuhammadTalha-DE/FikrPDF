from fastapi import APIRouter, Depends, Request, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.file import File as FileModel
from app.services.storage_service import storage_service
from app.utils.errors import ValidationError
from app.utils.files import validate_upload
from app.utils.security import limiter

router = APIRouter()


@router.post("/upload")
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Accept a single file.
    - MIME sniffed from bytes (Gap 4)
    - Size limit by tier (Gap 2)
    - UUID filename (Gap 4)
    - expires_at written (Gap 1)
    - rate limited 10/min (Gap 5)
    """
    content = await file.read()
    tier = "free"  # Phase 26 will read from authenticated user

    mime = validate_upload(content, tier=tier)

    stored = storage_service.save_upload(
        content=content,
        original_name=file.filename or "unnamed",
        ttl_hours=settings.ttl_hours(tier),
    )

    db_file = FileModel(
        id=stored["id"],
        user_id=None,               # Phase 26 attaches user
        filename=file.filename or "unnamed",
        mime=mime,
        size=stored["size"],
        storage_path=stored["storage_path"],
        kind="upload",
        expires_at=stored["expires_at"],
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {
        "file_id": str(db_file.id),
        "filename": db_file.filename,
        "mime": db_file.mime,
        "size": db_file.size,
        "expires_at": db_file.expires_at.isoformat(),
        "request_id": request.state.request_id,
    }


@router.post("/upload-many")
@limiter.limit("5/minute")
async def upload_many(
    request: Request,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Batch upload — used by Merge (Phase 8)."""
    if not files:
        raise ValidationError("No files provided.")
    if len(files) > 20:
        raise ValidationError("Maximum 20 files per request.")

    results = []
    tier = "free"
    for f in files:
        content = await f.read()
        mime = validate_upload(content, tier=tier)
        stored = storage_service.save_upload(
            content=content,
            original_name=f.filename or "unnamed",
            ttl_hours=settings.ttl_hours(tier),
        )
        db_file = FileModel(
            id=stored["id"],
            filename=f.filename or "unnamed",
            mime=mime,
            size=stored["size"],
            storage_path=stored["storage_path"],
            kind="upload",
            expires_at=stored["expires_at"],
        )
        db.add(db_file)
        results.append(db_file)

    db.commit()
    for r in results:
        db.refresh(r)

    return {
        "files": [
            {
                "file_id": str(r.id),
                "filename": r.filename,
                "mime": r.mime,
                "size": r.size,
                "expires_at": r.expires_at.isoformat(),
            }
            for r in results
        ],
        "request_id": request.state.request_id,
    }