import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

class TradingDatabase:
    def __init__(self, db_path="trading_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    volume INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS trading_signals (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    signal TEXT NOT NULL,
                    confidence REAL,
                    indicators TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS portfolio_positions (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    avg_price REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS market_alerts (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT,
                    triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_stock_symbol ON stock_prices(symbol);
                CREATE INDEX IF NOT EXISTS idx_signal_symbol ON trading_signals(symbol);
            """)
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def save_stock_price(self, symbol, price, volume=None):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO stock_prices (symbol, price, volume) VALUES (?, ?, ?)",
                (symbol, price, volume)
            )
    
    def save_trading_signal(self, symbol, signal, confidence, indicators=None):
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO trading_signals (symbol, signal, confidence, indicators) VALUES (?, ?, ?, ?)",
                (symbol, signal, confidence, json.dumps(indicators) if indicators else None)
            )
    
    def get_latest_signals(self, limit=10):
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM trading_signals ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_portfolio(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM portfolio_positions WHERE user_id = ?",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]