"""v1.8.1: bulk paper collection + filtering.

Strategy (your request):
  1. Fetch a large batch of arxiv papers (50+ abstracts) on a topic
  2. LLM-filter to find papers relevant to "self-evolving agent"
  3. Save the LLM-ranked list to upgrades/collected_papers.json
  4. Pipeline will use this list as a paper source (instead of search_arxiv
     which only returns a few)

Usage:
  python collect_papers.py 50 agent self-evolution
  python collect_papers.py 30 multi-agent
  python collect_papers.py 100 "self-evolving world model"
"""
import os, sys, time, json, argparse

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int, nargs="?", default=30,
                        help="Number of papers to fetch (default 30)")
    parser.add_argument("topic", nargs="?", default="self-evolving agent",
                        help="Search topic (default: 'self-evolving agent')")
    parser.add_argument("--save-to", default="upgrades/collected_papers.json",
                        help="Output file path")
    args = parser.parse_args()

    print(f"Fetching {args.count} arxiv papers on '{args.topic}'...")
    print(f"Saving to: {args.save_to}")

    # Step 1: bulk arxiv fetch
    from src.research import search_arxiv
    from src.config import load_config
    cfg = load_config("config.yaml")
    # Override keywords for the bulk fetch
    cfg.research.keywords = [args.topic] + list(cfg.research.keywords or [])
    cfg.research.max_results = args.count

    t0 = time.time()
    try:
        papers = search_arxiv(cfg.research)
        print(f"Fetched {len(papers)} papers in {time.time()-t0:.1f}s")
    except Exception as e:
        print(f"arxiv fetch failed: {e}")
        return 1

    if not papers:
        print("No papers fetched.  Aborting.")
        return 1

    # Step 2: LLM filter to score relevance
    print(f"\nLLM filtering {len(papers)} papers for relevance to 'self-evolving agent'...")
    from src.llm import LLMConfig, chat
    cfg_llm = LLMConfig.from_env()
    print(f"Using model: {cfg_llm.model}, base: {cfg_llm.base_url}")

    scored = []
    for i, p in enumerate(papers):
        # Build a small prompt: title + abstract
        prompt = f"""Rate this paper's relevance to "self-evolving agent / LLM improves its own code / autonomous bootstrap" on a scale 0-10.

Title: {p.title}
Abstract: {(p.abstract or '')[:500]}

Reply with ONLY a single number 0-10. Higher = more relevant. No explanation."""
        try:
            t1 = time.time()
            r = chat(
                messages=[{"role": "user", "content": prompt}],
                config=cfg_llm,
            )
            elapsed = time.time() - t1
            # Parse first number from content
            import re
            match = re.search(r"\d+", r.content or "")
            score = int(match.group()) if match else 0
            print(f"  [{i+1}/{len(papers)}] {p.arxiv_id} score={score} ({elapsed:.1f}s): {p.title[:60]}")
            scored.append({
                "arxiv_id": p.arxiv_id,
                "title": p.title,
                "abstract": p.abstract,
                "authors": p.authors,
                "published": p.published,
                "categories": p.categories,
                "relevance_score": score,
            })
        except Exception as e:
            print(f"  [{i+1}/{len(papers)}] {p.arxiv_id} ERROR: {e}")

    # Sort by score descending
    scored.sort(key=lambda x: x["relevance_score"], reverse=True)
    print(f"\nTop 10 papers by relevance:")
    for p in scored[:10]:
        print(f"  {p['relevance_score']:>2}/10 {p['arxiv_id']} {p['title'][:60]}")

    # Save
    out = {
        "topic": args.topic,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_fetched": len(papers),
        "total_scored": len(scored),
        "top_score": scored[0]["relevance_score"] if scored else 0,
        "papers": scored,
    }
    with open(args.save_to, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {args.save_to}")
    print(f"Next: pipeline will pick from this list (modify run_1round.py / run_stable.py to read it)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
