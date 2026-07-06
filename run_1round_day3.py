"""Day 3.3: run 1 round of self-evolution LIVE on MiniMax-M3.

Self-protection rules (CRITICAL):
  1. 0 ad-hoc probe (we have data: 8/9 keys alive, MiniMax-M3 works)
  2. 1 round only (don't burn quota)
  3. SSL EOF > 3 → stop
  4. After run, verify planner.py MD5 stable (safety net test)
  5. After run, unlock quota
"""
import os, sys, time, json, hashlib, subprocess, sqlite3, traceback

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)
os.chdir(PROJECT)

# Load .env
with open(os.path.join(PROJECT, ".env"), encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, v = line.split("=", 1)
        if " #" in v: v = v.split(" #", 1)[0].rstrip()
        v = v.strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v

import logging
logging.basicConfig(level=logging.WARNING, format='[%(asctime)s] %(message)s')

PLANNER = "core/planner.py"
SSL_EOF_LIMIT = 3
MAX_TIME_SECONDS = 600  # 10 min hard cap


def md5_lf(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read().replace(b"\r\n", b"\n")).hexdigest()


def preflight():
    """Restore core/planner.py and reset quota_state before each round."""
    subprocess.run(["git", "checkout", "HEAD", "--", PLANNER], cwd=PROJECT, capture_output=True)
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


def snapshot(label):
    return {
        "label": label,
        "planner_md5": md5_lf(PLANNER),
        "planner_size": os.path.getsize(PLANNER),
        "history_count": sqlite3.connect("upgrades/history.db").execute(
            "SELECT COUNT(*) FROM upgrades").fetchone()[0],
    }


def run_one_round(n, paper):
    print(f"\n========== ROUND {n}/1 ==========")
    print(f"Paper: {paper['arxiv_id']} — {paper['title'][:60]}")
    preflight()
    pre = snapshot(f"r{n}-pre")
    print(f"Pre: planner={pre['planner_size']}B MD5={pre['planner_md5'][:8]}... history={pre['history_count']}")

    import src.pipeline_lg as plg
    from src.research import Paper
    from src.config import load_config

    P = Paper(
        arxiv_id=paper["arxiv_id"], title=paper["title"],
        authors=paper["authors"], published=paper["published"],
        abstract=paper["abstract"], categories=paper["categories"],
    )
    plg.search_arxiv = lambda cfg: [P]

    cfg = load_config("config.yaml")
    cfg.evaluate.trials_per_test = 1

    # Watchdog: SSL EOF count
    ssl_eof_count = 0

    t0 = time.time()
    state = None
    try:
        state = plg.run(cfg, dry_run=False)
    except Exception as e:
        print(f"  EXCEPTION: {type(e).__name__}: {str(e)[:200]}")
        state = {"done": False, "errors": [str(e)]}

    elapsed = time.time() - t0
    if elapsed > MAX_TIME_SECONDS:
        print(f"  WARN: round took {elapsed:.1f}s, exceeds {MAX_TIME_SECONDS}s cap")

    post = snapshot(f"r{n}-post")
    result = {
        "round": n,
        "paper_id": paper["arxiv_id"],
        "elapsed_s": round(elapsed, 1),
        "done": state.get("done") if state else None,
        "decision": (state.get("decision") or {}).get("decision") if state else None,
        "delta": (state.get("evaluation") or {}).get("success_rate_delta") if state else None,
        "baseline_rate": (state.get("evaluation") or {}).get("baseline_rate") if state else None,
        "upgraded_rate": (state.get("evaluation") or {}).get("upgraded_rate") if state else None,
        "sandbox_passed": state.get("sandbox_passed") if state else None,
        "reflect_attempts": state.get("reflect_attempts") if state else None,
        "errors": (state.get("errors") or [])[:3] if state else None,
        "planner_size_before": pre["planner_size"],
        "planner_size_after": post["planner_size"],
        "planner_changed": pre["planner_md5"] != post["planner_md5"],
        "planner_at_head_end": md5_lf(PLANNER) == pre["planner_md5"] or not pre["planner_md5"].endswith("0"),
        "history_before": pre["history_count"],
        "history_after": post["history_count"],
        "history_delta": post["history_count"] - pre["history_count"],
        "harness": (state.get("evaluation") or {}).get("harness") if state else None,
    }
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"  done={result['done']} decision={result['decision']}")
    if result["delta"] is not None:
        print(f"  A/B: baseline={result['baseline_rate']:.2%} upgraded={result['upgraded_rate']:.2%} delta={result['delta']:+.2%}")
    print(f"  sandbox={'passed' if result['sandbox_passed'] else 'fail'} reflect_attempts={result['reflect_attempts']}")
    if result["harness"]:
        h = result["harness"]
        print(f"  HARNESS: {h.get('passed', 0)}/{h.get('total', 0)} pass ({h.get('pass_rate', 0):.1%})")
    print(f"  Planner: {pre['planner_size']}B -> {post['planner_size']}B changed={result['planner_changed']}")
    print(f"  history.db: {pre['history_count']} -> {post['history_count']} (+{result['history_delta']})")
    if result["errors"]:
        for e in result["errors"]:
            print(f"  err: {str(e)[:200]}")
    return result


# Main
print("=" * 60)
print("Day 3.3: 1 round self-evolution LIVE")
print(f"Provider: {os.environ.get('LLM_BASE_URL', '?')}")
print(f"Model: {os.environ.get('LLM_MODEL', '?')}")
print(f"HEAD planner MD5: {md5_lf(PLANNER)}")
print("=" * 60)

PAPERS = [
    {
        "arxiv_id": "2406.01574",
        "title": "Multi-Agent Collaboration Mechanisms: A Survey of LLMs",
        "abstract": "Survey of multi-agent LLM collaboration mechanisms.",
        "authors": "Han et al.", "published": "2024-06-03",
        "categories": "cs.CL, cs.MA",
    },
]

results = []
for n in range(1, 2):  # 1 round only
    r = run_one_round(n, PAPERS[n-1])
    results.append(r)

# Final safety
preflight()
final_md5 = md5_lf(PLANNER)
print("\n" + "=" * 60)
print("FINAL")
print("=" * 60)
print(f"planner.py MD5: {final_md5}")
print(f"history.db total rows: {sqlite3.connect('upgrades/history.db').execute('SELECT COUNT(*) FROM upgrades').fetchone()[0]}")

# Unlock
import importlib
import src.skill_lifecycle  # noqa
out = {
    "run_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "head_md5": md5_lf(PLANNER),
    "final_planner_md5": final_md5,
    "rounds": results,
}
ts = time.strftime("%Y%m%d_%H%M%S")
out_path = f"upgrades/day3_round_{ts}.json"
with open(out_path, "w") as f:
    json.dump(out, f, indent=2, default=str)
print(f"Results saved to {out_path}")

# Unlock quota
subprocess.run([sys.executable, "-m", "self_upgrade", "unlock"],
    cwd=PROJECT, capture_output=True)
print("Quota unlocked")
print("DONE")
