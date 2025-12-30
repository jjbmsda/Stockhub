from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import init_db
from app.api.router import api_router

app = FastAPI(title=settings.APP_NAME)

# CORS for local dev (frontend on 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(api_router)

@app.get("/health")
def health():
    return {"ok": True, "env": settings.ENV}
