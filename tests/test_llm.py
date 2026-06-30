"""Tests for src/llm.py — covers multi-key rotation, quota state, and
the public chat/chat_simple API without making real network calls.
"""
import os
import sys
import json
import pytest
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.llm import (
    LLMConfig,
    LLMResponse,
    QuotaState,
    _is_daily_quota_error,
    _try_with_fallback,
    get_config,
    configure,
    chat,
    chat_simple,
    estimate_tokens,
    quota_snapshot,
)


# Save original env so we can restore after each test.
_ORIG_ENV = dict(os.environ)


@pytest.fixture(autouse=True)
def restore_env():
    """Snapshot and restore env around every test.

    Also clears all LLM key env vars at the start so conftest's .env
    auto-load doesn't leak real ModelScope keys into the test.
    """
    saved = dict(os.environ)
    # Clear all key env vars up front — tests that need them set them
    # explicitly.  This isolates the suite from the user's .env.
    for i in range(64):
        os.environ.pop(f"LLM_API_KEY_{i}", None)
    os.environ.pop("LLM_API_KEY", None)
    os.environ.pop("MODELSCOPE_API_KEY", None)
    yield
    # Remove anything we added, restore originals.
    for k in list(os.environ.keys()):
        if k not in saved:
            os.environ.pop(k, None)
    for k, v in saved.items():
        os.environ[k] = v


# ═══════════════════════════════════════════════════════════
# LLMConfig — multi-key discovery
# ═══════════════════════════════════════════════════════════

class TestLLMConfig:
    def test_from_env_discovers_indexed_keys(self):
        # Wipe ALL key env vars first to make this test isolated.
        for i in range(64):
            os.environ.pop(f"LLM_API_KEY_{i}", None)
        os.environ.pop("LLM_API_KEY", None)
        os.environ.pop("MODELSCOPE_API_KEY", None)

        os.environ["LLM_API_KEY_0"] = "key-0"
        os.environ["LLM_API_KEY_1"] = "key-1"
        os.environ["LLM_API_KEY_2"] = "key-2"
        # Single key fallback should be ignored when _0..N are present.
        os.environ["LLM_API_KEY"] = "single-fallback"

        cfg = LLMConfig.from_env()
        assert cfg.api_keys == ["key-0", "key-1", "key-2"]
        # Backward-compat property
        assert cfg.api_key == "key-0"

    def test_from_env_falls_back_to_single_key(self):
        for i in range(64):
            os.environ.pop(f"LLM_API_KEY_{i}", None)
        os.environ["LLM_API_KEY"] = "solo-key"

        cfg = LLMConfig.from_env()
        assert cfg.api_keys == ["solo-key"]

    def test_from_env_falls_back_to_modelscope(self):
        for i in range(64):
            os.environ.pop(f"LLM_API_KEY_{i}", None)
        os.environ.pop("LLM_API_KEY", None)
        os.environ["MODELSCOPE_API_KEY"] = "ms-fallback"

        cfg = LLMConfig.from_env()
        assert cfg.api_keys == ["ms-fallback"]

    def test_from_env_empty_when_no_keys(self):
        for i in range(64):
            os.environ.pop(f"LLM_API_KEY_{i}", None)
        os.environ.pop("LLM_API_KEY", None)
        os.environ.pop("MODELSCOPE_API_KEY", None)

        cfg = LLMConfig.from_env()
        assert cfg.api_keys == []
        assert not cfg.ready

    def test_from_env_respects_overrides(self):
        os.environ["LLM_API_KEY_0"] = "k"
        os.environ["LLM_BASE_URL"] = "https://example.com/v1"
        os.environ["LLM_MODEL"] = "test/model"
        os.environ["LLM_MAX_TOKENS"] = "999"
        os.environ["LLM_TEMPERATURE"] = "0.7"

        cfg = LLMConfig.from_env()
        assert cfg.base_url == "https://example.com/v1"
        assert cfg.model == "test/model"
        assert cfg.max_tokens == 999
        assert abs(cfg.temperature - 0.7) < 1e-6

    def test_for_task_type_routes_models(self):
        os.environ["LLM_API_KEY_0"] = "k"
        for tt, expected in [
            ("code", "Qwen/Qwen3-Coder-30B-A3B-Instruct"),
            ("reasoning", "deepseek-ai/DeepSeek-V3.2"),
            ("planning", "Qwen/Qwen3-235B-A22B"),
            ("general", "Qwen/Qwen3-Coder-30B-A3B-Instruct"),
        ]:
            cfg = LLMConfig.for_task_type(tt)
            assert cfg.model == expected, f"task {tt}: {cfg.model}"
            assert len(cfg.fallback_models) >= 1, f"task {tt}: no fallbacks"

    def test_for_task_type_env_override(self):
        os.environ["LLM_API_KEY_0"] = "k"
        os.environ["LLM_MODEL_FOR_CODE"] = "custom/code-model"

        cfg = LLMConfig.for_task_type("code")
        assert cfg.model == "custom/code-model"


