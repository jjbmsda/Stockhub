import json
from fastapi import APIRouter, HTTPException
from datetime import date
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models
from app.api.schemas import TickerOut, CreateTickerIn, TickerSummaryOut, RunDailyOut
from app.jobs.run_daily import run_daily_pipeline

router = APIRouter()

@router.get("", response_model=list[TickerOut])
def list_tickers():
    with get_db() as db:
        rows = db.query(models.Ticker).order_by(models.Ticker.name.asc()).all()
        return [TickerOut(symbol=t.symbol, name=t.name) for t in rows]

@router.post("", response_model=TickerOut)
def create_ticker(payload: CreateTickerIn):
    with get_db() as db:
        exists = db.query(models.Ticker).filter(models.Ticker.symbol == payload.symbol).first()
        if exists:
            raise HTTPException(status_code=409, detail="Ticker already exists")
        t = models.Ticker(symbol=payload.symbol, name=payload.name)
        db.add(t)
        db.commit()
        return TickerOut(symbol=t.symbol, name=t.name)

@router.get("/{symbol}/summary", response_model=TickerSummaryOut)
def get_summary(symbol: str, asof_date: str | None = None):
    if asof_date is None:
        asof_date = date.today().isoformat()
    with get_db() as db:
        row = (
            db.query(models.TickerSummary)
            .filter(models.TickerSummary.symbol == symbol, models.TickerSummary.asof_date == asof_date)
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="Summary not found")
        bullets = json.loads(row.bullets) if row.bullets else []
        return TickerSummaryOut(
            symbol=row.symbol,
            asof_date=row.asof_date,
            summary=row.summary,
            bullets=bullets,
            confidence=row.confidence,
        )

@router.post("/run-daily", response_model=RunDailyOut)
def run_daily():
    # For local manual triggering.
    result = run_daily_pipeline()
    return result
