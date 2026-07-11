"""Skill promotion logic (per LITERATURE SkillOpt paper, skill lifecycle step 2/3).

Per LITERATURE SkillOpt paper:
- Skills = reusable patterns from LLM patches
- Lifecycle: candidate -> active -> archived
- Auto-discovery: LLM KEPT patches -> 'skill candidates' -> review -> commit
- Auto-promote: 3-factor activation score (success_count, applied_count, recency)

Per self-upgrade-agent SKILLS.md:
- status: candidate (initial) -> active (after promote_skill)
- promotion criteria: success_rate >= threshold (default 0.7) AND applied >= min_apps (default 1)
- archive: success_rate < archive_threshold (default 0.3) OR superseded

Per 自上而下/分治 (user 2026-07-11 meta-principle):
- Big task: skill lifecycle v3.2.0
- Sub-task 1 (done, commit e65ba25): skill metadata (write_skill_meta)
- Sub-task 2 (this): skill promotion (promote_skill)
- Sub-task 3 (future): skill archive + retention

Per P23 doc-first: SKILLS.md spec exists; impl follows.
Per P18 (failure -> regression test): must have tests.
"""
import json
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path


UPGRADES_DIR = Path(__file__).parent.parent / "upgrades" / "auto-patches"


def list_skill_metas(upgrades_dir=None):
    """List all skill meta.json files in upgrades/auto-patches/.

    Returns list of (meta_path, meta_dict) tuples.
    """
    d = Path(upgrades_dir) if upgrades_dir else UPGRADES_DIR
    if not d.exists():
        return []
    out = []
    for p in sorted(d.glob("*.meta.json")):
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                meta = json.loads(f.read())
            out.append((p, meta))
        except (json.JSONDecodeError, OSError):
            continue
    return out


def compute_activation_score(meta, now_ts=None):
    """Compute activation score per LITERATURE SkillOpt 3-factor model.

    Per SkillOpt paper: activation = success_rate * recency_weight

    Args:
        meta: skill meta dict (with success_count, applied_count, etc.)
        now_ts: current timestamp (default: real time)

    Returns: float in [0, 1]
    """
    if now_ts is None:
        now_ts = time.time()
    success = meta.get("success_count", 0)
    applied = meta.get("applied_count", 0)
    if applied == 0:
        # New skill, no history yet
        return 0.5  # neutral
    success_rate = success / applied
    # Recency weight: how recent is the last activity?
    last_used = meta.get("last_used_ts", meta.get("timestamp", now_ts))
    age_days = (now_ts - last_used) / 86400
    recency_weight = max(0.0, 1.0 - age_days / 30)  # decay over 30 days
    # 3-factor: success_rate (50%) + recency (30%) + sample_size (20%)
    sample_factor = min(1.0, applied / 5)  # saturate at 5+ applies
    return 0.5 * success_rate + 0.3 * recency_weight + 0.2 * sample_factor


def should_promote(meta, threshold=0.7, min_apps=1, now_ts=None):
    """Decide whether to promote a skill from 'candidate' to 'active'.

    Per LITERATURE SkillOpt paper: promotion criteria.
    Default: activation >= 0.7 AND applied_count >= 1.

    Returns: bool
    """
    if meta.get("status") != "candidate":
        return False  # already promoted or archived
    applied = meta.get("applied_count", 0)
    if applied < min_apps:
        return False
    score = compute_activation_score(meta, now_ts)
    return score >= threshold


def should_archive(meta, archive_threshold=0.3, now_ts=None):
    """Decide whether to archive a skill (move active -> archived).

    Per SKILLS.md: archive if success_rate < archive_threshold
    OR superseded by newer skill on same target.

    Returns: bool
    """
    if meta.get("status") != "active":
        return False
    success = meta.get("success_count", 0)
    applied = meta.get("applied_count", 0)
    if applied == 0:
        return False
    return (success / applied) < archive_threshold


def promote_skill(meta_path, meta, threshold=0.7, min_apps=1, now_ts=None):
    """Promote a single skill from candidate -> active.

    Per LITERATURE SkillOpt paper + SKILLS.md spec:
    Updates status, adds promotion_ts.
    Returns True if promoted, False otherwise.
    """
    if not should_promote(meta, threshold, min_apps, now_ts):
        return False
    meta["status"] = "active"
    meta["promoted_at"] = now_ts or time.time()
    meta["activation_score"] = compute_activation_score(meta, now_ts)
    _save_meta(meta_path, meta)
    return True


