"""
FAIDA: Financial Adversarial Indian Data Agents
Module: backend.agents.orchestrator
Description:
    Core Swarm Orchestrator implementing an asynchronous state machine that coordinates
    natural language thesis parsing, real-time multi-source data scraping, Local Knowledge
    Base (LKB) compilation, adversarial red-team counter-argumentation, cognitive bias
    detection, and institutional pre-mortem report persistence.
"""

from typing import Dict, Any, Optional
import time

from backend.agents.parser_agent import ParserAgent
from backend.agents.debater_agent import DebaterAgent
from backend.agents.educator_agent import EducatorAgent
from backend.agents.bias_agent import BiasAgent
from backend.lkb.builder import LKBBuilder
from backend.db.journal import DecisionJournal


class SwarmOrchestrator:
    """
    Asynchronous State Machine coordinating the FAIDA agent swarm.
    
    Pipeline Stages:
        1. Thesis Parsing (ParserAgent):
           Deconstructs natural language retail input into structured UserThesis
           (symbol, exchange, investment action, target price, tone continuum).
        2. Grounded Data Ingestion (LKBBuilder):
           Collects and normalizes live market technicals (NSE/YFinance), fundamental
           accounting ratios (Screener.in), governance red flags (BSE Filings), 
           macro indices (India VIX, 10Y G-Sec, FRED API), and news catalysts (Finnhub API).
        3. Adversarial Red-Teaming (DebaterAgent):
           Mounts a zero-hallucination, evidence-grounded counter-thesis against the user's
           position using strictly verified [LKB-XX] citation tags.
        4. Cognitive Bias Detection (BiasAgent):
           Scans user rationale for psychological traps (Anchoring, Sunk Cost, FOMO,
           Lottery Fallacy, Social Confirmation) and generates reframing prompts.
        5. Synthesis & Persisted Journaling (EducatorAgent & DecisionJournal):
           Calculates the deterministic Adversarial Friction Score (AFS), compiles the
           final PreMortemReport, and commits the immutable audit trail into DuckDB.
    """

    def __init__(self):
        """Initializes the LKB builder and DuckDB decision journal."""
        self.lkb_builder = LKBBuilder()
        self.journal = DecisionJournal()

    def process_investment_query(self, user_query: str, tone_level: int = 3) -> Dict[str, Any]:
        """
        Executes the end-to-end adversarial evaluation pipeline for a user investment thesis.
        
        Args:
            user_query: Unstructured text describing the investor's intent (e.g., 'Want to buy Reliance at 2950').
            tone_level: Integer from 1 (Socratic Educator) to 6 (Quant Forensic Analyst).
            
        Returns:
            Dict containing session_id, execution latency, parsed thesis, adversarial rebuttal,
            pre-mortem report, and the complete Local Knowledge Base fact packet.
        """
        start_time = time.time()

        # -------------------------------------------------------------------------
        # Step 1: Parse User Hypothesis & Extract Entities
        # -------------------------------------------------------------------------
        thesis = ParserAgent.parse(user_query, tone_level=tone_level)

        # -------------------------------------------------------------------------
        # Step 2: Ingest Data & Compile Grounded Local Knowledge Base (LKB)
        # -------------------------------------------------------------------------
        lkb_packet = self.lkb_builder.build_equity_packet(
            thesis.symbol,
            exchange=thesis.exchange,
            user_query=user_query
        )

        # -------------------------------------------------------------------------
        # Step 3: Mount Adversarial Red-Team Counter-Thesis (Strict Grounding)
        # -------------------------------------------------------------------------
        adversarial_text = DebaterAgent.argue(thesis, lkb_packet)

        # -------------------------------------------------------------------------
        # Step 4: Detect Cognitive Biases & Behavioral Traps in User Rationale
        # -------------------------------------------------------------------------
        detected_biases = BiasAgent.analyze_rationale(thesis.user_rationale)

        # -------------------------------------------------------------------------
        # Step 5: Synthesize Grounded Pre-Mortem Report & Calculate Friction Score
        # -------------------------------------------------------------------------
        pre_mortem = EducatorAgent.synthesize(thesis, lkb_packet, adversarial_text, biases=detected_biases)

        # Extract current market price for journal record keeping
        current_price = None
        for f in lkb_packet.facts:
            if "Current Market Price" in f.metric and isinstance(f.value, (int, float)):
                current_price = float(f.value)
                break

        # -------------------------------------------------------------------------
        # Step 6: Persist Decision & Pre-Mortem Audit Record to DuckDB Journal
        # -------------------------------------------------------------------------
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

