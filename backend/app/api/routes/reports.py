from fastapi import APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.db import models
from app.api.schemas import ReportOut

router = APIRouter()

@router.get("", response_model=list[ReportOut])
def list_reports(days: int = 7):
    cutoff = datetime.utcnow() - timedelta(days=days)
    with get_db() as db:
        rows = (
            db.query(models.Report)
            .filter(models.Report.published_at >= cutoff)
            .order_by(models.Report.published_at.desc())
            .limit(200)
            .all()
        )
        return [ReportOut(id=r.id, title=r.title, published_at=r.published_at, source_id=r.source_id) for r in rows]
