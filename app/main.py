from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.security import APIKeyHeader

from app.core.db import init_db
from app.routes import auth, admin, company, menu, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await init_db()
    print("Database initialized.")
    yield
    print("Shutting down...")

app = FastAPI(
    lifespan=lifespan,
    title="Online Menu API",
    version="2.0.0",
    description="API for managing online menus for cafes and restaurants."
)

app.mount("/static", StaticFiles(directory="./uploads"), name="static")

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(company.router, prefix="/api/company", tags=["Company"])
app.include_router(menu.router, prefix="/api/menu", tags=["Public Menu"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Online Menu API!"}