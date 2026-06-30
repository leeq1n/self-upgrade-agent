"""Tests for src/llm.py"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.llm import LLMConfig, LLMResponse, get_config, configure, chat, chat_simple, estimate_tokens


class TestLLMConfig:
    def test_from_env_uses_defaults_when_no_env(self):
        """When env vars are not set, from_env should use defaults."""
        # Save and clear relevant env vars
        saved = {}
        for key in ["LLM_API_KEY", "LLM_BASE_URL", "LLM_MODEL", "LLM_MAX_TOKENS",
                     "LLM_TEMPERATURE", "LLM_TIMEOUT", "LLM_MAX_RETRIES",
                     "MODELSCOPE_API_KEY", "SELFUPGRADE_DRY_RUN"]:
            saved[key] = os.environ.pop(key, None)

        config = LLMConfig.from_env()
        assert config.base_url == "https://api-inference.modelscope.cn/v1"
        assert config.model == "Qwen/Qwen3.5-35B-A3B"
        assert config.max_tokens == 2048
        assert config.temperature == 0.1
        assert config.max_retries == 3

        # Restore
        for key, val in saved.items():
            if val is not None:
                os.environ[key] = val

    def test_from_env_reads_env_vars(self):
        os.environ["LLM_API_KEY"] = "test-key-123"
        os.environ["LLM_MODEL"] = "test-model"
        os.environ["LLM_TEMPERATURE"] = "0.7"

        config = LLMConfig.from_env()
        assert config.api_key == "test-key-123"
        assert config.model == "test-model"
        assert config.temperature == 0.7

        # Clean up
        del os.environ["LLM_API_KEY"]
        del os.environ["LLM_MODEL"]
        del os.environ["LLM_TEMPERATURE"]


class TestLLMResponse:
    def test_dataclass_defaults(self):
        resp = LLMResponse(content="Hello")
        assert resp.content == "Hello"
        assert resp.total_tokens == 0
        assert resp.latency_ms == 0
        assert resp.error == ""


class TestEstimateTokens:
    def test_empty(self):
        assert estimate_tokens("") == 0

    def test_rough_estimate(self):
        assert estimate_tokens("hello world") == 2  # 11 chars // 4 = 2


class TestChatBehavior:
    """Test chat behavior without real API calls (requires mock)."""

    def test_chat_returns_error_when_no_key(self):
        """Without an API key, chat should return an error response."""
        saved = os.environ.pop("LLM_API_KEY", None)
        saved2 = os.environ.pop("MODELSCOPE_API_KEY", None)

        # Reset config to read env again
        import src.llm
        src.llm._config = None

        config = LLMConfig(api_key="")  # Explicitly empty
        result = chat(
            messages=[{"role": "user", "content": "hi"}],
            config=config,
        )
        assert result.error != ""
        assert "not configured" in result.error

        # Restore
        if saved:
            os.environ["LLM_API_KEY"] = saved
        if saved2:
            os.environ["MODELSCOPE_API_KEY"] = saved2


class TestChatSimple:
    def test_returns_empty_on_error(self):
        """chat_simple should return empty string on error, not crash."""
        config = LLMConfig(api_key="bad-key-123")
        result = chat_simple("hi", config=config)
        assert result == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
