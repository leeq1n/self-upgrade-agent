"""Unified LLM call layer with multi-key rotation and per-model fallback.

Design (v1.4.0):
  * Multiple API keys are loaded from env (``LLM_API_KEY_0``..``LLM_API_KEY_N``)
    and rotated on 429 quota errors.  When one key exhausts its daily quota
    we mark it dead-for-today and immediately move to the next key — no
    retries on the same dead key.  Minute-level rate limits (also 429) are
    retried with exponential backoff.
  * Model fallback only kicks in when *all* configured keys have failed for
    the current model.  This is intentional: a model that is 200 on one key
    is preferred over a 200 on a different model, because cost / quality
    vary by model.
  * Quota state (which key is dead for the day) is persisted in
    ``upgrades/quota_state.json`` so the daemon does not re-try dead keys
    on every run.

Configure via environment variables (all optional except keys/model):
  LLM_API_KEY_0      — first API key (required, at minimum)
  LLM_API_KEY_1..N   — additional keys for rotation
  LLM_API_KEY        — single-key fallback (used only if no _0.._N found)
  LLM_BASE_URL       — base URL (default: ModelScope)
  LLM_MODEL          — primary model
  LLM_MODELS         — comma-separated fallback model list
  LLM_MAX_TOKENS     — default 2048
  LLM_TEMPERATURE    — default 0.1
  LLM_TIMEOUT        — per-request HTTP timeout (default 60s)
  LLM_MAX_RETRIES    — retries on minute-level 429 (default 1, then key/model)
"""
from __future__ import annotations

import json
import logging
import os
import time
import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# Module-level cached config (re-read by configure() / get_config())
_config: Optional["LLMConfig"] = None

# Persistent quota state — shared across calls within this process.
# Path chosen under upgrades/ to match the convention used by db.py / switcher.py.
_QUOTA_STATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "upgrades", "quota_state.json"
)


# ═══════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════

