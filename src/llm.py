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


_FALLBACK_MODELS = [
    "deepseek-ai/DeepSeek-V3.2",
    "Qwen/Qwen3-Coder-30B-A3B-Instruct",  
    "Qwen/Qwen3-235B-A22B",
    "moonshotai/Kimi-K2.5",
    "ZhipuAI/GLM-5.1",
    "mistralai/Mistral-Large-Instruct-2407",
]

def _get_key_pool(config):
    """Build list of (model, key) pairs to try, rotating models and keys."""
    models = [config.model] + [m for m in _FALLBACK_MODELS if m != config.model]
    keys = [config.api_key]
    # Load additional keys from env
    import os
    count = int(os.environ.get("LLM_API_KEY_COUNT", "0"))
    for i in range(count):
        k = os.environ.get(f"LLM_API_KEY_{i}", "")
        if k and k not in keys:
            keys.append(k)
    # Build matrix: try each key with each model
    pairs = []
    for k in keys:
        for m in models:
            pairs.append((m, k))
    return pairs

def _try_with_fallback(messages, system, config, response_format) -> LLMResponse:
    """Try model×key combinations on quota errors."""
    import httpx, time, os
    pairs = _get_key_pool(config)
    full_messages = []
    if system: full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)
    body_template = {"messages": full_messages, "max_tokens": config.max_tokens, "temperature": config.temperature}
    if response_format: body_template["response_format"] = response_format
    
    for model, key in pairs:
        try:
            start = time.time()
            body = dict(body_template, model=model)
            
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
            resp = httpx.post(f"{config.base_url}/chat/completions", proxy=None,
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json=body, timeout=config.timeout)
            elapsed = int((time.time() - start) * 1000)
            if resp.status_code == 429:
                short_key = key[:10] + "..." + key[-4:]
                logger.warning(f"429: {short_key} + {model}, trying next combo")
                continue
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices")
            if choices and len(choices) > 0:
                return LLMResponse(content=choices[0].get("message",{}).get("content",""),
                    model=data.get("model",model),
                    total_tokens=data.get("usage",{}).get("total_tokens",0),
                    latency_ms=elapsed)
        except Exception as e:
            logger.warning(f"Fail: {key[:10]}... + {model}: {str(e)[:50]}")
            continue
    return LLMResponse(content="", error="All API keys + models exhausted")

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
    """Convenience: send a simple prompt, get content string back.

    Args:
        prompt: The user message.
        system: Optional system prompt.
        **kwargs: Passed to chat() — config, response_format, etc.

    Returns:
        Content string, or empty string on error.
    """
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
