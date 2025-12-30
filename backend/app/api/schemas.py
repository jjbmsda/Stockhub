from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class SourceOut(BaseModel):
    id: int
    name: str
    kind: str
    url: str

class ReportOut(BaseModel):
    id: int
    title: str
    published_at: datetime
    source_id: int

class TickerOut(BaseModel):
    symbol: str
    name: str

class TickerSummaryOut(BaseModel):
    symbol: str
    asof_date: str
    summary: str
    bullets: List[str]
    confidence: int

class CreateTickerIn(BaseModel):
    symbol: str
    name: str

class CreateSourceIn(BaseModel):
    name: str
    kind: str
    url: str

class RunDailyOut(BaseModel):
    fetched_reports: int
    mentions_created: int
    summaries_created: int
    asof_date: str
