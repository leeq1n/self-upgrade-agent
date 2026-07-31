# Acceptance Capability Enhancement — 2026-07-30

> **Trigger**: User 2026-07-30 priority order: planning first, then
> acceptance, then tasks. This doc ships after PLANNING_FRAMEWORK.md.
>
> **Layer**: ACCEPTANCE_PROTOCOL.md is in project layer. This doc
> enhances it with concrete acceptance tools + criteria.
>
> **Purpose**: Make acceptance a first-class capability, not
> an afterthought.

## 1. What acceptance capability means

Per user: "验收能力修复" = acceptance capability needs fixing.
Three parts:
1. **Tools** — scripts that verify (existing: self_health_check, cross_repo_audit)
2. **Criteria** — what to verify against (existing: P-14, M-n, etc.)
3. **Process** — how to run acceptance (existing: 3-phase protocol)

This doc adds the missing pieces: **criteria catalog + acceptance runner**.

## 2. Acceptance criteria catalog (per 真搜 + 真凭据)

### 2.1 Pre-existing criteria (from SUA conventions)

| Criterion | Tool | Layer |
|---|---|---|
| P-14 self-contained mandate | string pattern check | project |
| Q1 cross-repo pollution | cross_repo_audit.py | project |
| Commit-msg P-n cite | commit-msg hook | core |
| pytest passes | pytest | project |
| Hook syntax valid | bash -n | core |

### 2.2 New criteria (added per this round)

| Criterion | Tool | Verification |
|---|---|---|
| **Cross-refs valid** | `validate_links.py` (new) | All `[text](path)` in *.md resolve |
| **File structure integrity** | `validate_structure.py` (new) | All critical paths exist |
| **Token budget** | `token_budget.py` (new) | Large files > 100KB flagged |
| **3-layer markers** | string pattern | **LAYER** marker in 3 main docs |
| **LAYER marker present** | string pattern | All new project-layer docs have LAYER |
| **PLAN before SHIP** | meta-pattern | PLAN_<DATE>.md exists before code |
| **Plan → accept criteria → ship order** | temporal | git log shows plan commits precede code |

## 3. New acceptance tools (to be shipped in Phase 3)

### 3.1 `validate_links.py`

```python
"""Validate markdown cross-references in *.md files."""
import re
from pathlib import Path

def validate_links(root):
    broken = []
    for f in root.rglob("*.md"):
        if ".git" in f.parts:
            continue
        content = f.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
            link = m.group(2)
            if link.startswith("http") or link.startswith("#"):
                continue
            target = (f.parent / link) if not link.startswith("/") else Path(link.lstrip("/"))
            if not target.exists():
                broken.append((str(f.relative_to(root)), link, m.group(1)))
    return broken
```

### 3.2 `validate_structure.py`

```python
"""Validate file structure matches expected layout."""
from pathlib import Path

CRITICAL_PATHS = [
    "AGENTS.md", "AGENTS_DETAIL.md", "CHANGELOG.md",
    "core-layer/AGENTS_CORE.md",
    "core-layer/PLANNING_FRAMEWORK.md",
    "core-layer/ACCEPTANCE_FRAMEWORK.md",
    "docs/ACCEPTANCE_PROTOCOL.md",
    "docs/PLANS/",  # directory
    "hooks/commit-msg", "hooks/pre-commit", "hooks/prepare-commit-msg",
    ".hermes/scripts/self_health_check.py",
    ".hermes/scripts/cross_repo_audit.py",
    ".hermes/hook_principles.json",
    "LICENSE", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
    "README.md", ".gitattributes",
]

def validate_structure(root):
    missing = [p for p in CRITICAL_PATHS if not (root / p).exists()]
    return missing
```

### 3.3 `token_budget.py`

```python
"""Check for large files that may exceed token budget."""
from pathlib import Path

SIZE_BUDGETS = {
    "*.md": 50_000,  # 50KB
    "*.py": 30_000,  # 30KB
    "*.sh": 10_000,  # 10KB
}

def check_token_budget(root):
    warnings = []
    for pattern, limit in SIZE_BUDGETS.items():
        for f in root.rglob(pattern):
            if ".git" in f.parts:
                continue
            size = f.stat().st_size
            if size > limit:
                warnings.append((str(f.relative_to(root)), size, limit))
    return warnings
```

### 3.4 `run_acceptance.sh` (single entrypoint)

```bash
#!/usr/bin/env bash
# Run all acceptance checks + produce report.
set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "===SUA Acceptance v2.19.0==="
echo "Date: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "HEAD: $(git rev-parse HEAD)"
echo ""

# Run all checks
echo "--- self_health_check ---"
python .hermes/scripts/self_health_check.py || true
echo ""

echo "--- cross_repo_audit ---"
python .hermes/scripts/cross_repo_audit.py || true
echo ""

echo "--- validate_links ---"
python .hermes/scripts/validate_links.py || true
echo ""

echo "--- validate_structure ---"
python .hermes/scripts/validate_structure.py || true
echo ""

echo "--- token_budget ---"
python .hermes/scripts/token_budget.py || true
echo ""

echo "--- pytest ---"
python -m pytest tests/test_cross_repo_audit.py || true
echo ""

echo "===End==="
```

## 4. Acceptance report (per state, ephemeral, user layer)

Each acceptance run produces:

```
~/.config/sua/acceptance/ACCEPTANCE_<DATE>_<SHA>.md
```

This file:
- Captures state at acceptance
- Records all check results
- Categorizes findings (BLOCKER / MAJOR / MINOR / INFO)
- Recommends next action (FIX / REPLAN / SHIP)

## 5. Layer mapping (per user 哪层 question)

| Acceptance piece | Layer | Why |
|---|---|---|
| `validate_links.py` etc. | **核心层** (`.hermes/scripts/`) | Audit enforcement |
| `run_acceptance.sh` | **核心层** (`.hermes/scripts/`) | Single entrypoint |
| ACCEPTANCE_PROTOCOL.md | **项目层** (`docs/`) | Per-project protocol |
| Acceptance reports | **用户层** (`~/.config/sua/acceptance/`) | Per-state ephemeral |
| Acceptance criteria | **项目层** (`docs/ACCEPTANCE_PROTOCOL.md`) | Per-project spec |

## 6. Acceptance 4-phase process (per ATDD)

```
Phase 1: ACCEPTANCE (run run_acceptance.sh)
   ↓
Phase 2: ANALYZE (categorize findings by severity)
   ↓
Phase 3: FIX (apply fixes)
   ↓
Phase 4: RE-ACCEPT (run run_acceptance.sh again)
```

This is **identical** to planning framework structure. Both planning
and acceptance are thinking-capability cycles.

## 7. Migration plan (from current state)

Current state: PROJECT_ACCEPTANCE_<DATE>.md docs in `docs/` (project layer)
should be in user layer (per v2.17.0 + v2.18.0 PLAN).

Migration:
1. Create `~/.config/sua/acceptance/` (user layer dir)
2. Move `docs/PROJECT_ACCEPTANCE_2026-07-30.md` → user layer
3. Move `docs/BROKEN_REFS_AUDIT_2026-07-30.md` → user layer (was audit report)
4. Update acceptance tools to write to user layer by default

## 8. References

- ATDD (Acceptance Test-Driven Development)
- 3 Amigos Sessions
- M-n 32 Guardrail #1 (real verify before claim)
- M-n 36 pre-release audit
- P-14 self-contained mandate
- P-17 no fabricate
- core-layer/PLANNING_FRAMEWORK.md (the planning framework)
- docs/ACCEPTANCE_PROTOCOL.md (the existing protocol)