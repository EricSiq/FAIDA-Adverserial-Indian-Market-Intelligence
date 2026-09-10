from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AssetClass(str, Enum):
    EQUITY = "EQUITY"
    BOND = "BOND"
    COMMODITY = "COMMODITY"

class InvestmentAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class ToneLevel(int, Enum):
    SOCRATIC_EDUCATOR = 1      # Gentle, beginner analogies
    MINDFUL_MENTOR = 2         # Balanced caution & explanations
    PRAGMATIC_RISK_OFFICER = 3 # Institutional risk manager (default)
    CYNICAL_CONTRARIAN = 4     # Skeptical of narratives
    HARDCORE_SHORT_SELLER = 5  # Forensic roaster, aggressive
    QUANT_FORENSIC = 6         # Zero fluff, pure stats/ratios

class LKBFactCategory(str, Enum):
    TECHNICAL = "TECHNICAL"
    LIQUIDITY = "LIQUIDITY"
    VALUATION = "VALUATION"
    GOVERNANCE = "GOVERNANCE"
    MACRO = "MACRO"
    NEWS = "NEWS"

class LKBFact(BaseModel):
    id: str = Field(..., description="Fact citation ID e.g. LKB-01")
    category: LKBFactCategory
    source: str = Field(..., description="Source identifier e.g. NSE_LIVE, SCREENER, YFINANCE, CCIL")
    metric: str
    value: Any
    unit: str = ""
    context: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class LKBPacket(BaseModel):
    session_id: str
    symbol: str
    exchange: str = "NSE"
    asset_class: AssetClass = AssetClass.EQUITY
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    facts: List[LKBFact] = []
    metadata: Dict[str, Any] = {}

class UserThesis(BaseModel):
    raw_query: str
    symbol: str
    exchange: str = "NSE"
    asset_class: AssetClass = AssetClass.EQUITY
    action: InvestmentAction = InvestmentAction.BUY
    target_price: Optional[float] = None
    user_rationale: str = ""
    time_horizon: str = "MEDIUM_TERM"
    tone_level: ToneLevel = ToneLevel.PRAGMATIC_RISK_OFFICER

class PreMortemRiskItem(BaseModel):
    risk_title: str
    severity: str  # HIGH, MEDIUM, LOW
    argument: str
    lkb_citations: List[str] = []

class PreMortemReport(BaseModel):
    symbol: str
    action_analyzed: InvestmentAction
    friction_score: int = Field(..., ge=0, le=100, description="Adversarial Friction Score (0-100)")
    headline_verdict: str
    tone_level_used: ToneLevel
    bearish_risks: List[PreMortemRiskItem] = []
    bullish_traps: List[str] = []
    blind_spots: List[str] = []
    invalidation_levels: Dict[str, Any] = {}
    educational_takeaways: List[str] = []
    lkb_packet: Optional[LKBPacket] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
