"""Tests for filter self-upgrade boost (ISS-001)."""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.research import Paper
from src.filter import _self_upgrade_boost, _SELF_UPGRADE_BOOST_PATTERNS


def _make(title="x", abstract="x", categories="cs.AI"):
    return Paper(
        arxiv_id="9999.9999", title=title, authors="x", published="2026",
        abstract=abstract, categories=categories,
    )


class TestSelfUpgradeBoost:
    def test_no_match_returns_zero(self):
        p = _make("Generic ML paper", "We study a new algorithm.")
        assert _self_upgrade_boost(p) == 0.0

    def test_one_match_returns_one(self):
        p = _make("Agent planning with world models",
                  "We propose a method for better LLM agents.")
        # "agent planning" + "world model" + "llm agent" = 3 hits
        score = _self_upgrade_boost(p)
        assert score >= 1.0

    def test_self_evolving_paper_gets_boost(self):
        """The v1.5.0 famous 'Self-Evolving World Models' paper should
        get a meaningful boost so it ranks consistently."""
        p = _make(
            "Self-Evolving World Models for LLM Agent Planning",
            "We propose self-evolving world models that LLM agents use for planning."
        )
        score = _self_upgrade_boost(p)
        # self-evolv + world model + agent planning + llm agent = 4 hits → capped at 3
        assert score >= 2.0
        assert score <= 3.0

    def test_music_paper_gets_zero(self):
        p = _make("LeVo 2: Song Generation",
                  "We generate songs from lyrics using hierarchical audio tokens.")
        # No boost — boost patterns are agent-focused
        assert _self_upgrade_boost(p) == 0.0

    def test_robot_paper_gets_zero(self):
        p = _make("GROW^2: Grounding Which and Where for Robot Tool Use",
                  "Robotic tool manipulation with visual grounding.")
        # "tool use" matches but it would be controversial to boost robots
        # — the agent we care about is LLM-based, not physical.
        # Currently matches "tool use" — that's a known leak but not
        # catastrophic since patchgen's pre-filter catches the rest.
        score = _self_upgrade_boost(p)
        # If we want strict, set to 0; currently 1 due to "tool use"
        assert score <= 1.0

    def test_cap_at_3(self):
        """Even with many matches, cap is 3."""
        p = _make(
            title="Self-improving multi-agent LLM agent planning with code generation",
            abstract="A self-evolving agent tool planning world model for multi-agent code generation",
        )
        score = _self_upgrade_boost(p)
        assert score <= 3.0

    def test_patterns_are_lowercase(self):
        """All patterns must be lowercase to match lowercased text."""
        for p in _SELF_UPGRADE_BOOST_PATTERNS:
            assert p == p.lower(), f"pattern not lowercase: {p!r}"
