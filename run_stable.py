"""Day 7+: stable self-evolution runner.

Goal: keep running rounds UNTIL harness is 100% + decision=KEPT
for N consecutive rounds (default N=3).  Stop on success.

This is the real "self-evolution convergence" test, not just
"did 1 round work".

Usage:
  python run_stable.py           # default: 3 consecutive KEPT rounds
  python run_stable.py 5         # 5 consecutive KEPT rounds
  python run_stable.py 1         # 1 KEPT round (smoke test)
  python run_stable.py 3 60      # 3 KEPT rounds, 60s gap (avoid model warmup)

State:
  planner.py MUST be at HEAD (preflight restores it)
  quota_state.json gets reset between rounds
  Each round's state saved to upgrades/run_stable_<ts>.json

Self-protection:
  - 0 LLM calls in the wrapper itself
  - User runs it; reads results; decides when to stop
"""
import os, sys, time, json, hashlib, subprocess, sqlite3, traceback

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


def run_one_round(n, paper, consecutive_kept_so_far):
    print(f"\n========== ROUND {n} (consecutive KEPT: {consecutive_kept_so_far}) ==========")
    print(f"Paper: {paper['arxiv_id']} — {paper['title'][:60]}")
    preflight()
    pre_history = sqlite3.connect("upgrades/history.db").execute(
        "SELECT COUNT(*) FROM upgrades").fetchone()[0]
    pre_audit = sqlite3.connect("upgrades/history.db").execute(
        "SELECT COUNT(*) FROM audit_history").fetchone()[0]

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
    # Inject fake paper by patching the symbol in node_research\'s closure.
    # The function imported the name at module load, so we need to patch
    # the name in pipeline_lg\'s namespace too.
    plg.search_arxiv = lambda cfg: [P]
    # Also patch the symbol in src.research (source of truth)
    import src.research as research_mod
    research_mod.search_arxiv = lambda cfg: [P]

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

    decision = (state.get("decision") or {}).get("decision") if state else None
    harness = (state.get("evaluation") or {}).get("harness") if state else None
    audit = state.get("skill_audit") if state else None

    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"  done={state.get('done') if state else None} decision={decision}")
    if state and state.get("evaluation", {}).get("success_rate_delta") is not None:
        ev = state["evaluation"]
        print(f"  A/B: baseline={ev.get('baseline_rate', 0):.2%} "
              f"upgraded={ev.get('upgraded_rate', 0):.2%} "
              f"delta={ev.get('success_rate_delta', 0):+.2%}")
    if harness:
        print(f"  HARNESS: {harness.get('passed', 0)}/{harness.get('total', 0)} "
              f"({harness.get('pass_rate', 0):.1%})")
    if audit:
        print(f"  AUDIT: evaluated={audit.get('evaluated', 0)} culled={audit.get('culled', [])}")
    post_history = sqlite3.connect("upgrades/history.db").execute(
        "SELECT COUNT(*) FROM upgrades").fetchone()[0]
    post_audit = sqlite3.connect("upgrades/history.db").execute(
        "SELECT COUNT(*) FROM audit_history").fetchone()[0]
    print(f"  history.db: {pre_history} -> {post_history}")
    print(f"  audit_history: {pre_audit} -> {post_audit}")
    print(f"  planner.py MD5: {md5_lf(PLANNER)}")

    return {
        "round": n,
        "paper_id": paper["arxiv_id"],
        "elapsed_s": round(elapsed, 1),
        "done": state.get("done") if state else None,
        "decision": decision,
        "delta": (state.get("evaluation") or {}).get("success_rate_delta") if state else None,
        "harness": harness,
        "skill_audit": audit,
        "history_delta": post_history - pre_history,
        "audit_delta": post_audit - pre_audit,
        "errors": (state.get("errors") or [])[:3] if state else None,
    }


