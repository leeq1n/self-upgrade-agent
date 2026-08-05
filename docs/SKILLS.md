L0: Skill framework — auto-discovered patches with lifecycle metadata.
Per LITERATURE SkillOpt paper + user 2026-07-11 push next.
Last P20-verified: 2026-07-11

# Skills
> L0: Skills registered for this project.  Load when: looking for available skills.

Reusable patterns discovered from auto-committed LLM patches.  Per
[LITERATURE_DETAIL.md SkillOpt entry](LITERATURE_DETAIL.md#skillopt-paper)
and your vision (TODO #6 "skill lifecycle v3.2.0").

## Layered structure (per P20 progressive disclosure)

- **L0 (this file)**: what skills are + lifecycle stages
- **L1 (planned `docs/SKILLS_INDEX.md`)**: list of active skills by topic
- **L2 (per-skill `upgrades/skills/<id>.md`)**: detailed skill entry

## Discovery (auto-pipeline)

1. LLM KEPT patch → `auto-commit` runs → `upgrades/auto-patches/<date>-<hash>.patch`
2. **NEW (this commit)**: `upgrades/auto-patches/<date>-<hash>.meta.json` paired
3. Meta has: `status: "candidate"`, `applied_count: 0`, `success_count: 0`,
   `paper_id`, `target_module`, `tests_passed`.

## Lifecycle (per LITERATURE SkillOpt)

```
[discover] -> candidate (status="candidate")
                |
                v  (applied_count >= N + success_rate > 0.5)
            active (status="active")
                |
                v  (success_rate drops below threshold, or archived manually)
            archived (status="archived")
```

State transition rules (per SkillOpt paper):
- `candidate` → `active`: `applied_count >= 3` AND `success_count / applied_count > 0.6`
- `active` → `archived`: `success_count / applied_count < 0.3` (over last 5 applies)
- `archived` is terminal (manual re-evaluation only)

## Apply (future, v3.2.0)

For LLM to **reuse** a skill instead of inventing from scratch:

```
patch_path = upgrades/skills/<id>.patch   # promoted bundle
apply_patch(patch_path, target_module)    # existing v2_apply pipeline
on success: meta.applied_count += 1; success_count += 1
on failure: meta.success_count += 0; consider demotion
```

## Review (planned, v3.2.x)

- human-readable diff vs current state
- compare with newest paper insights (per LITERATURE updates)
- suggest "promote / demote / archive" actions

## Current state (per this commit, 2026-07-11)

- 2 successful sibling `[auto]` commits (`278cee9` + `4c99443`)
- Pre-existing bundles in `upgrades/auto-patches/` (no .meta.json yet — pre-meta)
- **NEW**: future auto-commits will write `*.meta.json` per LITERATURE SkillOpt pattern

## Forward-looking (planned)

- `promote_skill()` helper: scan candidates, apply retention rules
- Auto-promote on `--auto-commit` (apply rules after each successful commit)
- Daily-loop integrates: scan candidates, apply high-success ones to next rounds

Per 奥卡姆 (P7): each step is its own logical commit.  Started
with `write_skill_meta` (impl + meta file format).  Lifecycle
promotion is **separate** future commit.

Per LITERATURE Self-Harness paper (companion): "interface layer"
between patches and reuse.  This file IS that interface layer.

See also:
- [PRINCIPLES_DETAIL.md P19 (data flow observability)](PRINCIPLES_DETAIL.md#p19)
- [LITERATURE_DETAIL.md SkillOpt entry](LITERATURE_DETAIL.md#skillopt-paper)
