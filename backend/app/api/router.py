from fastapi import APIRouter
from app.api.routes import sources, reports, tickers

api_router = APIRouter(prefix="/api")
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(tickers.router, prefix="/tickers", tags=["tickers"])
