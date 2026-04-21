from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from contextlib import asynccontextmanager
from slowapi.middleware import SlowAPIMiddleware

from app.routes import auth, admin, company, menu, upload
from app.core.rate_limit import limiter



app = FastAPI(
    title="Online Menu API",
    version="2.0.0",
    description="API for managing online menus for cafes and restaurants."
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="./uploads"), name="uploads")
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(company.router, prefix="/api/company", tags=["Company"])
app.include_router(menu.router, prefix="/api/menu", tags=["Public Menu"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Online Menu API!"}