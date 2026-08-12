from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_analyze import router as analyze_router
from app.config import settings

app = FastAPI(title="dq-eda-copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

app.include_router(analyze_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}