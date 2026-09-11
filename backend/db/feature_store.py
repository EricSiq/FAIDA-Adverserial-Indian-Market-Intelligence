import duckdb
from typing import Dict, Any, Optional
import json
import time
from pathlib import Path
import threading
from backend.config import settings

class FeatureStore:
    """Local embedded DuckDB feature cache for high-frequency market data and fundamentals."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.FEATURE_STORE_PATH
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.conn = duckdb.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        with self._lock:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS market_features_cache (
                    cache_key VARCHAR PRIMARY KEY,
                    symbol VARCHAR NOT NULL,
                    feature_type VARCHAR NOT NULL,
                    payload_json VARCHAR NOT NULL,
                    ttl_seconds INTEGER NOT NULL,
                    updated_at DOUBLE NOT NULL
                )
            """)

    @staticmethod
    def _make_key(symbol: str, feature_type: str) -> str:
        sym = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        ft = feature_type.strip().upper()
        return f"{sym}:{ft}"

    def set(self, symbol: str, feature_type: str, data: Dict[str, Any], ttl_seconds: int = 900) -> bool:
        """Saves a feature payload with a specified TTL in seconds."""
        cache_key = self._make_key(symbol, feature_type)
        sym = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        ft = feature_type.strip().upper()
        now = time.time()
        payload = json.dumps(data)

        try:
            with self._lock:
                self.conn.execute("""
                    INSERT OR REPLACE INTO market_features_cache (
                        cache_key, symbol, feature_type, payload_json, ttl_seconds, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (cache_key, sym, ft, payload, ttl_seconds, now))
            return True
        except Exception:
            return False

    def get(self, symbol: str, feature_type: str) -> Optional[Dict[str, Any]]:
        """Retrieves a cached feature payload if still valid under TTL."""
        cache_key = self._make_key(symbol, feature_type)
        now = time.time()

        try:
            with self._lock:
                res = self.conn.execute("""
                    SELECT payload_json, ttl_seconds, updated_at 
                    FROM market_features_cache 
                    WHERE cache_key = ?
                """, (cache_key,)).fetchone()

            if not res:
                return None

            payload_json, ttl_seconds, updated_at = res
            if (now - updated_at) <= ttl_seconds:
                return json.loads(payload_json)
            else:
                return None
        except Exception:
            return None

    def clear_expired(self) -> int:
        """Purges stale cache entries beyond TTL."""
        now = time.time()
        try:
            with self._lock:
                res = self.conn.execute("""
                    DELETE FROM market_features_cache 
                    WHERE (? - updated_at) > ttl_seconds
                    RETURNING cache_key
                """, (now,)).fetchall()
                return len(res)
        except Exception:
            return 0

    def clear_all(self):
        """Purges all entries (primarily for test resets)."""
        try:
            with self._lock:
                self.conn.execute("DELETE FROM market_features_cache")
        except Exception:
            pass

    def close(self):
        """Closes the underlying DuckDB connection."""
        try:
            with self._lock:
                self.conn.close()
        except Exception:
            pass