# Default papers (5 candidates, rotates)
PAPERS = [
    {"arxiv_id": "2406.01574", "title": "Multi-Agent Collaboration Mechanisms: A Survey of LLMs",
     "abstract": "Survey of multi-agent LLM collaboration mechanisms.",
     "authors": "Han et al.", "published": "2024-06-03", "categories": "cs.CL, cs.MA"},
    {"arxiv_id": "2606.30639", "title": "Self-Evolving World Models for LLM Agent Planning",
     "abstract": "WorldEvolver with Episodic Memory.",
     "authors": "Anon", "published": "2026-06-30", "categories": "cs.AI"},
    {"arxiv_id": "2310.02170", "title": "AutoGen: Multi-Agent Conversation",
     "abstract": "AutoGen framework for multi-agent LLM systems.",
     "authors": "Wu et al.", "published": "2023-10-03", "categories": "cs.CL"},
    {"arxiv_id": "2304.14733", "title": "Generative Agents: Interactive Simulacra of Human Behavior",
     "abstract": "Generative agents with memory, reflection, planning.",
     "authors": "Park et al.", "published": "2023-04", "categories": "cs.CL"},
    {"arxiv_id": "2210.03629", "title": "ReAct: Reasoning and Acting",
     "abstract": "ReAct framework for LLM reasoning + acting.",
     "authors": "Yao et al.", "published": "2022-10", "categories": "cs.CL"},
]


def main():
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    gap = int(sys.argv[2]) if len(sys.argv) > 2 else 75

    print("=" * 60)
    print(f"Day 7+ : stable self-evolution runner")
    print(f"Target: {target} consecutive KEPT rounds")
    print(f"Provider: {os.environ.get('LLM_BASE_URL', '?')}")
    print(f"Model: {os.environ.get('LLM_MODEL', '?')}")
    print(f"Gap: {gap}s between rounds")
    print("=" * 60)

    consecutive_kept = 0
    consecutive_kept_with_harness = 0  # KEPT AND harness=100%
    consecutive_kept_runs = []  # list of round dicts (the consecutive kept ones)
    all_runs = []
    max_rounds = 20  # hard cap to prevent infinite loop

    for n in range(1, max_rounds + 1):
        # Pick paper (rotate through PAPERS)
        paper = PAPERS[(n - 1) % len(PAPERS)]
        result = run_one_round(n, paper, consecutive_kept_with_harness)
        all_runs.append(result)

        if result["decision"] == "kept":
            consecutive_kept += 1
            harness_pct = (result.get("harness") or {}).get("pass_rate", 0.0)
            if harness_pct == 1.0:
                consecutive_kept_with_harness += 1
                consecutive_kept_runs.append(result)
                print(f"  >>> CONSECUTIVE KEPT WITH HARNESS 100%: {consecutive_kept_with_harness}/{target}")
            else:
                # Reset counter — KEPT but harness not 100% is a partial win
                consecutive_kept_with_harness = 0
                consecutive_kept_runs = []
                print(f"  >>> KEPT but harness < 100% (counter reset)")
        else:
            consecutive_kept = 0
            consecutive_kept_with_harness = 0
            consecutive_kept_runs = []
            print(f"  >>> NOT KEPT (counter reset)")

        if consecutive_kept_with_harness >= target:
            print(f"\n*** REACHED TARGET: {target} consecutive KEPT rounds with harness 100% ***")
            break

        if n < max_rounds:
            print(f"\n(waiting {gap}s)")
            time.sleep(gap)

    # Final summary
    preflight()
    print("\n" + "=" * 60)
    print("FINAL")
    print("=" * 60)
    print(f"Total rounds: {len(all_runs)}")
    print(f"Consecutive KEPT with harness 100%: {consecutive_kept_with_harness}/{target}")
    print(f"planner.py MD5: {md5_lf(PLANNER)}")
    print(f"history.db: {sqlite3.connect('upgrades/history.db').execute('SELECT COUNT(*) FROM upgrades').fetchone()[0]} rows")
    print(f"audit_history: {sqlite3.connect('upgrades/history.db').execute('SELECT COUNT(*) FROM audit_history').fetchone()[0]} rows")

    out = {
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "target": target,
        "achieved": consecutive_kept_with_harness,
        "consecutive_kept_runs": consecutive_kept_runs,
        "all_runs": all_runs,
        "planner_md5": md5_lf(PLANNER),
    }
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = f"upgrades/run_stable_{ts}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"Results saved to {out_path}")

    subprocess.run([sys.executable, "-m", "self_upgrade", "unlock"],
                   cwd=PROJECT, capture_output=True)
    print("Quota unlocked")
    print("DONE")

    if consecutive_kept_with_harness >= target:
        sys.exit(0)  # success
    else:
        sys.exit(2)  # not converged


if __name__ == "__main__":
    main()
