from typing import Dict, Any, Optional
import time

from backend.agents.parser_agent import ParserAgent
from backend.agents.debater_agent import DebaterAgent
from backend.agents.educator_agent import EducatorAgent
from backend.agents.bias_agent import BiasAgent
from backend.lkb.builder import LKBBuilder
from backend.db.journal import DecisionJournal

class SwarmOrchestrator:
    """Async State Machine coordinating parsing, scraping, LKB grounding, adversarial debate, and persistence."""

    def __init__(self):
        self.lkb_builder = LKBBuilder()
        self.journal = DecisionJournal()

    def process_investment_query(self, user_query: str, tone_level: int = 3) -> Dict[str, Any]:
        start_time = time.time()

        # Step 1: Parse User Hypothesis
        thesis = ParserAgent.parse(user_query, tone_level=tone_level)

        # Step 2: Ingest Data & Compile Local Knowledge Base (LKB)
        lkb_packet = self.lkb_builder.build_equity_packet(thesis.symbol, exchange=thesis.exchange)

        # Step 3: Mount Adversarial Red-Team Counter-Thesis
        adversarial_text = DebaterAgent.argue(thesis, lkb_packet)

        # Step 4: Detect Cognitive Biases in User Rationale
        detected_biases = BiasAgent.analyze_rationale(thesis.user_rationale)

        # Step 5: Synthesize Grounded Pre-Mortem Report & Calculate Friction Score
        pre_mortem = EducatorAgent.synthesize(thesis, lkb_packet, adversarial_text, biases=detected_biases)

        # Extract current market price for journal
        current_price = None
        for f in lkb_packet.facts:
            if "Current Market Price" in f.metric and isinstance(f.value, (int, float)):
                current_price = float(f.value)
                break

        # Step 5: Persist Decision & Pre-Mortem to DuckDB Journal
        self.journal.save_decision(
            session_id=lkb_packet.session_id,
            symbol=thesis.symbol,
            exchange=thesis.exchange,
            action=thesis.action.value,
            target_price=thesis.target_price,
            current_price=current_price,
            friction_score=pre_mortem.friction_score,
            tone_level=tone_level,
            headline_verdict=pre_mortem.headline_verdict,
            pre_mortem_dict=pre_mortem.model_dump(),
            lkb_packet_dict=lkb_packet.model_dump()
        )

        elapsed_seconds = round(time.time() - start_time, 2)

        return {
            "session_id": lkb_packet.session_id,
            "elapsed_seconds": elapsed_seconds,
            "thesis": thesis.model_dump(),
            "adversarial_counter_thesis": adversarial_text,
            "pre_mortem": pre_mortem.model_dump(),
            "lkb_packet": lkb_packet.model_dump()
        }
