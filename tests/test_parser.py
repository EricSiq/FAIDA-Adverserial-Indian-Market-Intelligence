import pytest
from backend.agents.parser_agent import ParserAgent
from backend.lkb.models import InvestmentAction, ToneLevel

def test_parse_sell_action():
    text = "Thinking of selling Reliance at ₹2900 because crude oil is surging"
    thesis = ParserAgent.parse(text, tone_level=4)
    assert thesis.symbol == "RELIANCE"
    assert thesis.action == InvestmentAction.SELL
    assert thesis.target_price == 2900.0
    assert thesis.tone_level == ToneLevel.CYNICAL_CONTRARIAN

def test_parse_buy_action():
    text = "Want to buy Tata Motors at 980 rupees anticipating EV expansion"
    thesis = ParserAgent.parse(text, tone_level=1)
    assert thesis.symbol == "TATAMOTORS"
    assert thesis.action == InvestmentAction.BUY
    assert thesis.target_price == 980.0
    assert thesis.tone_level == ToneLevel.SOCRATIC_EDUCATOR

def test_parse_infosys_official_ticker():
    text = "Should I buy Infosys at @ 1520?"
    thesis = ParserAgent.parse(text, tone_level=3)
    assert thesis.symbol == "INFY"
    assert thesis.target_price == 1520.0
    assert thesis.action == InvestmentAction.BUY

def test_parse_default_fallbacks():
    text = "Hello market"
    thesis = ParserAgent.parse(text, tone_level=99)  # Invalid tone defaults to 3
    assert thesis.action == InvestmentAction.BUY
    assert thesis.tone_level == ToneLevel.PRAGMATIC_RISK_OFFICER
