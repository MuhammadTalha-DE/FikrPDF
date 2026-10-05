'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health

app = FastAPI(
    title="PDF Love API",
    description="Backend for PDF Love platform",
    version="0.1.0",
)

# CORS — allow Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api", tags=["health"])


@app.get("/")
def root():
    return {"message": "PDF Love API is running", "docs": "/docs"}

'''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health

app = FastAPI(
    title=" FikrPDF  API",
    description="Backend for FikrPDF platform",
    version="0.1.0",
)

# CORS — allow Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, prefix="/api", tags=["health"])


@app.get("/")
def root():
    return {"message": " FikrPDF  API is running", "docs": "/docs"}