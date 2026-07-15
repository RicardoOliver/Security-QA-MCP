from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.interfaces.api.v1.auth_router import router as auth_router
from app.interfaces.api.v1.router import api_router
from app.interfaces.mcp.tools import router as mcp_router

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(mcp_router)


@app.get("/health", tags=["health"], summary="Health check")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.on_event("startup")
def startup_event() -> None:
    init_db()
