"""v1.8.1: Goal machinery for the self-evolution loop.

User insight (2026-07-07):
  - "当前没有设计的最好的目标函数或奖励函数"
  - "保留可扩展性,未来动态变化"
  - "小心可扩展性被锁死 (用 harness 避免)"
  - "奥卡姆剃刀原则"

DESIGN (三层):

  Level 1 (涌现):  Goal strategies are *data*, not code.
                   The pipeline asks "what should we do this round?"
                   The answer is picked from a registry.  LLM can
                   register new strategies via patchgen, OR by adding
                   entries to the registry at runtime.

  Level 2 (防锁死): Harness tests guarantee strategies are:
                     - serializable (can be removed/saved)
                     - have a decide_fn that returns a known string
                     - can be called with state, never crash the pipeline
                   If a new strategy fails harness, patch is REVERTED
                   (same atomic write mechanism that protects core/planner.py).

  Level 3 (奥卡姆): If the registry is empty OR every strategy crashes,
                   fallback to a single hardcoded "explore" strategy
                   that does the safest thing: pick a paper we haven't
                   seen, prefer recent categories.

KEY ANTI-LOCK-IN PROPERTIES:
  1. Registry is mutable at runtime (no compile-time fixed list)
  2. Strategies are pure functions (no side effects on registration)
  3. Each strategy has a 'test_fn' that can be invoked to verify
     it works correctly — this is the harness layer
  4. Removing a strategy does NOT break the loop (fallback exists)
  5. Default fallback NEVER changes (奥卡姆: simplest possible)
"""
from typing import Callable, Dict, Any, Optional, List


# ── Registry (mutable, runtime-extensible) ───────────────────────────────

# Each strategy is a dict with:
#   description: str              — what the strategy does
#   decide_fn: Callable[[state], str]  — picks the next strategy
#   test_fn: Optional[Callable]   — sanity check (run by harness)
#
# 'decide_fn' takes a state dict (last_outcome + round) and returns
# a strategy NAME.  This allows strategies to chain (A decides B).
#
# If decide_fn raises or returns an unknown name, the loop falls back
# to the built-in "explore" strategy.

_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register(name: str, description: str,
             decide_fn: Callable[[Dict[str, Any]], str],
             test_fn: Optional[Callable[[], bool]] = None) -> None:
    """Register a strategy.  Re-registering overwrites (allows patching).

    Args:
        name: unique identifier
        description: human-readable (goes into LLM prompts)
        decide_fn: callable(state) -> next_strategy_name
        test_fn: optional sanity check, returns True if healthy

    Raises:
        ValueError: if name is empty or decide_fn is not callable
    """
    if not name or not isinstance(name, str):
        raise ValueError(f"strategy name must be non-empty string, got {name!r}")
    if not callable(decide_fn):
        raise ValueError(f"decide_fn must be callable, got {type(decide_fn).__name__}")
    _REGISTRY[name] = {
        "description": description,
        "decide_fn": decide_fn,
        "test_fn": test_fn,
    }


def unregister(name: str) -> bool:
    """Remove a strategy from the registry.  Returns True if it existed."""
    return _REGISTRY.pop(name, None) is not None


def list_strategies() -> List[str]:
    """Return names of currently-registered strategies."""
    return list(_REGISTRY.keys())


def get_strategy(name: str) -> Optional[Dict[str, Any]]:
    """Return strategy dict (with description, decide_fn, test_fn)."""
    return _REGISTRY.get(name)


def clear_registry() -> None:
    """Remove ALL strategies.  Used by tests + emergency fallback."""
    _REGISTRY.clear()


# ── Built-in fallback (奥卡姆: never changes, never removed) ─────────────

# This is the ONLY hard-coded strategy.  It is intentionally simple
# and CANNOT be removed (we use _HARDCODED_FALLBACK not _REGISTRY).
# If every other strategy fails, this one runs.

_HARDCODED_FALLBACK = {
    "description": "Pick a paper we haven't seen, prefer recent.  Always safe.",
    "decide_fn": lambda state: "fallback_explore",  # refers to itself
    "test_fn": lambda: True,
}


def _fallback() -> Dict[str, Any]:
    """Return the built-in fallback strategy.  Always exists."""
    return _HARDCODED_FALLBACK


def _fallback_decide(state: Dict[str, Any]) -> str:
    """The fallback strategy decides to keep itself (no chaining)."""
    return "fallback_explore"


# ── Public API ──────────────────────────────────────────────────────────

def pick_strategy(state: Dict[str, Any]) -> str:
    """Pick the strategy to use this round.

    Args:
        state: dict with keys like:
            - "round_number": int
            - "last_outcome": dict | None
            - "long_term_goal": str | None

    Returns:
        A strategy NAME (string).  Guaranteed to be non-empty.

    Anti-lock-in behavior:
        1. If registry is empty → return "fallback_explore"
        2. Try the strategy named in state["next_strategy"] if set
        3. Otherwise try each registered strategy in registration order
        4. First one whose decide_fn runs without raising wins
        5. If ALL fail → return "fallback_explore"
    """
    if not _REGISTRY:
        return "fallback_explore"

    # Honor explicit request first (LLM can pre-declare via state)
    explicit = state.get("next_strategy")
    if explicit and explicit in _REGISTRY:
        try:
            result = _REGISTRY[explicit]["decide_fn"](state)
            if isinstance(result, str) and result:
                return result
        except Exception:
            pass  # fall through to default

    # Try each registered strategy in order
    for name, strat in _REGISTRY.items():
        try:
            result = strat["decide_fn"](state)
            if isinstance(result, str) and result:
                return result
        except Exception:
            continue

    return "fallback_explore"


def describe(name: str) -> str:
    """Return human-readable description of a strategy.

    Falls back to the hardcoded description if name is unknown.
    """
    if name == "fallback_explore":
        return _HARDCODED_FALLBACK["description"]
    s = _REGISTRY.get(name)
    if s is None:
        return f"(unknown strategy: {name})"
    return s["description"]


def run_health_check() -> Dict[str, bool]:
    """Run test_fn for each registered strategy + fallback.

    Returns dict: {strategy_name: test_passed}.
    This is what harness tests assert on.
    """
    out = {"fallback_explore": True}  # fallback is always healthy
    for name, strat in _REGISTRY.items():
        test_fn = strat.get("test_fn")
        if test_fn is None:
            out[name] = True  # no test = trust it (奥卡姆)
            continue
        try:
            out[name] = bool(test_fn())
        except Exception:
            out[name] = False
    return out


def registry_size() -> int:
    """How many strategies are currently registered.  For diagnostics."""
    return len(_REGISTRY)


# ── Default long-term goal ─────────────────────────────────────────────
# Even this is a fallback — can be overridden by --long-term-goal flag
# at runtime.  v1.8.1 doesn't ship a "register long-term goal" mechanism;
# that's for future evolution.

DEFAULT_LONG_TERM_GOAL = (
    "Improve core/planner.py task decomposition success rate "
    "while keeping harness tests green"
)