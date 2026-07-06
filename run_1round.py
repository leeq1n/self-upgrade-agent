"""Day 6+: 1 round live self-evolution (v1.8.0, harness-aware).

After v1.8.0 changes:
  - node_evaluate now calls run_harness() (subprocess pytest)
  - node_skill_audit runs after decide (0 LLM)
  - audit_history table tracks audit runs
  - LLM_MODELS must be only real MiniMax models (no claude-*)

This wrapper is the cleanest way to run 1 round.  It:
  1. Unlocks quota
  2. Pre-flights (git checkout HEAD, restore planner.py)
  3. Runs 1 round with paper from CLI arg (or default)
  4. Reports decision + harness + audit

Usage:
  python run_1round.py
  python run_1round.py 2606.30639
  python run_1round.py 2606.30639 "Custom paper title"
"""
import os, sys, time, json, hashlib, subprocess, sqlite3

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)
os.chdir(PROJECT)

# Load .env
with open(os.path.join(PROJECT, ".env"), encoding="utf-8-sig") as f:
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

import logging
logging.basicConfig(level=logging.WARNING, format='[%(asctime)s] %(message)s')

PLANNER = "core/planner.py"


def md5_lf(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read().replace(b"\r\n", b"\n")).hexdigest()


def preflight():
    subprocess.run(["git", "checkout", "HEAD", "--", PLANNER],
                   cwd=PROJECT, capture_output=True)
    qf = "upgrades/quota_state.json"
    if os.path.exists(qf):
        try:
            state = json.load(open(qf))
            for info in state.get("keys", {}).values():
                info["dead_until"] = 0
                info["failures_today"] = 0
            json.dump(state, open(qf, "w"), indent=2)
        except Exception:
            pass


def run_one_round(paper):
    print("=" * 60)
    print("Day 6+ : 1 round self-evolution LIVE (v1.8.0)")
    print(f"Provider: {os.environ.get('LLM_BASE_URL', '?')}")
    print(f"Model: {os.environ.get('LLM_MODEL', '?')}")
    print(f"Fallback: {os.environ.get('LLM_MODELS', '?')}")
    print(f"HEAD planner MD5: {md5_lf(PLANNER)}")
    print("=" * 60)

    preflight()
    pre_history = sqlite3.connect("upgrades/history.db").execute(
        "SELECT COUNT(*) FROM upgrades").fetchone()[0]
    pre_audit = sqlite3.connect("upgrades/history.db").execute(
        "SELECT COUNT(*) FROM audit_history").fetchone()[0]
    print(f"Pre: history={pre_history} audit_history={pre_audit}")

    import src.pipeline_lg as plg
    from src.research import Paper
    from src.config import load_config

    P = Paper(
        arxiv_id=paper["arxiv_id"],
        title=paper["title"],
        authors=paper.get("authors", "Unknown"),
        published=paper.get("published", "2024"),
        abstract=paper.get("abstract", paper["title"]),
        categories=paper.get("categories", "cs.CL"),
    )
    plg.search_arxiv = lambda cfg: [P]

    cfg = load_config("config.yaml")
    cfg.evaluate.trials_per_test = 1

    t0 = time.time()
    state = None
    try:
        state = plg.run(cfg, dry_run=False)
    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {str(e)[:300]}")
        state = {"done": False, "errors": [str(e)]}

    elapsed = time.time() - t0

    # Report
    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)
    print(f"Paper: {paper['arxiv_id']} — {paper['title'][:60]}")
    print(f"Elapsed: {elapsed:.1f}s")
    print(f"done={state.get('done') if state else None}")
    print(f"decision={((state.get('decision') or {}).get('decision') if state else None)}")

    if state and state.get("evaluation"):
        ev = state["evaluation"]
        if ev.get("success_rate_delta") is not None:
            print(f"A/B: baseline={ev.get('baseline_rate', 0):.2%} "
                  f"upgraded={ev.get('upgraded_rate', 0):.2%} "
                  f"delta={ev.get('success_rate_delta', 0):+.2%}")
        h = ev.get("harness", {})
        if h:
            print(f"HARNESS: {h.get('passed', 0)}/{h.get('total', 0)} pass "
                  f"({h.get('pass_rate', 0):.1%})")
            if h.get("failures"):
                print(f"  Failures: {h['failures'][:3]}")

    if state and state.get("skill_audit"):
        sa = state["skill_audit"]
        print(f"AUDIT: evaluated={sa.get('evaluated', 0)} culled={sa.get('culled', [])}")

    if state:
        print(f"sandbox={state.get('sandbox_passed')} "
              f"reflect_attempts={state.get('reflect_attempts', 0)}")

    # Final state
    post_history = sqlite3.connect("upgrades/history.db").execute(
        "SELECT COUNT(*) FROM upgrades").fetchone()[0]
    post_audit = sqlite3.connect("upgrades/history.db").execute(
        "SELECT COUNT(*) FROM audit_history").fetchone()[0]
    print()
    print(f"history.db: {pre_history} -> {post_history} (+{post_history - pre_history})")
    print(f"audit_history: {pre_audit} -> {post_audit} (+{post_audit - pre_audit})")
    print(f"planner.py MD5: {md5_lf(PLANNER)}")

    if state and state.get("errors"):
        print()
        print(f"Errors ({len(state['errors'])}):")
        for e in state["errors"][:3]:
            print(f"  {str(e)[:200]}")

    # Save result
    out = {
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "paper": paper,
        "elapsed_s": round(elapsed, 1),
        "state_keys": list(state.keys()) if state else [],
        "done": state.get("done") if state else None,
        "decision": (state.get("decision") or {}).get("decision") if state else None,
        "evaluation": state.get("evaluation") if state else None,
        "skill_audit": state.get("skill_audit") if state else None,
        "errors": (state.get("errors") or [])[:3] if state else None,
    }
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = f"upgrades/run_1round_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nResults saved to {out_path}")

    # Auto-unlock
    subprocess.run([sys.executable, "-m", "self_upgrade", "unlock"],
                   cwd=PROJECT, capture_output=True)
    print("Quota unlocked")
    print("DONE")


if __name__ == "__main__":
    # Default paper
    DEFAULT_PAPER = {
        "arxiv_id": "2406.01574",
        "title": "Multi-Agent Collaboration Mechanisms: A Survey of LLMs",
        "abstract": "Survey of multi-agent LLM collaboration mechanisms.",
        "authors": "Han et al.",
        "published": "2024-06-03",
        "categories": "cs.CL, cs.MA",
    }
    if len(sys.argv) > 1:
        DEFAULT_PAPER["arxiv_id"] = sys.argv[1]
    if len(sys.argv) > 2:
        DEFAULT_PAPER["title"] = sys.argv[2]
    run_one_round(DEFAULT_PAPER)
