"""Unified LLM call layer.

[FROZEN v1.1.0] — stable API (chat/chat_simple/LLMConfig), tested, do not modify.

All LLM calls in the system go through this module.
Supports any OpenAI-compatible API (ModelScope, OpenRouter, etc.)

Configure via environment variables:
  LLM_API_KEY      — API key
  LLM_BASE_URL     — API base URL
  LLM_MODEL        — Model name
  LLM_MAX_TOKENS   — Max tokens per response (default: 2048)
  LLM_TEMPERATURE  — Temperature (default: 0.1)
"""
import os
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM calls. Falls back to env vars."""
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    max_tokens: int = 2048
    temperature: float = 0.1
    timeout: int = 120
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            api_key=os.environ.get("LLM_API_KEY", os.environ.get("MODELSCOPE_API_KEY", "")),
            base_url=os.environ.get("LLM_BASE_URL", "https://api-inference.modelscope.cn/v1"),
            model=os.environ.get("LLM_MODEL", "Qwen/Qwen3.5-35B-A3B"),
            max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "2048")),
            temperature=float(os.environ.get("LLM_TEMPERATURE", "0.1")),
            timeout=int(os.environ.get("LLM_TIMEOUT", "60")),
            max_retries=int(os.environ.get("LLM_MAX_RETRIES", "3")),
        )

    @property
    def ready(self) -> bool:
        """Check if config has enough info to make a call."""
        return bool(self.api_key) and bool(self.model)


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    content: str
    model: str = ""
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    error: str = ""


# Module-level cached config
_config: Optional[LLMConfig] = None


def configure(config: LLMConfig):
    """Set global LLM configuration."""
    global _config
    _config = config


def get_config() -> LLMConfig:
    """Get current config (initialize from env if not set)."""
    global _config
    if _config is None:
        _config = LLMConfig.from_env()
    return _config


# Fallback models to try only when primary model returns 404 (not found)
_FALLBACK_MODELS = [
    "deepseek-ai/DeepSeek-V3.2",
    "Qwen/Qwen3-Coder-30B-A3B-Instruct",
    "Qwen/Qwen3-235B-A22B",
    "moonshotai/Kimi-K2.5",
    "ZhipuAI/GLM-5.1",
    "mistralai/Mistral-Large-Instruct-2407",
]


def _try_with_fallback(messages, system, config, response_format) -> LLMResponse:
    """Try primary model first, retry on 429, fallback only on 404."""
    import httpx, time, warnings

    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    body_template = {
        "messages": full_messages,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
    }
    if response_format:
        body_template["response_format"] = response_format

    # Only try fallback models if primary returns 404 (model not found)
    fallback_models = [m for m in _FALLBACK_MODELS if m != config.model]
    models_to_try = [config.model] + fallback_models

    for model in models_to_try:
        body = dict(body_template, model=model)
        # Retry 429 up to 3 times with backoff on the same model
        for attempt in range(4):
            try:
                start = time.time()
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                resp = httpx.post(
                    f"{config.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {config.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                    timeout=config.timeout,
                )
                elapsed = int((time.time() - start) * 1000)

                if resp.status_code == 429:
                    if attempt < 3:
                        wait = 2 ** attempt
                        logger.warning(
                            f"429 on {model}, retry {attempt + 1}/3 in {wait}s"
                        )
                        time.sleep(wait)
                        continue
                    logger.warning(f"429 exhausted on {model}, trying next model")
                    break

                if resp.status_code == 404:
                    logger.warning(f"404: model {model} not found, trying next")
                    break

                resp.raise_for_status()
                data = resp.json()
                choices = data.get("choices")
                if choices and len(choices) > 0:
                    return LLMResponse(
                        content=choices[0].get("message", {}).get("content", ""),
                        model=data.get("model", model),
                        total_tokens=data.get("usage", {}).get("total_tokens", 0),
                        latency_ms=elapsed,
                    )
            except httpx.HTTPError as e:
                logger.warning(f"HTTP error: {model}: {e}")
                break
            except Exception as e:
                if attempt < 3:
                    time.sleep(1)
                    continue
                logger.warning(f"Fail: {model}: {str(e)[:50]}")
                break

    return LLMResponse(content="", error="All models exhausted")


def chat(
    messages: List[Dict[str, str]],
    system: Optional[str] = None,
    config: Optional[LLMConfig] = None,
    response_format: Optional[Dict] = None,
) -> LLMResponse:
    if config is None:
        config = get_config()
    if not config.ready:
        return LLMResponse(content="", error="LLM not configured")
    return _try_with_fallback(messages, system, config, response_format)


def chat_simple(
    prompt: str,
    system: Optional[str] = None,
    **kwargs,
) -> str:
    """Convenience: send a simple prompt, get content string back."""
    result = chat(
        messages=[{"role": "user", "content": prompt}],
        system=system,
        **kwargs,
    )
    if result.error:
        logger.error(f"LLM call failed: {result.error}")
    return result.content


def estimate_tokens(text: str) -> int:
    """Rough token estimate (4 chars per token)."""
    return len(text) // 4
