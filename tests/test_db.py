"""Tests for src/db.py"""
import pytest
import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db import UpgradeHistory, UpgradeRecord


@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        path = f.name
    history = UpgradeHistory(path)
    yield history
    history.close()
    os.unlink(path)


def test_insert_and_retrieve(db):
    record = UpgradeRecord(
        paper_arxiv_id="2402.03300",
        paper_title="Test Paper",
        skill_name="test-skill",
        baseline_success_rate=0.80,
        upgraded_success_rate=0.88,
        baseline_cost_tokens=1000,
        upgraded_cost_tokens=1100,
        decision="kept",
    )
    record_id = db.insert(record)
    assert record_id > 0

    records = db.get_all()
    assert len(records) == 1
    assert records[0].paper_arxiv_id == "2402.03300"
    assert records[0].decision == "kept"
    assert records[0].skill_name == "test-skill"


def test_get_by_decision(db):
    db.insert(UpgradeRecord(
        paper_arxiv_id="1", skill_name="a", paper_title="T1",
        decision="kept",
        baseline_success_rate=0.8, upgraded_success_rate=0.9,
        baseline_cost_tokens=1000, upgraded_cost_tokens=1000))
    db.insert(UpgradeRecord(
        paper_arxiv_id="2", skill_name="b", paper_title="T2",
        decision="reverted",
        baseline_success_rate=0.8, upgraded_success_rate=0.8,
        baseline_cost_tokens=1000, upgraded_cost_tokens=1000))

    kept = db.get_by_decision("kept")
    assert len(kept) == 1
    assert kept[0].paper_arxiv_id == "1"


def test_get_stats(db):
    db.insert(UpgradeRecord(
        paper_arxiv_id="1", skill_name="a", paper_title="T1",
        decision="kept",
        baseline_success_rate=0.8, upgraded_success_rate=0.9,
        baseline_cost_tokens=1000, upgraded_cost_tokens=1000))
    db.insert(UpgradeRecord(
        paper_arxiv_id="2", skill_name="b", paper_title="T2",
        decision="kept",
        baseline_success_rate=0.7, upgraded_success_rate=0.85,
        baseline_cost_tokens=1000, upgraded_cost_tokens=1000))

    stats = db.get_stats()
    assert stats["total"] == 2
    assert stats["kept"] == 2
    assert stats["reverted"] == 0
    assert abs(stats["avg_delta"] - 0.125) < 0.001


def test_get_all_returns_most_recent_first(db):
    import time
    r1id = db.insert(UpgradeRecord(
        paper_arxiv_id="1", skill_name="a", paper_title="T1",
        decision="kept",
        baseline_success_rate=0.8, upgraded_success_rate=0.9,
        baseline_cost_tokens=1000, upgraded_cost_tokens=1000))
    time.sleep(0.05)
    r2id = db.insert(UpgradeRecord(
        paper_arxiv_id="2", skill_name="b", paper_title="T2",
        decision="reverted",
        baseline_success_rate=0.8, upgraded_success_rate=0.8,
        baseline_cost_tokens=1000, upgraded_cost_tokens=1000))

    records = db.get_all()
    assert records[0].paper_arxiv_id == "2"
    assert records[1].paper_arxiv_id == "1"


def test_empty_db_returns_empty_lists(db):
    assert db.get_all() == []
    assert db.get_by_decision("kept") == []
    stats = db.get_stats()
    assert stats["total"] == 0
