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
