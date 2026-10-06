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