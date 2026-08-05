# -*- coding: utf-8 -*-
"""Build a reference map for candidate-to-delete docs.

For each candidate file, list which other files reference it by name.
"""
import pathlib
import re

CANDIDATES = [
    "docs/RETROSPECTIVE_2026-07-16.md",
    "docs/RETROSPECTIVE_2026-07-20.md",
    "docs/AUDIT_PHASE_1_2_3_2026_07_16.md",
    "docs/DECISIONS_2026_07_11_12.md",
    "docs/DECISION_RECORD_2026-07-31.md",
    "docs/FINAL_ACCEPTANCE_2026-07-31.md",
    "docs/PROJECT_ACCEPTANCE_2026-07-30.md",
    "docs/VALUE_ASSESSMENT_2026-07-30.md",
    "docs/POST_SEARCH_EVALUATION_2026-07-30.md",
    "docs/THREE_LAYER_DECISION_2026-07-30.md",
    "docs/IMPLEMENTATION_PLAN_2026-07-30.md",
    "docs/BROKEN_REFS_AUDIT_2026-07-30.md",
    "docs/GRAPH_TO_SKILL_DESIGN.md",
    "docs/GRAPH_TO_SKILL_DESIGN_DETAIL.md",
    "docs/GRAPH_TO_SKILL_ANALYSIS.md",
    "docs/GRAPH_TO_SKILL_ANALYSIS_DETAIL.md",
    "docs/PLAN_TOPDOWN_REORG.md",
    "docs/PLAN_TOPDOWN_REORG_DETAIL.md",
    "docs/PROJECT_TOPDOWN_AUDIT.md",
    "docs/PROJECT_TOPDOWN_AUDIT_DETAIL.md",
    "docs/MERGE_EVAL.md",
    "docs/MERGE_EVAL_DETAIL.md",
    "docs/SELF_AUDIT_P20.md",
    "docs/SELF_AUDIT_P20_DETAIL.md",
    "docs/REFLECTION_STEP_BACK.md",
    "docs/REFLECTION_STEP_BACK_DETAIL.md",
    "docs/LEGACY_STATUS.md",
    "docs/OBSERVATIONS.md",
    "docs/OBSERVATIONS_DETAIL.md",
    "docs/TODO_KNOWLEDGE_GRAPH.md",
    "docs/TODO_KNOWLEDGE_LIFECYCLE.md",
    "docs/TODO_SESSION_PERSISTENCE.md",
    "docs/TODO_SESSION_PERSISTENCE_DETAIL.md",
    "docs/_REGRESSION_NOTES.md",
    "HISTORY.md",
    "ISSUES.md",
    "PROJECT_BRIEF.md",
    "RELEASE_NOTES_v2.3.0.md",
    "ACCEPTANCE_REPORT.md",
]

ALL_MD = []
for base in [".", "docs", "core-layer", "hooks"]:
    for p in pathlib.Path(base).rglob("*.md"):
        if ".git" in str(p) or "node_modules" in str(p):
            continue
        ALL_MD.append(p)
# also scripts that reference doc paths
ALL_FILES = list(ALL_MD) + list(pathlib.Path(".hermes/scripts").glob("*.py")) + list(pathlib.Path(".hermes/scripts").glob("*.sh"))

for cand in CANDIDATES:
    name = pathlib.Path(cand).name
    refs = []
    for p in ALL_FILES:
        try:
            s = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if name in s:
            refs.append(str(p))
    print(f"{cand}  <- {refs}")
