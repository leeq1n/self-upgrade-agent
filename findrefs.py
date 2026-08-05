# -*- coding: utf-8 -*-
"""Find remaining references to deleted docs in surviving files."""
import pathlib

DELETED = [
    "RETROSPECTIVE_2026-07-16.md", "RETROSPECTIVE_2026-07-20.md",
    "AUDIT_PHASE_1_2_3_2026_07_16.md", "DECISIONS_2026_07_11_12.md",
    "DECISION_RECORD_2026-07-31.md", "FINAL_ACCEPTANCE_2026-07-31.md",
    "PROJECT_ACCEPTANCE_2026-07-30.md", "VALUE_ASSESSMENT_2026-07-30.md",
    "POST_SEARCH_EVALUATION_2026-07-30.md", "THREE_LAYER_DECISION_2026-07-30.md",
    "IMPLEMENTATION_PLAN_2026-07-30.md", "BROKEN_REFS_AUDIT_2026-07-30.md",
    "GRAPH_TO_SKILL_DESIGN.md", "GRAPH_TO_SKILL_DESIGN_DETAIL.md",
    "GRAPH_TO_SKILL_ANALYSIS.md", "GRAPH_TO_SKILL_ANALYSIS_DETAIL.md",
    "PLAN_TOPDOWN_REORG.md", "PLAN_TOPDOWN_REORG_DETAIL.md",
    "PROJECT_TOPDOWN_AUDIT.md", "PROJECT_TOPDOWN_AUDIT_DETAIL.md",
    "MERGE_EVAL.md", "MERGE_EVAL_DETAIL.md",
    "SELF_AUDIT_P20.md", "SELF_AUDIT_P20_DETAIL.md",
    "REFLECTION_STEP_BACK.md", "REFLECTION_STEP_BACK_DETAIL.md",
    "LEGACY_STATUS.md", "OBSERVATIONS.md", "OBSERVATIONS_DETAIL.md",
    "TODO_KNOWLEDGE_GRAPH.md", "TODO_KNOWLEDGE_LIFECYCLE.md",
    "_REGRESSION_NOTES.md", "HISTORY.md", "ISSUES.md", "PROJECT_BRIEF.md",
    "RELEASE_NOTES_v2.3.0.md", "ACCEPTANCE_REPORT.md",
]

files = []
for base in [".", "docs", "core-layer", "hooks"]:
    for p in pathlib.Path(base).rglob("*.md"):
        files.append(p)
files += list(pathlib.Path(".hermes/scripts").glob("*.py"))
files += list(pathlib.Path(".hermes/scripts").glob("*.sh"))

for p in files:
    try:
        s = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    hits = [d for d in DELETED if d in s]
    if hits:
        print(f"### {p}")
        for d in hits:
            for i, line in enumerate(s.splitlines(), 1):
                if d in line:
                    print(f"  L{i}: {line.strip()[:110]}")
