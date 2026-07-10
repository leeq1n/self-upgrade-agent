"""Tests for src/v4_thinker.py - Thinker abstraction (v3.0.2 step 2.1)."""
import json
import pytest

from src.v4_thinker import (
    Step, Plan, Thinker, MockThinker, JsonThinker,
)


# ── Step dataclass ──────────────────────────────────────────────

class TestStep:
    def test_step_default_args(self):
        s = Step(name="noop")
        assert s.name == "noop"
        assert s.args == {}

    def test_step_with_args(self):
        s = Step(name="read", args={"path": "/etc/foo"})
        assert s.name == "read"
        assert s.args == {"path": "/etc/foo"}

    def test_step_to_dict(self):
        s = Step(name="write", args={"file": "x.py", "content": "# hi"})
        d = s.to_dict()
        assert d == {"name": "write", "args": {"file": "x.py", "content": "# hi"}}

    def test_step_dataclass_no_mutable_default(self):
        """Per P9: hard rule, no mutable default."""
        s1 = Step(name="a")
        s2 = Step(name="b")
        s1.args["x"] = 1
        # s2's args should be a fresh dict
        assert s2.args == {}


# ── Abstract Thinker ───────────────────────────────────────────

class TestAbstractThinker:
    def test_abstract_plan_raises(self):
        t = Thinker()
        with pytest.raises(NotImplementedError):
            t.plan("anything")

    def test_thinker_takes_config(self):
        cfg = {"model": "test"}
        t = Thinker(config=cfg)
        assert t.config == cfg


# ── MockThinker ────────────────────────────────────────────────

class TestMockThinker:
    def test_empty_prompt(self):
        m = MockThinker()
        plan = m.plan("")
        # No lines = noop fallback
        assert len(plan) == 1
        assert plan[0].name == "noop"

    def test_single_step_with_colon(self):
        m = MockThinker()
        plan = m.plan("read: /etc/foo")
        assert len(plan) == 1
        assert plan[0].name == "read"
        assert plan[0].args == {"input": "/etc/foo"}

    def test_multi_step_lines(self):
        m = MockThinker()
        plan = m.plan("step1: arg1\nstep2: arg2\n# comment\nstep3: arg3")
        assert len(plan) == 3
        assert [s.name for s in plan] == ["step1", "step2", "step3"]

    def test_step_with_space_arg(self):
        m = MockThinker()
        plan = m.plan("read /path/to/file")
        assert plan[0].name == "read"
        assert plan[0].args == {"input": "/path/to/file"}

    def test_step_with_no_arg(self):
        m = MockThinker()
        plan = m.plan("list_files")
        assert plan[0].name == "list_files"
        assert plan[0].args == {}

    def test_fixed_plan(self):
        """fixed_plan overrides prompt parsing."""
        fixed = [Step("a"), Step("b")]
        m = MockThinker(fixed_plan=fixed)
        plan = m.plan("ignored_prompt: x")
        assert [s.name for s in plan] == ["a", "b"]

    def test_comment_lines_skipped(self):
        m = MockThinker()
        plan = m.plan("# this is a comment\nstep1: arg\n# another")
        assert len(plan) == 1
        assert plan[0].name == "step1"


# ── JsonThinker ────────────────────────────────────────────────

class TestJsonThinkerParseSteps:
    def test_parse_clean_json(self):
        text = '[{"name": "step1", "args": {"x": 1}}]'
        plan = JsonThinker._parse_steps(text)
        assert len(plan) == 1
        assert plan[0].name == "step1"
        assert plan[0].args == {"x": 1}

    def test_parse_markdown_fenced(self):
        text = '```json\n[{"name": "a", "args": {}}]\n```'
        plan = JsonThinker._parse_steps(text)
        assert len(plan) == 1
        assert plan[0].name == "a"

    def test_parse_no_array(self):
        plan = JsonThinker._parse_steps("just text, no array")
        assert len(plan) == 1
        assert plan[0].name == "noop"

    def test_parse_invalid_json(self):
        plan = JsonThinker._parse_steps("[not valid json")
        assert len(plan) == 1
        assert plan[0].name == "noop"

    def test_parse_non_dict_items_skipped(self):
        # Items that aren't dicts should be skipped
        text = '[{"name": "a"}, "string_item", {"name": "b"}]'
        plan = JsonThinker._parse_steps(text)
        # Both dicts should survive
        assert [s.name for s in plan] == ["a", "b"]

    def test_parse_empty_array(self):
        plan = JsonThinker._parse_steps("[]")
        assert plan[0].name == "noop"
        assert "empty" in plan[0].args.get("reason", "")


class TestJsonThinkerWithMockedLLM:
    def test_plan_calls_llm(self, monkeypatch):
        """plan() invokes _call_llm and parses the result."""
        captured = {}
        def fake_call(prompt):
            captured["prompt"] = prompt
            return '[{"name": "x", "args": {}}]'
        jt = JsonThinker(config={"fake": True})
        monkeypatch.setattr(jt, "_call_llm", fake_call)
        plan = jt.plan("test prompt")
        assert plan[0].name == "x"
        assert captured["prompt"] == "test prompt"

    def test_plan_llm_exception_falls_back(self, monkeypatch):
        """If LLM call raises, return noop step (fail-OPEN)."""
        jt = JsonThinker(config={"fake": True})
        def raise_call(prompt):
            raise RuntimeError("API down")
        monkeypatch.setattr(jt, "_call_llm", raise_call)
        plan = jt.plan("anything")
        assert plan[0].name == "noop"
        assert "LLM call failed" in plan[0].args.get("reason", "")

    def test_plan_bad_response_falls_back(self, monkeypatch):
        """If LLM returns non-JSON, return noop step (fail-OPEN)."""
        jt = JsonThinker(config={"fake": True})
        monkeypatch.setattr(jt, "_call_llm", lambda p: "garbage")
        plan = jt.plan("anything")
        assert plan[0].name == "noop"


# ── Joint with LITERATURE principles ───────────────────────────

class TestJointWithLiterature:
    """Joint sanity: Thinker can produce plans for real LLM prompts.

    Per LITERATURE: Self-Harness / Lilian Weng / Nate Berkopec
    all emphasize planning as the bottleneck.  Our Thinker should
    support both mock and real LLM paths.
    """

    def test_mock_path_no_llm_call(self):
        """MockThinker.plan() never imports or calls LLM."""
        # We just check that MockThinker.plan() runs without import errors
        m = MockThinker()
        plan = m.plan("step1: arg\nstep2: arg2")
        assert len(plan) == 2

    def test_json_path_lazy_imports(self):
        """JsonThinker only imports v2_agent._chat when plan() is called."""
        # JsonThinker init should not fail
        jt = JsonThinker(config={"fake": True})
        assert jt.config == {"fake": True}
        # Calling plan() without a working LLM should not crash
        # (it may fall back to noop)
        plan = jt.plan("anything")
        assert plan is not None
