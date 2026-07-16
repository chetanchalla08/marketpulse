"""
Database layer: schema definitions and connection handling.

Two tables:
- indicator_snapshots: every time we screen the watchlist, we store the
  computed indicator values for each ticker. This builds a historical
  record over time, which we'll need for Week 4's backtesting.
- signals: every time a rule actually triggers (e.g. RSI oversold + price
  above VWAP), we log it here. This is the "alert history."

Run `python -m src.db` once to create the tables in your Supabase database.
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()


class IndicatorSnapshot(Base):
    """One row = one ticker's indicator values at one point in time."""
    __tablename__ = "indicator_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_hist = Column(Float)
    vwap = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Signal(Base):
    """One row = one rule triggering for one ticker at one point in time."""
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    rule_name = Column(String, nullable=False)
    close_at_signal = Column(Float, nullable=False)
    details = Column(String)  # human-readable description of why it triggered
    created_at = Column(DateTime, default=datetime.utcnow)


class BacktestResult(Base):
    """One row = one rule's outcome stats at one horizon, for one backtest run."""
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_at = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    rule_name = Column(String, nullable=False, index=True)
    horizon_days = Column(Integer, nullable=False)
    trigger_count = Column(Integer, nullable=False)
    win_rate_pct = Column(Float, nullable=False)
    avg_return_pct = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_engine():
    if not DATABASE_URL:
        raise EnvironmentError(
            "DATABASE_URL not found in .env. "
            "Add your Supabase connection string to .env first."
        )
    return create_engine(DATABASE_URL)


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def create_tables():
    """Creates the tables in the database if they don't already exist."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Tables created (or already existed): indicator_snapshots, signals")


if __name__ == "__main__":
    create_tables()