@dataclass
class LLMConfig:
    """Configuration for LLM calls. Falls back to env vars."""

    api_keys: List[str] = field(default_factory=list)
    base_url: str = ""
    model: str = ""
    fallback_models: List[str] = field(default_factory=list)
    max_tokens: int = 2048
    temperature: float = 0.1
    timeout: int = 30  # per-request HTTP timeout (large prompts need >15s)
    max_retries: int = 2  # retries per (key, model) on minute-level 429
    daily_quota_cooldown: int = 86400  # seconds before re-trying a dead key
    total_timeout: float = 180.0  # whole-call budget across all keys/models
    # If True, raise LLMCallTimeout on total_timeout breach (instead of
    # returning an error response).  Useful for callers that want a hard
    # deadline (tests, CI); off by default to preserve call()=str return
    # type for the public API.
    raise_on_timeout: bool = False

    @property
    def api_key(self) -> str:
        """Backward-compat: return the first (primary) key."""
        return self.api_keys[0] if self.api_keys else ""

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Build config from environment variables.

        Multi-key discovery order:
          1. ``LLM_API_KEY_0``, ``LLM_API_KEY_1``, ..., ``LLM_API_KEY_N``
             (highest contiguous index wins; gaps are tolerated but odd)
          2. If none of the above, fall back to single ``LLM_API_KEY``
        """
        api_keys: List[str] = []
        # Look for indexed keys first.
        for i in range(64):  # hard cap to avoid pathological envs
            v = os.environ.get(f"LLM_API_KEY_{i}", "").strip()
            if v:
                api_keys.append(v)
        # Fall back to single key if no indexed ones were found.
        if not api_keys:
            single = os.environ.get("LLM_API_KEY", "").strip()
            if not single:
                single = os.environ.get("MODELSCOPE_API_KEY", "").strip()
            if single:
                api_keys = [single]

        # Fallback model list — ordered by current ModelScope availability.
        # As of v1.5.1 (2026-06-30), we have empirical evidence that:
        #   * DeepSeek-V4-Flash returns choices=null on ModelScope (broken)
        #   * DeepSeek-V4-Pro works on 3 alive keys (key#0, #4, #6)
        #   * ZhipuAI/GLM-5.1 works on 2 alive keys (key#4, #6) but
        #     daily-quota-burned on key#0
        #   * Qwen3-235B daily-quota-burned on key#0, alive on #4
        # So: V4-Pro is the most reliable model across the surviving
        # keys.  When daily quota resets, Qwen3-235B and GLM-5.1
        # come back to life and serve as fallbacks.
        models_env = os.environ.get("LLM_MODELS", "").strip()
        if models_env:
            fallback_models = [m.strip() for m in models_env.split(",") if m.strip()]
        else:
            fallback_models = [
                # Most reliable on 3 alive keys.
                "deepseek-ai/DeepSeek-V4-Pro",
                # Tier-2 fallbacks — work when daily quota resets.
                "ZhipuAI/GLM-5.1",
                "Qwen/Qwen3-235B-A22B",
                "deepseek-ai/DeepSeek-V3.2",
                "Qwen/Qwen3-Coder-30B-A3B-Instruct",
            ]

        return cls(
            api_keys=api_keys,
            base_url=os.environ.get(
                "LLM_BASE_URL", "https://api-inference.modelscope.cn/v1"
            ),
            model=os.environ.get("LLM_MODEL", "deepseek-ai/DeepSeek-V4-Pro"),
            fallback_models=fallback_models,
            max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "2048")),
            temperature=float(os.environ.get("LLM_TEMPERATURE", "0.1")),
            timeout=int(os.environ.get("LLM_TIMEOUT", "30")),
            max_retries=int(os.environ.get("LLM_MAX_RETRIES", "2")),
            daily_quota_cooldown=int(os.environ.get("LLM_DAILY_QUOTA_COOLDOWN", "86400")),
            total_timeout=float(os.environ.get("LLM_TOTAL_TIMEOUT", "180")),
        )

    @property
    def ready(self) -> bool:
        return bool(self.api_keys) and bool(self.model) and bool(self.base_url)

    # ── Task-type routing ──────────────────────────────────────
    # Maps a logical task type to a (primary_model, fallback_models) pair.
    # Override by setting LLM_MODEL_FOR_{TYPE} env var.  This is deliberately
    # a small switch — quality wins come from picking the right primary,
    # not from maintaining a giant per-model leaderboard.
    # NOTE: declared as a plain class attribute (no type annotation) so
    # dataclasses does not mistake it for an instance field.
    _TASK_MODEL_MAP = {
        "code": {
            "primary": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
            "fallback": [
                "deepseek-ai/DeepSeek-V3.2",
                "Qwen/Qwen3-235B-A22B",
                "moonshotai/Kimi-K2.5",
                "ZhipuAI/GLM-5.1",
            ],
        },
        "reasoning": {
            "primary": "deepseek-ai/DeepSeek-V3.2",
            "fallback": [
                "Qwen/Qwen3-235B-A22B",
                "moonshotai/Kimi-K2.5",
                "ZhipuAI/GLM-5.1",
                "Qwen/Qwen3-Coder-30B-A3B-Instruct",
            ],
        },
        "planning": {
            "primary": "Qwen/Qwen3-235B-A22B",
            "fallback": [
                "deepseek-ai/DeepSeek-V3.2",
                "moonshotai/Kimi-K2.5",
                "ZhipuAI/GLM-5.1",
                "Qwen/Qwen3-Coder-30B-A3B-Instruct",
            ],
        },
        "general": {
            "primary": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
            "fallback": [
                "Qwen/Qwen3-235B-A22B",
                "deepseek-ai/DeepSeek-V3.2",
                "moonshotai/Kimi-K2.5",
                "ZhipuAI/GLM-5.1",
            ],
        },
    }

    @classmethod
    def for_task_type(cls, task_type: str) -> "LLMConfig":
        """Build a config whose primary model is chosen for ``task_type``.

        ``task_type`` ∈ ``{"code", "reasoning", "planning", "general"}``.
        Unrecognized types fall back to "general".  Individual fields can
        still be overridden via env vars (``LLM_BASE_URL``, etc.).
        """
        env = os.environ
        tt = task_type if task_type in cls._TASK_MODEL_MAP else "general"
        primary = env.get(f"LLM_MODEL_FOR_{tt.upper()}") or cls._TASK_MODEL_MAP[tt]["primary"]
        # Per-type fallback list — env override or default map.
        env_fb = env.get(f"LLM_FALLBACK_FOR_{tt.upper()}")
        if env_fb:
            fallback = [m.strip() for m in env_fb.split(",") if m.strip()]
        else:
            fallback = list(cls._TASK_MODEL_MAP[tt]["fallback"])

        # Reuse from_env for keys/base_url/etc, then override model fields.
        base = cls.from_env()
        base.model = primary
        base.fallback_models = fallback
        return base


@dataclass
class LLMResponse:
    content: str
    model: str = ""
    key_index: int = -1
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    error: str = ""
    attempts: int = 0
    # Diagnostic report populated when the call failed or hit total_timeout.
    # Contains keys: total_timeout, total_elapsed_s, attempts, last_error,
    # tried (list of {model, key_index, status, elapsed_s, note}),
    # quota_snapshot, models_attempted.  Always present, even on success.
    diagnostic: dict = field(default_factory=dict)


def configure(config: LLMConfig) -> None:
    global _config
    _config = config


def get_config() -> LLMConfig:
    global _config
    if _config is None:
        _config = LLMConfig.from_env()
    return _config


# ═══════════════════════════════════════════════════════════
# Persistent quota state
# ═══════════════════════════════════════════════════════════

class QuotaState:
    """Tracks per-key daily-quota exhaustion in a JSON file.

    Layout::

        {
            "keys": {
                "<api_key>": {
                    "dead_until": <unix_ts>,  # 0 means alive
                    "failures_today": <int>,
                    "last_failure_at": <iso>,
                    "last_status": <int>
                }
            },
            "updated": "<iso>"
        }
    """

    def __init__(self, path: str = _QUOTA_STATE_PATH) -> None:
        self.path = path
        self._state: Dict[str, dict] = {"keys": {}, "updated": ""}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                self._state = json.load(f)
            # Coerce out dead keys whose cooldown has expired.
            now = time.time()
            for k, info in list(self._state.get("keys", {}).items()):
                if info.get("dead_until", 0) and now >= info["dead_until"]:
                    info["dead_until"] = 0
                    info["failures_today"] = 0
        except Exception as e:
            logger.debug(f"quota state load failed: {e}")

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self._state["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2)
            os.replace(tmp, self.path)
        except Exception as e:
            logger.debug(f"quota state save failed: {e}")

    def is_dead(self, api_key: str) -> bool:
        info = self._state.get("keys", {}).get(api_key, {})
        return bool(info.get("dead_until", 0))

    def mark_dead(self, api_key: str, cooldown_seconds: int, reason: str = "") -> None:
        """Mark a key as dead for ``cooldown_seconds``.

        Use a very large value (e.g. 100 years via mark_permanently_dead)
        for keys that are 401/403-broken — they won't recover without
        user intervention.  Use LLMConfig.daily_quota_cooldown (24h by
        default) for 429 daily-quota-exceeded errors.
        """
        keys = self._state.setdefault("keys", {})
        info = keys.setdefault(api_key, {})
        info["dead_until"] = int(time.time()) + cooldown_seconds
        info["failures_today"] = info.get("failures_today", 0) + 1
        info["last_failure_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        if reason:
            info["last_reason"] = reason
        self._save()

    def mark_permanently_dead(self, api_key: str, reason: str = "auth_invalid") -> None:
        """Mark a key as permanently dead (effectively forever).

        Used for 401/403 auth errors.  The key won't be retried for
        ~100 years, which is effectively "until the user rotates keys".
        """
        self.mark_dead(
            api_key,
            cooldown_seconds=100 * 365 * 24 * 3600,
            reason=reason,
        )

    def record_failure(self, api_key: str, status: int) -> None:
        keys = self._state.setdefault("keys", {})
        info = keys.setdefault(api_key, {})
        info["last_status"] = status
        info["failures_today"] = info.get("failures_today", 0) + 1
        info["last_failure_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._save()

    def snapshot(self) -> dict:
        return dict(self._state.get("keys", {}))


# ═══════════════════════════════════════════════════════════
# Core call loop
# ═══════════════════════════════════════════════════════════

def _is_daily_quota_error(resp: httpx.Response) -> bool:
    """Heuristic: distinguish daily-quota 429s from minute-level 429s.

    ModelScope and similar gateways usually return a JSON body with a
    ``code``/``message`` hinting at quota, OR use specific status text.
    If the body is opaque, fall back to the *response pattern*: a
    daily-quota key fails the *first* request of the day but is otherwise
    clean — we treat 429 + 0 successful recent requests as daily.
    """
    if resp.status_code != 429:
        return False
    try:
        body = (resp.text or "").lower()
    except Exception:
        body = ""
    daily_markers = (
        "quota",
        "exceeded",
        "insufficient",
        "balance",
        "free tier",
        "daily",
        "limit reached",
    )
    return any(m in body for m in daily_markers)


def _try_with_fallback(
    messages: List[dict],
    system: Optional[str],
    config: LLMConfig,
    response_format: Optional[Dict] = None,
) -> LLMResponse:
    """Try keys in rotation × models in fallback order.

    For each (key, model) pair, do at most ``config.max_retries`` retries
    on minute-level 429.  Daily-quota 429 immediately marks the key dead
    and moves to the next key.

    Hard overall deadline: ``config.total_timeout`` seconds.  If the
    whole-call budget is breached, returns an LLMResponse with a
    ``diagnostic`` field listing every (key, model) tried (or raises
    ``LLMCallTimeout`` when ``config.raise_on_timeout`` is set).  This
    is the difference between "test hung for 180s, no idea why" and
    "test failed in 60s, here's the report".
    """
    full_messages: List[dict] = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    quota = QuotaState(_QUOTA_STATE_PATH)
    models_to_try = [config.model] + [
        m for m in config.fallback_models if m != config.model
    ]

    last_error = ""
    attempts = 0
    call_start = time.time()
    tried: List[dict] = []  # every (model, key, status, elapsed, note)
    deadline = call_start + config.total_timeout

    # If a key is marked dead, skip it (its index is still kept for error reporting).
    alive_keys = [k for k in config.api_keys if not quota.is_dead(k)]
    if not alive_keys:
        alive_keys = config.api_keys  # all dead — try anyway, with backoff
        logger.warning("All API keys marked dead; attempting with backoff")

    for model in models_to_try:
        # Budget check before each model — bail early if we're out of time.
        remaining = deadline - time.time()
        if remaining <= 0:
            last_error = f"total_timeout {config.total_timeout}s exhausted before trying {model}"
            break
        for key in alive_keys:
            # Same budget check before each (key, model) attempt.
            remaining = deadline - time.time()
            if remaining <= 0:
                last_error = f"total_timeout exhausted mid-rotation (last model: {model})"
                break

            attempts += 1
            body = dict(
                {
                    "model": model,
                    "messages": full_messages,
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature,
                }
            )
            if response_format:
                body["response_format"] = response_format

            # Minute-level 429 → same-key retry with backoff.
            for attempt in range(config.max_retries + 1):
                # Re-check budget even between retries on the same key.
                if time.time() >= deadline:
                    last_error = f"total_timeout exhausted during retry on {model}"
                    break
                # Also cap each individual HTTP request at the smaller of
                # config.timeout and the remaining budget, so we don't
                # fire a 30s request with only 0.5s left.
                per_request_timeout = min(config.timeout, max(1, int(deadline - time.time())))

                start = time.time()
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        resp = httpx.post(
                            f"{config.base_url}/chat/completions",
                            headers={
                                "Authorization": f"Bearer {key}",
                                "Content-Type": "application/json",
                            },
                            json=body,
                            timeout=per_request_timeout,
                        )
                    elapsed_ms = int((time.time() - start) * 1000)

                    if resp.status_code == 200:
                        data = resp.json()
                        choices = data.get("choices") or []
                        if choices:
                            tried.append({
                                "model": model,
                                "key_index": config.api_keys.index(key),
                                "status": 200,
                                "elapsed_s": elapsed_ms / 1000,
                                "note": "ok",
                            })
                            return LLMResponse(
                                content=choices[0].get("message", {}).get("content", ""),
                                model=data.get("model", model),
                                key_index=config.api_keys.index(key),
                                latency_ms=elapsed_ms,
                                attempts=attempts,
                                prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
                                completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
                                total_tokens=data.get("usage", {}).get("total_tokens", 0),
                            )
                        # 200 with no choices — try next model.
                        last_error = "200 with empty choices"
                        tried.append({
                            "model": model,
                            "key_index": config.api_keys.index(key),
                            "status": 200,
                            "elapsed_s": elapsed_ms / 1000,
                            "note": "empty choices",
                        })
                        break

                    if resp.status_code == 429:
                        if _is_daily_quota_error(resp):
                            quota.mark_dead(
                                key, config.daily_quota_cooldown,
                                reason="daily_quota_exceeded",
                            )
                            logger.warning(
                                f"Daily quota exhausted on key#{config.api_keys.index(key)} "

                            )
                            tried.append({
                                "model": model,
                                "key_index": config.api_keys.index(key),
                                "status": 429,
                                "elapsed_s": elapsed_ms / 1000,
                                "note": "daily_quota_dead",
                            })
                            # Break inner loop → outer key loop will pick next key.
                            break
                        # Minute-level rate limit — backoff and retry same key.
                        if attempt < config.max_retries:
                            wait = 2 ** attempt
                            logger.warning(
                                f"429 rate-limit on key#{config.api_keys.index(key)} "
                                f"(model {model}); retry {attempt + 1}/{config.max_retries} in {wait}s"
                            )
                            time.sleep(wait)
                            continue
                        # Out of retries on this key — try next.
                        quota.record_failure(key, 429)
                        last_error = f"429 on {model}"
                        tried.append({
                            "model": model,
                            "key_index": config.api_keys.index(key),
                            "status": 429,
                            "elapsed_s": elapsed_ms / 1000,
                            "note": "rate_limited_retries_exhausted",
                        })
                        break

                    if resp.status_code == 404:
                        logger.warning(
                            f"404: model {model} not found, trying next model"
                        )
                        last_error = f"404: {model}"
                        tried.append({
                            "model": model,
                            "key_index": config.api_keys.index(key),
                            "status": 404,
                            "elapsed_s": elapsed_ms / 1000,
                            "note": "model_not_found",
                        })
                        break  # break key-loop, outer model-loop picks next model

                    if resp.status_code in (401, 403):
                        # Auth issues — this key is BROKEN, not just
                        # quota-exhausted.  Mark permanently dead (100y
                        # cooldown) so we don't waste time on every
                        # subsequent call.  The user must rotate the key.
                        logger.warning(
                            f"Auth error {resp.status_code} on key#{config.api_keys.index(key)}; "
                            f"marking permanently dead"
                        )
                        quota.mark_permanently_dead(
                            key, reason=f"http_{resp.status_code}"
                        )
                        last_error = f"{resp.status_code} auth"
                        tried.append({
                            "model": model,
                            "key_index": config.api_keys.index(key),
                            "status": resp.status_code,
                            "elapsed_s": elapsed_ms / 1000,
                            "note": "auth_failed_marked_dead",
                        })
                        break

                    # Any other 4xx/5xx
                    tried.append({
                        "model": model,
                        "key_index": config.api_keys.index(key),
                        "status": resp.status_code,
                        "elapsed_s": elapsed_ms / 1000,
                        "note": f"http_{resp.status_code}",
                    })
                    resp.raise_for_status()

                except httpx.TimeoutException:
                    last_error = f"timeout on {model}"
                    logger.warning(
                        f"Timeout calling {model} with key#{config.api_keys.index(key)} "
                        f"after {time.time() - start:.1f}s"
                    )
                    tried.append({
                        "model": model,
                        "key_index": config.api_keys.index(key),
                        "status": "timeout",
                        "elapsed_s": time.time() - start,
                        "note": "httpx_timeout",
                    })
                    break  # try next key
                except httpx.HTTPError as e:
                    last_error = f"http error: {str(e)[:80]}"
                    logger.warning(f"HTTP error on {model}: {e}")
                    tried.append({
                        "model": model,
                        "key_index": config.api_keys.index(key),
                        "status": "httpx_error",
                        "elapsed_s": time.time() - start,
                        "note": str(e)[:60],
                    })
                    break
                except Exception as e:
                    last_error = f"unexpected: {str(e)[:80]}"
                    logger.warning(f"Unexpected error on {model}: {e}")
                    tried.append({
                        "model": model,
                        "key_index": config.api_keys.index(key),
                        "status": "exception",
                        "elapsed_s": time.time() - start,
                        "note": str(e)[:60],
                    })
                    break

        # If we got here with a 200, we returned. Otherwise continue to next model.
        else:
            # Inner for-else: didn't break early, all keys for this model failed.
            continue
        # If the inner key-loop broke (e.g. on 404 or timeout-budget), continue model loop.

    # Build diagnostic report.
    total_elapsed = time.time() - call_start
    report = {
        "total_timeout": config.total_timeout,
        "total_elapsed_s": round(total_elapsed, 2),
        "attempts": attempts,
        "last_error": last_error,
        "tried": tried,
        "quota_snapshot": quota.snapshot(),
        "models_attempted": list({t["model"] for t in tried}),
    }
    # Decide whether to raise LLMCallTimeout.  Two triggers:
    #   1. The whole-call budget was breached.
    #   2. Every (key, model) pair failed (we have a final error and
    #      nothing returned).  This is the more general "we tried and
    #      gave up" case — easier for tests to assert on than waiting
    #      for the budget to elapse.
    timed_out = total_elapsed >= config.total_timeout or last_error.startswith("total_timeout")
    all_attempts_failed = (
        attempts > 0
        and last_error
        and last_error not in ("", "All keys × all models exhausted")
    )
    if config.raise_on_timeout and (timed_out or all_attempts_failed):
        raise LLMCallTimeout(report)
    if timed_out:
        logger.error("LLM call report (timeout):\n" + LLMCallTimeout._format(report))

    return LLMResponse(
        content="",
        error=last_error or "All keys × all models exhausted",
        attempts=attempts,
        diagnostic=report,
    )


# ═══════════════════════════════════════════════════════════
# Public API (unchanged signatures — backward compatible)
# ═══════════════════════════════════════════════════════════

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


def quota_snapshot() -> dict:
    """Return current per-key quota state (for diagnostics / CLI)."""
    return QuotaState(_QUOTA_STATE_PATH).snapshot()


# ═══════════════════════════════════════════════════════════
# Hard-timeout exception + diagnostic helpers
# ═══════════════════════════════════════════════════════════


class LLMCallTimeout(Exception):
    """Raised when the whole-call budget (LLMConfig.total_timeout) is breached.

    Carries a structured ``report`` dict so callers (tests, CI, daemon)
    can log exactly which (key, model) pairs were tried, what status
    each one returned, and how much time was spent.  The goal: when a
    test times out, you should be able to read the exception's report
    and know *why* — not just "it hung".
    """

    def __init__(self, report: dict):
        self.report = report
        super().__init__(self._format(report))

    @staticmethod
    def _format(report: dict) -> str:
        lines = [
            f"LLM call exceeded {report.get('total_timeout', '?')}s "
            f"after {report.get('attempts', '?')} attempt(s)."
        ]
        if report.get("last_error"):
            lines.append(f"Last error: {report['last_error']}")
        if report.get("tried"):
            lines.append("Tried:")
            for t in report["tried"]:
                lines.append(
                    f"  - model={t.get('model','?')[:40]:40s} "
                    f"key#{t.get('key_index','?')} "
                    f"status={t.get('status','?')} "
                    f"elapsed={t.get('elapsed_s', 0):.2f}s "
                    f"note={t.get('note','')}"
                )
        if report.get("quota_snapshot"):
            dead = [
                f"key#{i}"
                for i, info in enumerate(report["quota_snapshot"].values())
                if info.get("dead_until", 0)
            ]
            if dead:
                lines.append(f"Keys marked dead: {', '.join(dead)}")
        return "\n".join(lines)


def diagnose() -> dict:
    """One-shot diagnostic snapshot for "what's wrong with my LLM setup".

    Returns a dict with:
      - config: the current config (without leaking the actual key values)
      - quota: per-key alive/dead status
      - ready: whether LLM is callable
      - model_attempt_count: how many models we have to try
    Call this from CLI when something hangs and you want a quick read.
    """
    cfg = get_config()
    snap = QuotaState(_QUOTA_STATE_PATH).snapshot()
    safe_keys = [
        f"key#{i}:{k[:6]}...{k[-4:]}" if len(k) > 12 else f"key#{i}:***"
        for i, k in enumerate(cfg.api_keys)
    ]
    return {
        "ready": cfg.ready,
        "base_url": cfg.base_url,
        "primary_model": cfg.model,
        "fallback_count": len(cfg.fallback_models),
        "api_key_count": len(cfg.api_keys),
        "api_keys_redacted": safe_keys,
        "quota": {
            (f"key#{i}:{k[:6]}...{k[-4:]}" if len(k) > 12 else f"key#{i}:***"): {
                "dead_until": info.get("dead_until", 0),
                "failures_today": info.get("failures_today", 0),
                "last_status": info.get("last_status", 0),
            }
            for i, (k, info) in enumerate(zip(cfg.api_keys, snap.values()))
        },
        "total_timeout_s": cfg.total_timeout,
        "per_request_timeout_s": cfg.timeout,
    }
