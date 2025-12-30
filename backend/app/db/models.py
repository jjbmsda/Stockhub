from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.db.base import Base

class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    kind: Mapped[str] = mapped_column(String(50), nullable=False)  # html | pdf
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)

    reports: Mapped[list["Report"]] = relationship(back_populates="source")

class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        UniqueConstraint("source_id", "published_at", name="uq_report_source_pub"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(400), nullable=False, default="")
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    raw_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    source: Mapped["Source"] = relationship(back_populates="reports")
    mentions: Mapped[list["Mention"]] = relationship(back_populates="report", cascade="all, delete-orphan")

class Ticker(Base):
    __tablename__ = "tickers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # e.g., 005930
    name: Mapped[str] = mapped_column(String(200), nullable=False)               # e.g., 삼성전자

    mentions: Mapped[list["Mention"]] = relationship(back_populates="ticker")

class Mention(Base):
    __tablename__ = "mentions"
    __table_args__ = (
        UniqueConstraint("report_id", "ticker_id", name="uq_mention_report_ticker"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"), nullable=False)
    ticker_id: Mapped[int] = mapped_column(ForeignKey("tickers.id"), nullable=False)

    # extracted snippets (lightweight)
    snippets: Mapped[str] = mapped_column(Text, nullable=False, default="")

    report: Mapped["Report"] = relationship(back_populates="mentions")
    ticker: Mapped["Ticker"] = relationship(back_populates="mentions")

class TickerSummary(Base):
    __tablename__ = "ticker_summaries"
    __table_args__ = (
        UniqueConstraint("symbol", "asof_date", name="uq_summary_symbol_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    asof_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    bullets: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # json list
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=50)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