# ═══════════════════════════════════════════════════════════
# QuotaState
# ═══════════════════════════════════════════════════════════

class TestQuotaState:
    def test_mark_dead_and_is_dead(self, tmp_path):
        path = str(tmp_path / "quota.json")
        qs = QuotaState(path)
        key = "ms-test-key"

        assert not qs.is_dead(key)
        qs.mark_dead(key, cooldown_seconds=3600)
        assert qs.is_dead(key)

    def test_is_dead_expires(self, tmp_path, monkeypatch):
        path = str(tmp_path / "quota.json")
        # Patch time.time BEFORE mark_dead so the saved dead_until
        # is computed from a known baseline.
        import src.llm
        base_time = 1_000_000.0
        monkeypatch.setattr(src.llm.time, "time", lambda: base_time)

        qs1 = QuotaState(path)
        key = "ms-test-key"
        qs1.mark_dead(key, cooldown_seconds=60)
        assert qs1.is_dead(key)

        # Now jump time forward past the cooldown and re-instantiate.
        monkeypatch.setattr(src.llm.time, "time", lambda: base_time + 120)
        qs2 = QuotaState(path)
        assert not qs2.is_dead(key)

    def test_persistence_across_instances(self, tmp_path):
        path = str(tmp_path / "quota.json")
        key = "ms-persist-key"

        qs1 = QuotaState(path)
        qs1.mark_dead(key, cooldown_seconds=3600)
        del qs1

        # Brand new instance should see the persisted dead state.
        qs2 = QuotaState(path)
        assert qs2.is_dead(key)

    def test_record_failure(self, tmp_path):
        path = str(tmp_path / "quota.json")
        qs = QuotaState(path)
        key = "ms-fail-key"

        qs.record_failure(key, 429)
        snap = qs.snapshot()
        assert key in snap
        assert snap[key]["last_status"] == 429
        assert snap[key]["failures_today"] == 1


# ═══════════════════════════════════════════════════════════
# Daily-quota detection
# ═══════════════════════════════════════════════════════════

class _StubResp:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text


class TestDailyQuotaDetection:
    def test_429_with_quota_keyword(self):
        resp = _StubResp(429, '{"message": "You exceeded your current quota"}')
        assert _is_daily_quota_error(resp) is True

    def test_429_with_daily_keyword(self):
        resp = _StubResp(429, "Daily limit reached, please try again tomorrow")
        assert _is_daily_quota_error(resp) is True

    def test_429_with_rate_limit_only(self):
        # "rate" is NOT in daily_markers, so this should be False.
        # Use a body with no quota/daily/exceeded/limit-reached hints.
        resp = _StubResp(429, "Please retry after 30 seconds")
        assert _is_daily_quota_error(resp) is False

    def test_429_opaque_body(self):
        resp = _StubResp(429, "")
        assert _is_daily_quota_error(resp) is False

    def test_non_429(self):
        resp = _StubResp(500, "quota")
        assert _is_daily_quota_error(resp) is False


# ═══════════════════════════════════════════════════════════
# Public chat/chat_simple — error paths
# ═══════════════════════════════════════════════════════════

class TestChatBehavior:
    def test_chat_returns_error_when_no_key(self):
        for i in range(64):
            os.environ.pop(f"LLM_API_KEY_{i}", None)
        os.environ.pop("LLM_API_KEY", None)
        os.environ.pop("MODELSCOPE_API_KEY", None)

        cfg = LLMConfig(api_keys=[])  # empty
        result = chat(messages=[{"role": "user", "content": "hi"}], config=cfg)
        assert result.error != ""
        assert "not configured" in result.error

    def test_chat_simple_returns_empty_on_no_key(self):
        cfg = LLMConfig(api_keys=[])
        result = chat_simple("hi", config=cfg)
        assert result == ""


# ═══════════════════════════════════════════════════════════
# LLMResponse & estimate_tokens
# ═══════════════════════════════════════════════════════════

class TestLLMResponse:
    def test_dataclass_defaults(self):
        resp = LLMResponse(content="Hello")
        assert resp.content == "Hello"
        assert resp.total_tokens == 0
        assert resp.latency_ms == 0
        assert resp.error == ""
        assert resp.attempts == 0
        assert resp.key_index == -1


class TestEstimateTokens:
    def test_empty(self):
        assert estimate_tokens("") == 0

    def test_rough_estimate(self):
        assert estimate_tokens("hello world") == 2  # 11 chars // 4 = 2
