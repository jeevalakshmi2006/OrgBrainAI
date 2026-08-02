from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import engine, Base
from config import settings

# Import models so SQLAlchemy knows about all tables before create_all
import models  # noqa: F401

from routers import auth_router, admin_router, interview_router, twin_router, sop_router, analytics_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OrgBrain AI",
    description="Organizational Knowledge Preservation & Department AI Twin Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RuntimeError)
async def llm_error_handler(request: Request, exc: RuntimeError):
    """Turns LLM provider failures into a clean, actionable 502 instead of a raw 500."""
    return JSONResponse(status_code=502, content={"detail": str(exc)})


app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(interview_router.router)
app.include_router(twin_router.router)
app.include_router(sop_router.router)
app.include_router(analytics_router.router)


@app.get("/")
def root():
    return {"status": "OrgBrain AI backend is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
