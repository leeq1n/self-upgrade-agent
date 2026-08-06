"""Test configuration.

Responsibilities:
  1. Make the project root importable.
  2. Load .env into os.environ so the LLM code path can discover keys
     during tests (matches the behavior of run.py).
  3. Register custom markers.
  4. Auto-skip @pytest.mark.llm tests when no LLM_API_KEY_* is configured,
     and auto-skip @pytest.mark.network tests when network is disabled
     (env var ``SUA_SKIP_NETWORK=1``).
  5. Auto-skip @pytest.mark.slow tests when ``SUA_FAST=1``.
  6. Pin tests to a CHEAP model (Qwen3.5-2B) with a short total_timeout
     so a stuck LLM call fails fast (< 30s) instead of hanging the suite.
"""
import os
import sys

# 1) project root on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _load_env_file(path: str) -> None:
    """Load KEY=VALUE pairs from a .env file.  Strips inline comments.

    We do a single pass on each line:
      - skip blank lines and lines starting with '#'
      - split on the first '='
      - strip whitespace and surrounding quotes from value
      - drop any inline comment after the value (anything after '#')
    """
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                # Strip inline comments (" 30 # comment" → "30").
                if " #" in v:
                    v = v.split(" #", 1)[0].rstrip()
                v = v.strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


# 2) .env auto-load (mirrors run.py)
_load_env_file(os.path.join(os.path.dirname(__file__), "..", ".env"))

# 6) Test-mode LLM defaults: model + short total_timeout so a
# misconfigured test environment fails the suite in <30s with a clear
# diagnostic, not 180s of mysterious hanging.
# These only apply if the user hasn't already set them.  Pinned to a
# model that actually exists on ModelScope (Qwen3-235B); the "cheap
# 2B" tier that was here earlier is not actually served.
os.environ.setdefault("LLM_MODEL", "deepseek-ai/DeepSeek-V4-Pro")
os.environ.setdefault("LLM_TIMEOUT", "30")  # per-request (v1.6.0: large prompts need >15s)
os.environ.setdefault("LLM_TOTAL_TIMEOUT", "180")  # whole-call budget


def _has_llm_keys() -> bool:
    """Return True iff at least one usable LLM key is in the environment."""
    for i in range(64):
        if os.environ.get(f"LLM_API_KEY_{i}", "").strip():
            return True
    return bool(
        os.environ.get("LLM_API_KEY", "").strip()
        or os.environ.get("MODELSCOPE_API_KEY", "").strip()
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "llm: tests that require LLM API (auto-skip if no key)")
    config.addinivalue_line("markers", "network: tests that require network access (auto-skip with SUA_SKIP_NETWORK=1)")
    config.addinivalue_line("markers", "slow: tests > 5s (auto-skip with SUA_FAST=1)")


def pytest_collection_modifyitems(config, items):
    """Auto-skip llm/network/slow markers when their prereqs are missing.

    Skipping is opt-out: a developer can force a skipped test to run with
    ``--runllm`` / ``--runnetwork`` / ``--runslow`` flags, or by exporting
    ``SUA_FORCE_LLM=1``.  This avoids the silent "test hung for 180s"
    problem we hit when LLM markers were registered but never honored.
    """
    skip_llm = not _has_llm_keys() and not (
        os.environ.get("SUA_FORCE_LLM") or os.environ.get("HERMES_FORCE_LLM")
    )
    skip_network = bool(
        os.environ.get("SUA_SKIP_NETWORK") or os.environ.get("HERMES_SKIP_NETWORK")
    )
    skip_slow = bool(
        os.environ.get("SUA_FAST") or os.environ.get("HERMES_FAST")
    )

    force_llm = bool(getattr(config.option, "runllm", False))
    force_network = bool(getattr(config.option, "runnetwork", False))
    force_slow = bool(getattr(config.option, "runslow", False))

    skip_llm = skip_llm and not force_llm
    skip_network = skip_network and not force_network
    skip_slow = skip_slow and not force_slow

    for item in items:
        markers = {m.name for m in item.iter_markers()}
        if "llm" in markers and skip_llm:
            item.add_marker(pytest.mark.skip(reason="no LLM_API_KEY_* in env (use SUA_FORCE_LLM=1 to override)"))
        if "network" in markers and skip_network:
            item.add_marker(pytest.mark.skip(reason="SUA_SKIP_NETWORK=1"))
        if "slow" in markers and skip_slow:
            item.add_marker(pytest.mark.skip(reason="SUA_FAST=1"))


# Late import so the module is set up before pytest.* is referenced.
import pytest  # noqa: E402
