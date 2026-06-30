"""Tests for src/patchgen.py — verifies surgical-patch generation.

We mock the LLM call to return canned patches, then assert that:
  1. The current source of core/planner.py is included in the prompt.
  2. A patch that defines plan_task() is accepted.
  3. A patch that DOESN'T define plan_task() is rejected (returned None).
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import patchgen
from src.llm import LLMConfig, LLMResponse
from src.research import Paper


# Save the real planner so we don't trample it.
_PLANNER_PATH = os.path.join(
    os.path.dirname(__file__), "..", "core", "planner.py"
)


@pytest.fixture
def fake_paper():
    return Paper(
        arxiv_id="2606.00000",
        title="Chain-of-Thought Decomposition for Agent Planning",
        authors="Test Author",
        published="2026-06-30",
        abstract=(
            "We propose a CoT-style decomposition step for LLM-based task planners "
            "that improves step ordering and reduces hallucination."
        ),
        categories="cs.AI",
    )


class _FakeLLM:
    """Captures the prompt and returns a configured response."""

    def __init__(self, response_content: str):
        self.response_content = response_content
        self.last_prompt = None

    def __call__(self, *args, **kwargs):
        # mimic src.llm.chat(...) shape
        self.last_prompt = kwargs.get("messages", args[0] if args else None)
        return LLMResponse(
            content=self.response_content,
            model="fake",
            attempts=1,
        )


def test_patchgen_includes_current_source_in_prompt(monkeypatch, fake_paper):
    """The prompt must contain the current source of core/planner.py so the
    LLM knows what's already there and writes a surgical patch."""
    good_patch = (
        '{"function": "def plan_task(task, llm_call):\\n'
        '    return [task]",'
        ' "test": "def test_p(): assert plan_task(\'x\', None) == [\'x\']",'
        ' "module": "planner.py"}'
    )
    fake = _FakeLLM(good_patch)
    # patchgen imports `from src.llm import chat` — patch the symbol it uses.
    monkeypatch.setattr(patchgen, "chat", fake)
    cfg = LLMConfig(api_keys=["k"], base_url="http://x", model="m", fallback_models=[])

    result = patchgen.generate_patch(fake_paper, "planner.py", llm_config=cfg)
    assert result is not None, (
        f"expected non-None, last prompt={fake.last_prompt!r}"
    )
    assert result["module"] == "planner.py"
    # The captured prompt is a list of messages; pull the user content.
    user_msg = fake.last_prompt[0]["content"]
    # The current planner's signature must be in the prompt.
    assert "def plan_task" in user_msg
    # The paper title must be in the prompt.
    assert "Chain-of-Thought" in user_msg
    # Constraint language.
    assert "Keep" in user_msg or "constraint" in user_msg.lower()


def test_patchgen_rejects_patch_missing_primary_function(monkeypatch, fake_paper):
    """If the LLM returns a patch that does NOT define plan_task, we reject
    it.  Surgical merge would otherwise misroute the patch (replace some
    other function, or append at the end)."""
    bad_patch = (
        '{"function": "def totally_different_function(x):\\n    return x + 1",'
        ' "test": "def test_tdf(): assert totally_different_function(2) == 3"}'
    )
    fake = _FakeLLM(bad_patch)
    monkeypatch.setattr(patchgen, "chat", fake)
    cfg = LLMConfig(api_keys=["k"], base_url="http://x", model="m", fallback_models=[])

    result = patchgen.generate_patch(fake_paper, "planner.py", llm_config=cfg)
    assert result is None, "patch without plan_task() must be rejected"


def test_patchgen_handles_fenced_json(monkeypatch, fake_paper):
    """Many LLMs wrap JSON in ```json ... ``` fences; our lenient parser
    must handle that without response_format."""
    fenced = (
        '```json\n'
        '{"function": "def plan_task(t, c):\\n    return [t]",'
        ' "test": "def test_p(): assert plan_task(\'x\', None) == [\'x\']"}\n'
        '```'
    )
    fake = _FakeLLM(fenced)
    monkeypatch.setattr(patchgen, "chat", fake)
    cfg = LLMConfig(api_keys=["k"], base_url="http://x", model="m", fallback_models=[])

    result = patchgen.generate_patch(fake_paper, "planner.py", llm_config=cfg)
    assert result is not None
    assert "def plan_task" in result["function"]


def test_patchgen_returns_none_on_garbage(monkeypatch, fake_paper):
    """Garbage in → None out, not a crash."""
    fake = _FakeLLM("totally not JSON, sorry")
    monkeypatch.setattr(patchgen, "chat", fake)
    cfg = LLMConfig(api_keys=["k"], base_url="http://x", model="m", fallback_models=[])

    result = patchgen.generate_patch(fake_paper, "planner.py", llm_config=cfg)
    assert result is None


class TestPaperPreFilter:
    """Patchgen pre-filters papers that are obviously not about AI/ML
    agents (e.g. music generation, image segmentation).  This prevents
    the system from wasting LLM calls on papers filter.py scored too
    generously."""

    def _make(self, title="x", abstract="x", categories="cs.AI"):
        return Paper(
            arxiv_id="9999.9999",
            title=title,
            authors="x",
            published="2026",
            abstract=abstract,
            categories=categories,
        )

    def test_rejects_music_paper(self):
        from src.patchgen import _paper_is_obviously_unrelated
        p = self._make(
            title="LeVo 2: Stable and Melodious Song Generation",
            abstract="hierarchical audio tokens for song generation",
            categories="cs.SD",
        )
        assert _paper_is_obviously_unrelated(p) is True

    def test_rejects_image_segmentation_paper(self):
        from src.patchgen import _paper_is_obviously_unrelated
        p = self._make(
            title="Mask2Former for Image Segmentation",
            abstract="universal image segmentation architecture",
            categories="cs.CV",
        )
        assert _paper_is_obviously_unrelated(p) is True

    def test_accepts_reinforcement_learning_paper(self):
        from src.patchgen import _paper_is_obviously_unrelated
        p = self._make(
            title="Reinforcement Learning for LLM Agent Planning",
            abstract="We use reinforcement learning to improve agent planning.",
            categories="cs.AI",
        )
        assert _paper_is_obviously_unrelated(p) is False

    def test_accepts_prompt_engineering_paper(self):
        from src.patchgen import _paper_is_obviously_unrelated
        p = self._make(
            title="Prompt Engineering for Tool-Use Agents",
            abstract="We study prompt design for LLM-based tool use.",
            categories="cs.CL",
        )
        assert _paper_is_obviously_unrelated(p) is False

    def test_patchgen_skips_music_paper_without_calling_llm(self, monkeypatch):
        """End-to-end: if the best paper is a music paper, patchgen
        returns None without ever calling the LLM (saves a 120s budget)."""
        from src import patchgen
        music = self._make(
            title="LeVo 2: Stable and Melodious Song Generation",
            abstract="song generation",
            categories="cs.SD",
        )
        called = {"n": 0}
        def must_not_call(*args, **kwargs):
            called["n"] += 1
            return LLMResponse(content="", model="x")
        monkeypatch.setattr(patchgen, "chat", must_not_call)
        cfg = LLMConfig(api_keys=["k"], base_url="http://x", model="m", fallback_models=[])

        result = patchgen.generate_patch(music, "planner.py", llm_config=cfg)
        assert result is None
        assert called["n"] == 0, "LLM must not be called for unrelated papers"
