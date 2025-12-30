from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models
from app.api.schemas import SourceOut, CreateSourceIn

router = APIRouter()

@router.get("", response_model=list[SourceOut])
def list_sources():
    with get_db() as db:
        sources = db.query(models.Source).order_by(models.Source.id.desc()).all()
        return [SourceOut(id=s.id, name=s.name, kind=s.kind, url=s.url) for s in sources]

@router.post("", response_model=SourceOut)
def create_source(payload: CreateSourceIn):
    with get_db() as db:
        exists = db.query(models.Source).filter(models.Source.url == payload.url).first()
        if exists:
            raise HTTPException(status_code=409, detail="Source already exists")
        s = models.Source(name=payload.name, kind=payload.kind, url=payload.url)
        db.add(s)
        db.commit()
        db.refresh(s)
        return SourceOut(id=s.id, name=s.name, kind=s.kind, url=s.url)
