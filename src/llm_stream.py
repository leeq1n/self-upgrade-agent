"""v1.8.1: streaming LLM chat wrapper for local qwen3.6-27B.

The local model takes 6-30+ seconds per call.  Without streaming,
the user sees nothing until the call returns.  With streaming,
the user sees tokens as they arrive (much better UX for long
calls and helps debug hangs).

This module exposes `chat_stream(messages, ...)` which yields
text chunks as they arrive.  It does NOT replace the existing
`chat()` function — that's still used by the pipeline for
non-interactive work.  This is a NEW path for users who want
visibility into slow LLM calls.

Usage:
  from src.llm_stream import chat_stream
  for chunk in chat_stream(messages, prompt="..."):
      print(chunk, end="", flush=True)
"""
import os
import sys
import time
import httpx
from typing import Iterator, Optional, List, Dict

# Reuse LLMConfig from src.llm
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_config():
    """Load .env and return LLMConfig (mirrors src/llm.LLMConfig.from_env)."""
    # Read .env from project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if " #" in v:
                    v = v.split(" #", 1)[0].rstrip()
                v = v.strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v

    from src.llm import LLMConfig
    return LLMConfig.from_env()


def _is_anthropic(base_url: str) -> bool:
    return "/anthropic" in (base_url or "")


def chat_stream(
    messages: List[Dict[str, str]],
    system: Optional[str] = None,
    config=None,
    timeout: int = 600,
) -> Iterator[str]:
    """Stream tokens from a chat completion.  Yields text chunks.

    Args:
        messages: chat messages
        system: optional system message
        config: LLMConfig (default: from env)
        timeout: per-request timeout in seconds (default 10min)

    Yields:
        text chunks as they arrive from the server

    Notes:
        - For OpenAI-format endpoints (incl. local qwen3.6):
          uses stream=True, parses SSE chunks.
        - For Anthropic-format endpoints:
          uses stream=True with anthropic-specific event format.
    """
    if config is None:
        config = _load_config()

    full_messages: List[Dict[str, str]] = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    body = {
        "model": config.model,
        "messages": full_messages,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
        "stream": True,
    }

    is_anthropic = _is_anthropic(config.base_url)
    key = config.api_keys[0] if config.api_keys else "no-key"

    if is_anthropic:
        # Anthropic streaming: separate system field
        ant_messages = [m for m in full_messages if m.get("role") != "system"]
        ant_body = {**body, "messages": ant_messages}
        if system:
            ant_body["system"] = system
        url = f"{config.base_url.rstrip('/')}/v1/messages"
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        event_type = None
        with httpx.stream(
            "POST", url, headers=headers, json=ant_body, timeout=timeout
        ) as resp:
            for line in resp.iter_lines():
                if not line:
                    continue
                if line.startswith("event: "):
                    event_type = line[7:].strip()
                    continue
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        import json
                        d = json.loads(data)
                        if event_type == "content_block_delta":
                            delta = d.get("delta", {})
                            text = delta.get("text", "")
                            if text:
                                yield text
                    except Exception:
                        pass
    else:
        # OpenAI streaming (incl. local vLLM)
        url = f"{config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
        with httpx.stream(
            "POST", url, headers=headers, json=body, timeout=timeout
        ) as resp:
            for line in resp.iter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        import json
                        d = json.loads(data)
                        choices = d.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            text = delta.get("content", "")
                            if text:
                                yield text
                    except Exception:
                        pass


def main():
    """Quick smoke test: stream a simple question to verify endpoint works."""
    config = _load_config()
    print(f"Provider: {config.base_url}", file=sys.stderr)
    print(f"Model: {config.model}", file=sys.stderr)
    print(f"Is anthropic: {_is_anthropic(config.base_url)}", file=sys.stderr)
    print(f"--- streaming response ---", file=sys.stderr)

    t0 = time.time()
    chunks = []
    try:
        for chunk in chat_stream(
            messages=[{"role": "user", "content": "Reply with just the number 42. No other text."}],
            config=config,
            timeout=120,
        ):
            chunks.append(chunk)
            print(chunk, end="", flush=True)
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1
    print(f"\n--- done in {time.time()-t0:.1f}s ({len(chunks)} chunks) ---", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
