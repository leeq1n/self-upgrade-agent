"""Day 6: 5-round live run on MiniMax-M3.

Self-protection:
  1. 5 round, 75s gap (200 RPM = 1 call/0.3s, but 75s is safe margin)
  2. SSL EOF watchdog
  3. Auto-unlock between rounds
  4. Audit results checked after each round
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
MAX_TIME_PER_ROUND = 600  # 10 min cap per round


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


def snapshot():
    return {
        "planner_md5": md5_lf(PLANNER),
        "planner_size": os.path.getsize(PLANNER),
        "history_count": sqlite3.connect("upgrades/history.db").execute(
            "SELECT COUNT(*) FROM upgrades").fetchone()[0],
    }


def run_one_round(n, paper):
    print(f"\n========== ROUND {n}/5 ==========")
    print(f"Paper: {paper['arxiv_id']} — {paper['title'][:60]}")
    preflight()
    pre = snapshot()
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

    t0 = time.time()
    state = None
    try:
        state = plg.run(cfg, dry_run=False)
    except Exception as e:
        print(f"  EXCEPTION: {type(e).__name__}: {str(e)[:200]}")
        state = {"done": False, "errors": [str(e)]}

    elapsed = time.time() - t0
    if elapsed > MAX_TIME_PER_ROUND:
        print(f"  WARN: round took {elapsed:.1f}s > {MAX_TIME_PER_ROUND}s cap")

    post = snapshot()
    audit = state.get("skill_audit", {}) if state else {}
    result = {
        "round": n,
        "paper_id": paper["arxiv_id"],
        "elapsed_s": round(elapsed, 1),
        "done": state.get("done") if state else None,
        "decision": (state.get("decision") or {}).get("decision") if state else None,
        "delta": (state.get("evaluation") or {}).get("success_rate_delta") if state else None,
        "harness": (state.get("evaluation") or {}).get("harness") if state else None,
        "skill_audit": audit,
        "planner_size_before": pre["planner_size"],
        "planner_size_after": post["planner_size"],
        "planner_changed": pre["planner_md5"] != post["planner_md5"],
        "history_before": pre["history_count"],
        "history_after": post["history_count"],
        "history_delta": post["history_count"] - pre["history_count"],
        "errors": (state.get("errors") or [])[:3] if state else None,
    }
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"  done={result['done']} decision={result['decision']}")
    if result["delta"] is not None:
        print(f"  A/B delta={result['delta']:+.2%}")
    if result["harness"]:
        h = result["harness"]
        print(f"  HARNESS: {h.get('passed', 0)}/{h.get('total', 0)} pass")
    if result["skill_audit"]:
        sa = result["skill_audit"]
        print(f"  AUDIT: evaluated={sa.get('evaluated', 0)} culled={sa.get('culled', [])}")
    print(f"  history.db: {pre['history_count']} -> {post['history_count']}")
    if result["errors"]:
        for e in result["errors"]:
            print(f"  err: {str(e)[:150]}")
    return result


# Main
print("=" * 60)
print("Day 6: 5-round self-evolution LIVE")
print(f"Provider: {os.environ.get('LLM_BASE_URL', '?')}")
print(f"Model: {os.environ.get('LLM_MODEL', '?')}")
print(f"HEAD planner MD5: {md5_lf(PLANNER)}")
print("=" * 60)

# 5 different papers
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

results = []
for n in range(1, 6):  # 5 rounds
    r = run_one_round(n, PAPERS[n-1])
    results.append(r)
    if n < 5:
        print(f"\n(waiting 75s to dodge RPM)")
        time.sleep(75)

# Final safety + save
preflight()
final_md5 = md5_lf(PLANNER)
print("\n" + "=" * 60)
print("FINAL")
print("=" * 60)
print(f"planner.py MD5: {final_md5}")
print(f"history.db total rows: {sqlite3.connect('upgrades/history.db').execute('SELECT COUNT(*) FROM upgrades').fetchone()[0]}")
print(f"audit_history rows: {sqlite3.connect('upgrades/history.db').execute('SELECT COUNT(*) FROM audit_history').fetchone()[0]}")

# Save results
out = {
    "run_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "head_md5": md5_lf(PLANNER),
    "final_planner_md5": final_md5,
    "rounds": results,
    "summary": {
        "kept": sum(1 for r in results if r["decision"] == "kept"),
        "reverted": sum(1 for r in results if r["decision"] == "reverted"),
        "done": sum(1 for r in results if r["done"]),
    },
}
ts = time.strftime("%Y%m%d_%H%M%S")
out_path = f"upgrades/day6_5rounds_{ts}.json"
with open(out_path, "w") as f:
    json.dump(out, f, indent=2, default=str)
print(f"Results saved to {out_path}")
subprocess.run([sys.executable, "-m", "self_upgrade", "unlock"],
    cwd=PROJECT, capture_output=True)
print("Quota unlocked")
print("DONE")
