import duckdb
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from backend.config import settings

class DecisionJournal:
    """Embedded DuckDB repository tracking past investment decisions, LKB snapshots, and pre-mortems."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DB_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return duckdb.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decisions_journal (
                    id VARCHAR PRIMARY KEY,
                    symbol VARCHAR NOT NULL,
                    exchange VARCHAR DEFAULT 'NSE',
                    action VARCHAR NOT NULL,
                    target_price DOUBLE,
                    current_price DOUBLE,
                    friction_score INTEGER,
                    tone_level INTEGER,
                    headline_verdict VARCHAR,
                    pre_mortem_json VARCHAR,
                    lkb_packet_json VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_decision(
        self,
        session_id: str,
        symbol: str,
        exchange: str,
        action: str,
        target_price: Optional[float],
        current_price: Optional[float],
        friction_score: int,
        tone_level: int,
        headline_verdict: str,
        pre_mortem_dict: Dict[str, Any],
        lkb_packet_dict: Dict[str, Any]
    ) -> bool:
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO decisions_journal (
                        id, symbol, exchange, action, target_price, current_price,
                        friction_score, tone_level, headline_verdict,
                        pre_mortem_json, lkb_packet_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    session_id,
                    symbol.upper(),
                    exchange.upper(),
                    action.upper(),
                    target_price,
                    current_price,
                    friction_score,
                    tone_level,
                    headline_verdict,
                    json.dumps(pre_mortem_dict),
                    json.dumps(lkb_packet_dict)
                ))
            return True
        except Exception as err:
            print(f"[DecisionJournal] Save error: {err}")
            return False

    def list_recent_decisions(self, limit: int = 20) -> List[Dict[str, Any]]:
        safe_limit = max(1, min(100, int(limit)))
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, symbol, exchange, action, target_price, current_price,
                       friction_score, tone_level, headline_verdict, created_at
                FROM decisions_journal
                ORDER BY created_at DESC
                LIMIT ?
            """, (safe_limit,))
            cols = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(cols, row)) for row in rows]

    def get_decision_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM decisions_journal WHERE id = ?
            """, (session_id,))
            row = cursor.fetchone()
            if not row:
                return None
            cols = [desc[0] for desc in cursor.description]
            res = dict(zip(cols, row))
            res["pre_mortem"] = json.loads(res["pre_mortem_json"]) if res.get("pre_mortem_json") else None
            res["lkb_packet"] = json.loads(res["lkb_packet_json"]) if res.get("lkb_packet_json") else None
            return res
