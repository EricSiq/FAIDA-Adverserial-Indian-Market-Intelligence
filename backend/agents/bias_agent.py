from typing import List, Dict, Any
import re
from pydantic import BaseModel

class DetectedBias(BaseModel):
    bias_name: str
    severity: str  # HIGH, MEDIUM, LOW
    matched_phrase: str
    psychological_trap: str
    reframing_advice: str

class BiasAgent:
    """Detects cognitive biases and behavioral traps in retail investor theses."""

    BIAS_RULES = [
        {
            "name": "Anchoring Bias",
            "severity": "HIGH",
            "patterns": [
                r"\b(?:used to be|was at|down from|fell from|corrected from|peak of|trading below its high|cheap compared to)\b",
                r"\b(?:52[- ]?week high|all[- ]?time high|discount from peak)\b"
            ],
            "trap": "Fixating on a past peak price as an anchor of 'true value', ignoring structural business or margin deterioration.",
            "reframing": "Ask: If this company never traded at that historical high, would you still buy it at today's multiple based on current cash flows?"
        },
        {
            "name": "Loss Aversion & Sunk Cost Fallacy",
            "severity": "HIGH",
            "patterns": [
                r"\b(?:hold(?:ing)? until break[- ]?even|recover my loss|down \d+%|average down|cannot book loss|trapped in)\b"
            ],
            "trap": "Refusing to accept a paper loss, locking up capital in stagnant or deteriorating businesses.",
            "reframing": "Opportunity Cost Check: If you were in 100% cash today, would you deploy fresh capital into this exact stock, or park it in 7.1% G-Secs?"
        },
        {
            "name": "FOMO & Recency Bias",
            "severity": "MEDIUM",
            "patterns": [
                r"\b(?:gained \d+%|up \d+% in|surging|parabolic|rallying|everyone is buying|to the moon|multibagger)\b",
                r"\b(?:missing out|can't miss|going to double)\b"
            ],
            "trap": "Extrapolating recent rapid price momentum into the future, frequently entering during institutional distribution.",
            "reframing": "Check Institutional Conviction: High price velocity on low delivery percentage (<25%) indicates retail frenzy susceptible to sharp reversals."
        },
        {
            "name": "Lottery Ticket & Turnaround Fallacy",
            "severity": "HIGH",
            "patterns": [
                r"\b(?:penny stock|turnaround|cheap at ₹?\d{1,2}|dirt cheap|multi[- ]?bagger potential|can 10x)\b"
            ],
            "trap": "Overweighting low-probability exponential returns while underestimating permanent capital loss via insolvency or dilution.",
            "reframing": "Examine Free Cash Flow: Over 85% of turnaround narratives in Indian markets fail to generate positive Operating Cash Flow (CFO)."
        },
        {
            "name": "Social Proof & Confirmation Bias",
            "severity": "MEDIUM",
            "patterns": [
                r"\b(?:telegram|whatsapp|tip|hot stock|analyst said|news buzz|rumou?r|target price given)\b"
            ],
            "trap": "Relying on social consensus or unverified tips rather than audited balance sheets and regulatory filings.",
            "reframing": "Verification Rule: Never trade on secondary tips without inspecting promoter pledging and auditor disclosures on BSE/NSE."
        }
    ]

    @classmethod
    def analyze_rationale(cls, text: str) -> List[DetectedBias]:
        if not text or not isinstance(text, str):
            return []

        detected = []
        lower_text = text.lower()

        for rule in cls.BIAS_RULES:
            for pattern in rule["patterns"]:
                match = re.search(pattern, lower_text, re.IGNORECASE)
                if match:
                    matched_phrase = match.group(0)
                    detected.append(DetectedBias(
                        bias_name=rule["name"],
                        severity=rule["severity"],
                        matched_phrase=matched_phrase,
                        psychological_trap=rule["trap"],
                        reframing_advice=rule["reframing"]
                    ))
                    break  # Trigger each bias at most once per query

        return detected
