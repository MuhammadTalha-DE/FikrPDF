# FikrPDF API Contract — v1

**Base URL (dev):** `http://localhost:8000`
**Base URL (prod):** `https://api.fikrpdf.com`
**Content-Type:** `application/json` (except uploads: `multipart/form-data`)

---

## Standard Error Envelope

Every 4xx/5xx response uses this shape:

```json
{
  "error": {
    "code": "PDF_CORRUPT",
    "message": "The PDF could not be read.",
    "hint": "Try re-saving the file or check if it is password-protected."
  }
}
```

### Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| `VALIDATION_ERROR` | 422 | Malformed request |
| `FILE_TOO_LARGE` | 413 | Exceeds tier limit |
| `UNSUPPORTED_MIME` | 415 | Wrong file type |
| `PDF_CORRUPT` | 400 | Cannot parse PDF |
| `PDF_PASSWORD_PROTECTED` | 400 | Needs password |
| `NOT_FOUND` | 404 | Resource missing |
| `RATE_LIMITED` | 429 | Too many requests |
| `NOT_IMPLEMENTED` | 501 | Feature not yet built |
| `INTERNAL_ERROR` | 500 | Server-side bug |

---

## Headers

| Header | Direction | Notes |
|--------|-----------|-------|
| `X-Request-ID` | Response | Echo of client ID or auto-generated |
| `Content-Type` | Both | `application/json` or `multipart/form-data` |

---

## Endpoints

### `GET /api/health`
Returns service status.

**Response 200**
```json
{
  "status": "ok",
  "service": "fikrpdf-backend",
  "version": "0.1.0",
  "env": "development",
  "request_id": "abc123",
  "timestamp": "2026-10-05T12:00:00Z"
}
```

---

### `POST /api/pdf/merge` *(Phase 8)*
Merge multiple PDFs into one.

**Request** `multipart/form-data`
- `files`: `UploadFile[]` (2–20 PDFs, each ≤ tier limit)

**Response 202**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "poll_url": "/api/jobs/uuid"
}
```

**Current behavior (Phase 4):** returns `501 NOT_IMPLEMENTED`.

---

### `POST /api/pdf/split` *(Phase 9)*
**Current behavior:** `501`.

### `POST /api/pdf/compress` *(Phase 10)*
**Current behavior:** `501`.

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| All `/api/*` | 30 req/min per IP |
| `/api/upload` (Phase 6+) | 10 req/min per IP |

Exceeding → `429 RATE_LIMITED`.

---

## Versioning

Contract locks at v1. Breaking changes require a new `/api/v2/*` prefix.



---

### POST /api/upload (Phase 6)

Upload a single file.

**Request** `multipart/form-data`
- `file`: UploadFile

**Response 200**
```json
{
  "file_id": "uuid",
  "filename": "report.pdf",
  "mime": "application/pdf",
  "size": 123456,
  "expires_at": "2026-10-06T14:00:00+00:00",
  "request_id": "abc123"
}



---

### POST /api/admin/cleanup (Phase 7)

Manually trigger expired-file sweep. Idempotent.

**Response 200**
```json
{
  "expired_found": 3,
  "deleted_disk": 3,
  "deleted_db": 3,
  "failed": 0,
  "elapsed_ms": 5,
  "request_id": "abc"
}