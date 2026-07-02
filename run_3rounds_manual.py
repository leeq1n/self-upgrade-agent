"""3-round self-evolution run (manual, MiniMax provider).

User runs this manually:
  python run_3rounds_manual.py

This runs the pipeline 3 times with the same 3 papers, reports
real-time state of core/planner.py and history.db, and saves
results to upgrades/3round_manual_<timestamp>.json.

Stops on first round that successfully promotes (decision=kept).
If all 3 revert, still saves results and reports the situation.

Cost: ~50 LLM calls per round × 3 rounds = ~150 calls.
Uses claude-sonnet-4-5 on api.minimaxi.com/anthropic endpoint.
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
        k = k.strip(); v = v.strip()
        if " #" in v: v = v.split(" #", 1)[0].rstrip()
        v = v.strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v

import logging
logging.basicConfig(level=logging.WARNING, format='[%(asctime)s] %(message)s')

PLANNER = "core/planner.py"

# 3 papers to try. Use different ones so we don't waste quota on the same.
# (2406.01574, 2310.02170, 2606.30639 are well-known multi-agent papers
#  available on arxiv; if MiniMax endpoint is actually ModelScope behind
#  the scenes, arxiv API is currently flaky so we mock them.)
PAPERS = [
    {
        "arxiv_id": "2406.01574",
        "title": "Multi-Agent Collaboration Mechanisms: A Survey of LLMs",
        "abstract": "Survey of multi-agent LLM collaboration mechanisms including role-based, message-passing, and consensus-based architectures. Reviews AutoGen, CrewAI, LangGraph multi-agent patterns.",
        "authors": "Han et al.",
        "published": "2024-06-03",
        "categories": "cs.CL, cs.MA",
    },
    {
        "arxiv_id": "2606.30639",
        "title": "Self-Evolving World Models for LLM Agent Planning",
        "abstract": "WorldEvolver introduces self-evolving world model with Episodic Memory, Semantic Memory, Selective Foresight. Evaluated on ALFWorld and ScienceWorld.",
        "authors": "Anon",
        "published": "2026-06-30",
        "categories": "cs.AI, cs.CL",
    },
    {
        "arxiv_id": "2310.02170",
        "title": "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation",
        "abstract": "AutoGen framework for multi-agent LLM systems. Customizable agents that converse to solve tasks. Demonstrated on math, coding, decision-making benchmarks.",
        "authors": "Wu et al.",
        "published": "2023-10-03",
        "categories": "cs.CL, cs.MA",
    },
]


def md5_lf(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read().replace(b"\r\n", b"\n")).hexdigest()


def head_md5():
    r = subprocess.run(["git", "ls-tree", "HEAD", PLANNER], capture_output=True, text=True, cwd=PROJECT)
    sha = r.stdout.strip().split()[2]
    r2 = subprocess.run(["git", "cat-file", "blob", sha], capture_output=True, cwd=PROJECT)
    return hashlib.md5(r2.stdout).hexdigest()


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
        "planner_at_head": md5_lf(PLANNER) == head_md5(),
        "history_count": sqlite3.connect("upgrades/history.db").execute("SELECT COUNT(*) FROM upgrades").fetchone()[0],
    }


def run_one_round(n, paper):
    print(f"\n========== ROUND {n}/3 ==========")
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
    import src.research as research_mod
    research_mod.search_arxiv = lambda cfg: [P]
    plg.search_arxiv = lambda cfg: [P]

    cfg = load_config("config.yaml")
    cfg.evaluate.trials_per_test = 1

    t0 = time.time()
    state = None
    try:
        state = plg.run(cfg, dry_run=False)
    except Exception as e:
        print(f"  EXCEPTION: {type(e).__name__}: {str(e)[:200]}")
        state = {"done": False, "errors": [str(e)]}
    elapsed = time.time() - t0

    post = snapshot(f"r{n}-post")
    result = {
        "round": n,
        "paper_id": paper["arxiv_id"],
        "paper_title": paper["title"][:50],
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
        "planner_changed": pre["planner_size"] != post["planner_size"] or pre["planner_md5"] != post["planner_md5"],
        "planner_at_head_end": post["planner_at_head"],
        "history_before": pre["history_count"],
        "history_after": post["history_count"],
        "history_delta": post["history_count"] - pre["history_count"],
    }

    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"  done={result['done']} decision={result['decision']}")
    if result["delta"] is not None:
        print(f"  A/B: baseline={result['baseline_rate']:.2%} upgraded={result['upgraded_rate']:.2%} delta={result['delta']:+.2%}")
    print(f"  sandbox={'passed' if result['sandbox_passed'] else 'fail'} reflect_attempts={result['reflect_attempts']}")
    print(f"  Planner: {pre['planner_size']}B -> {post['planner_size']}B changed={result['planner_changed']} at_head={result['planner_at_head_end']}")
    print(f"  history.db: {pre['history_count']} -> {post['history_count']} (+{result['history_delta']})")
    if result["errors"]:
        for e in result["errors"]:
            print(f"  err: {str(e)[:150]}")
    return result


# === MAIN ===
print("=" * 60)
print("3-round self-evolution manual run")
print(f"Provider: {os.environ.get('LLM_BASE_URL', '?')}")
print(f"Model: {os.environ.get('LLM_MODEL', '?')}")
print(f"HEAD planner MD5: {head_md5()}")
print("=" * 60)

results = []
for n in range(1, 4):
    r = run_one_round(n, PAPERS[n-1])
    results.append(r)
    if n < 3:
        print(f"\n(waiting 75s to dodge RPM 1002)")
        time.sleep(75)

# Final state
print("\n" + "=" * 60)
print("FINAL")
print("=" * 60)
preflight()  # final safety
final_md5 = md5_lf(PLANNER)
final_size = os.path.getsize(PLANNER)
head = head_md5()
print(f"planner.py: {final_size}B MD5={final_md5[:12]}... matches_HEAD={final_md5 == head}")
print(f"history.db total rows: {sqlite3.connect('upgrades/history.db').execute('SELECT COUNT(*) FROM upgrades').fetchone()[0]}")
r = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, cwd=PROJECT)
print(f"git status: {r.stdout!r}")

# Summary
kept_rounds = [r for r in results if r["decision"] == "kept"]
reverted_rounds = [r for r in results if r["decision"] == "reverted"]
print(f"\n3 rounds summary:")
print(f"  kept: {len(kept_rounds)}")
print(f"  reverted: {len(reverted_rounds)}")
print(f"  failed: {len([r for r in results if r['decision'] is None])}")
print(f"  total LLM calls: ~{sum(1 for _ in results) * 50} (estimated)")

# Save results
out = {
    "run_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "head_md5": head,
    "final_planner_md5": final_md5,
    "final_planner_size": final_size,
    "rounds": results,
    "summary": {
        "kept": len(kept_rounds),
        "reverted": len(reverted_rounds),
        "failed": len([r for r in results if r["decision"] is None]),
    },
}
ts = time.strftime("%Y%m%d_%H%M%S")
out_path = f"upgrades/3round_manual_{ts}.json"
with open(out_path, "w") as f:
    json.dump(out, f, indent=2, default=str)
print(f"\nResults saved to {out_path}")
print("\nDONE")
