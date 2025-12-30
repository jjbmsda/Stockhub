import os
import hashlib
import json
from datetime import datetime, date
from typing import List, Dict

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import get_db
from app.db import models
from app.services.http_client import get
from app.services.text_extract import extract_text_from_html, extract_text_from_pdf
from app.services.mentions import extract_mentions
from app.services.summarizer import summarize_snippets

logger = get_logger(__name__)

def _split_csv(s: str) -> List[str]:
    return [x.strip() for x in (s or "").split(",") if x.strip()]

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _upsert_source(db: Session, name: str, kind: str, url: str) -> models.Source:
    row = db.query(models.Source).filter(models.Source.url == url).first()
    if row:
        return row
    row = models.Source(name=name, kind=kind, url=url)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

def _store_report(db: Session, source: models.Source, title: str, published_at: datetime, raw_text: str) -> models.Report | None:
    h = _sha256(raw_text)
    exists = db.query(models.Report).filter(models.Report.source_id == source.id, models.Report.raw_hash == h).first()
    if exists:
        return None
    r = models.Report(source_id=source.id, title=title or source.name, published_at=published_at, raw_text=raw_text, raw_hash=h)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

def _ensure_default_tickers(db: Session):
    # Minimal starter tickers; you can add via API later.
    defaults = [
        ("005930", "삼성전자"),
        ("000660", "SK하이닉스"),
        ("005380", "현대차"),
        ("035420", "NAVER"),
        ("035720", "카카오"),
    ]
    for sym, name in defaults:
        if not db.query(models.Ticker).filter(models.Ticker.symbol == sym).first():
            db.add(models.Ticker(symbol=sym, name=name))
    db.commit()

def fetch_reports(db: Session) -> List[models.Report]:
    reports = []
    now = datetime.utcnow()

    # HTML sources
    for url in _split_csv(settings.NAVER_MOBILE_RESEARCH_URLS):
        source = _upsert_source(db, name="Naver Research", kind="html", url=url)
        html = get(url).text
        text, title = extract_text_from_html(html)
        r = _store_report(db, source, title=title or "Naver Research", published_at=now, raw_text=text)
        if r:
            reports.append(r)

    # PDF sources
    pdf_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "pdf")
    pdf_dir = os.path.abspath(pdf_dir)
    os.makedirs(pdf_dir, exist_ok=True)

    for i, url in enumerate(_split_csv(settings.PDF_URLS)):
        source = _upsert_source(db, name="PDF Source", kind="pdf", url=url)
        resp = get(url)
        path = os.path.join(pdf_dir, f"report_{i}.pdf")
        with open(path, "wb") as f:
            f.write(resp.content)
        text = extract_text_from_pdf(path)
        r = _store_report(db, source, title="PDF Report", published_at=now, raw_text=text)
        if r:
            reports.append(r)

    return reports

def create_mentions(db: Session, reports: List[models.Report]) -> int:
    tickers = db.query(models.Ticker).all()
    created = 0
    for rep in reports:
        for t in tickers:
            snippets = extract_mentions(rep.raw_text, t.symbol, t.name)
            if not snippets:
                continue
            # upsert mention
            m = (
                db.query(models.Mention)
                .filter(models.Mention.report_id == rep.id, models.Mention.ticker_id == t.id)
                .first()
            )
            if not m:
                m = models.Mention(report_id=rep.id, ticker_id=t.id, snippets="\n".join(snippets))
                db.add(m)
                created += 1
            else:
                # merge append (avoid duplicates roughly)
                existing = set((m.snippets or "").split("\n"))
                merged = list(existing.union(snippets))
                m.snippets = "\n".join(merged)
    db.commit()
    return created

async def create_summaries(db: Session, asof_date: str) -> int:
    created = 0
    tickers = db.query(models.Ticker).all()
    for t in tickers:
        mentions = (
            db.query(models.Mention)
            .join(models.Report, models.Mention.report_id == models.Report.id)
            .filter(models.Mention.ticker_id == t.id)
            .order_by(models.Report.published_at.desc())
            .limit(50)
            .all()
        )
        snippets = []
        for m in mentions:
            snippets.extend([x.strip() for x in (m.snippets or "").split("\n") if x.strip()])

        # if already exists for date, skip
        if db.query(models.TickerSummary).filter(models.TickerSummary.symbol == t.symbol, models.TickerSummary.asof_date == asof_date).first():
            continue

        result = await summarize_snippets(snippets[:40])
        summary = models.TickerSummary(
            symbol=t.symbol,
            asof_date=asof_date,
            summary=result.get("summary", ""),
            bullets=json.dumps(result.get("bullets", []), ensure_ascii=False),
            confidence=int(result.get("confidence", 50)),
        )
        db.add(summary)
        created += 1
    db.commit()
    return created

def run_daily_pipeline() -> Dict:
    asof_date = date.today().isoformat()
    with get_db() as db:
        _ensure_default_tickers(db)
        reports = fetch_reports(db)
        mentions_created = create_mentions(db, reports)

    # Summaries need async
    import asyncio
    with get_db() as db:
        summaries_created = asyncio.run(create_summaries(db, asof_date))

    return {
        "fetched_reports": len(reports),
        "mentions_created": mentions_created,
        "summaries_created": summaries_created,
        "asof_date": asof_date,
    }

if __name__ == "__main__":
    print(run_daily_pipeline())