def archive_skill(meta_path, meta, archive_threshold=0.3, now_ts=None):
    """Archive a single skill (active -> archived)."""
    if not should_archive(meta, archive_threshold, now_ts):
        return False
    meta["status"] = "archived"
    meta["archived_at"] = now_ts or time.time()
    _save_meta(meta_path, meta)
    return True


def _save_meta(meta_path, meta):
    """Save updated meta back to disk."""
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def run_promotion_cycle(upgrades_dir=None, threshold=0.7,
                        min_apps=1, archive_threshold=0.3, now_ts=None):
    """Run full promotion + archive cycle on all skill metas.

    Per LITERATURE Signal-to-Fix: bulk apply at end of cycle.
    Returns dict with counts.
    """
    metas = list_skill_metas(upgrades_dir)
    promoted = 0
    archived = 0
    skipped = 0
    for path, meta in metas:
        status = meta.get("status", "candidate")
        if status == "candidate":
            if promote_skill(path, meta, threshold, min_apps, now_ts):
                promoted += 1
            else:
                skipped += 1
        elif status == "active":
            if archive_skill(path, meta, archive_threshold, now_ts):
                archived += 1
        else:
            skipped += 1
    return {
        "promoted": promoted,
        "archived": archived,
        "skipped": skipped,
        "total": len(metas),
    }


def main():
    """CLI entry: run skill promotion cycle."""
    import argparse
    ap = argparse.ArgumentParser(prog="skill-promote")
    ap.add_argument("--threshold", type=float, default=0.7,
                    help="Activation score threshold for promotion")
    ap.add_argument("--min-apps", type=int, default=1,
                    help="Min applied_count for promotion")
    ap.add_argument("--archive-threshold", type=float, default=0.3,
                    help="Success rate threshold for archiving")
    args = ap.parse_args()

    result = run_promotion_cycle(
        threshold=args.threshold,
        min_apps=args.min_apps,
        archive_threshold=args.archive_threshold,
    )
    print(f"Promotion cycle: {result}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

def should_supersede(old_meta, new_meta):
    """Check if new_meta supersedes old_meta (per SKILLS.md).

    Per SKILLS.md: 'archive if superseded by newer skill on same target'.
    Returns True if both target same module AND new_meta is newer.
    """
    if not old_meta or not new_meta:
        return False
    if old_meta.get("target_module") != new_meta.get("target_module"):
        return False
    old_ts = old_meta.get("promoted_at", old_meta.get("timestamp", 0))
    new_ts = new_meta.get("promoted_at", new_meta.get("timestamp", 0))
    return new_ts > old_ts


def supersede_skill(old_meta_path, old_meta, new_meta):
    """Mark old skill as superseded (active -> superseded).

    Per SKILLS.md: 'archive if superseded by newer skill on same target'.
    """
    if not should_supersede(old_meta, new_meta):
        return False
    old_meta["status"] = "superseded"
    old_meta["superseded_at"] = time.time()
    old_meta["superseded_by"] = new_meta.get("id", "unknown")
    _save_meta(old_meta_path, old_meta)
    return True


def retention_cleanup(upgrades_dir=None, archive_max_days=90, now_ts=None):
    """Auto-delete superseded/archived skills older than threshold.

    Per SKILLS.md: retention rule (don't keep dead skills forever).
    Returns dict with cleanup counts.
    """
    if now_ts is None:
        now_ts = time.time()
    metas = list_skill_metas(upgrades_dir)
    deleted = 0
    kept = 0
    for path, meta in metas:
        status = meta.get("status")
        if status not in ("archived", "superseded"):
            kept += 1
            continue
        # Use archived_at / superseded_at if present, else promoted_at
        decision_ts = meta.get("archived_at") or meta.get("superseded_at")                       or meta.get("promoted_at") or meta.get("timestamp")
        if decision_ts is None:
            kept += 1
            continue
        age_days = (now_ts - decision_ts) / 86400
        if age_days > archive_max_days:
            path.unlink()
            deleted += 1
        else:
            kept += 1
    return {"deleted": deleted, "kept": kept, "total": len(metas)}
