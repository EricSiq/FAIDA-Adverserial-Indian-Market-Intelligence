import pytest
import tempfile
import os
from backend.db.journal import DecisionJournal

@pytest.fixture
def temp_journal():
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, "test_journal.duckdb")
    journal = DecisionJournal(db_path=temp_path)
    yield journal
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except Exception:
            pass

def test_save_and_retrieve_decision(temp_journal):
    success = temp_journal.save_decision(
        session_id="faida-test-save-01",
        symbol="TCS",
        exchange="NSE",
        action="BUY",
        target_price=3900.0,
        current_price=3850.0,
        friction_score=45,
        tone_level=3,
        headline_verdict="MODERATE FRICTION: Mixed signals.",
        pre_mortem_dict={"headline": "Test Pre-Mortem"},
        lkb_packet_dict={"facts": []}
    )
    assert success is True

    # Retrieve by list
    recent = temp_journal.list_recent_decisions(limit=10)
    assert len(recent) == 1
    assert recent[0]["symbol"] == "TCS"
    assert recent[0]["friction_score"] == 45

    # Retrieve by ID
    detail = temp_journal.get_decision_by_id("faida-test-save-01")
    assert detail is not None
    assert detail["symbol"] == "TCS"
    assert detail["pre_mortem"]["headline"] == "Test Pre-Mortem"

def test_get_nonexistent_decision(temp_journal):
    assert temp_journal.get_decision_by_id("non-existent-id") is None
