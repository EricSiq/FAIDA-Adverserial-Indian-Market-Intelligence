import pytest
from backend.agents.bias_agent import BiasAgent

def test_detect_anchoring_bias():
    text = "Tata Motors used to be at 1200, now at 980 so it is a bargain."
    biases = BiasAgent.analyze_rationale(text)
    assert len(biases) >= 1
    assert any(b.bias_name == "Anchoring Bias" for b in biases)

def test_detect_loss_aversion_bias():
    text = "I am holding until break-even, cannot book a loss now."
    biases = BiasAgent.analyze_rationale(text)
    assert len(biases) >= 1
    assert any(b.bias_name == "Loss Aversion & Sunk Cost Fallacy" for b in biases)

def test_detect_fomo_bias():
    text = "Reliance has gained 15% in 3 days, it is rallying to the moon!"
    biases = BiasAgent.analyze_rationale(text)
    assert len(biases) >= 1
    assert any(b.bias_name == "FOMO & Recency Bias" for b in biases)

def test_clean_rational_query_no_biases():
    text = "Selling 200 shares to rebalance asset allocation into debt."
    biases = BiasAgent.analyze_rationale(text)
    assert len(biases) == 0
