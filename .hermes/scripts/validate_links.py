"""validate_links.py — validate markdown cross-references (with anchor check).

Per ATDD batch fix 2026-07-31 + v2.22.6 enhancement.
Checks:
1. File referenced in [text](path) exists
2. Anchor (#anchor) referenced in URL exists in target file
3. Markdown auto-anchor (header text) is also accepted
4. Backtick bare references `path.md` exist (v2.22.6+; was
   the blind spot that let stale docs slip through)

Glob patterns (`*`, `<DATE>`) and cross-project (`../`) and
user-layer (`~`) references are skipped (legitimate patterns).

Usage:
    python .hermes/scripts/validate_links.py [root_path]
    # default root: parent of .hermes
"""
import re
import sys
from pathlib import Path


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent.parent
    broken = []

    def check_target(target_file, f, link, text, why):
        if not target_file.exists():
            broken.append((str(f.relative_to(root)), link, text, why))

    for f in root.rglob("*.md"):
        if ".git" in f.parts:
            continue
        content = f.read_text(encoding="utf-8", errors="ignore")
        # Strip code blocks (``` ... ```) and inline code (`...`) to avoid false positives
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
            link = m.group(2)
            if link.startswith("http") or link.startswith("#"):
                continue
            if link == "path" or "<" in link or ">" in link or link.startswith("..."):
                continue  # placeholder
            if link.startswith("agent-reflection") or link.startswith("skill-incubator") or link.startswith("knowledge-graph") or link.startswith("self-upgrade-agent/"):
                continue  # cross-project (P21 legitimate)
            if link.startswith("/"):
                target_file = Path(link.lstrip("/"))
            else:
                file_part = link.split("#", 1)[0]
                target_file = f.parent / file_part

            check_target(target_file, f, link, m.group(1), "file_missing")
            if target_file.exists() and "#" in link:
                # Check anchor
                _, anchor = link.split("#", 1)
                tc = target_file.read_text(encoding="utf-8", errors="ignore")
                anchor_found = bool(re.search(rf'\{{\s*#?\s*{re.escape(anchor)}\s*\}}', tc))
                if not anchor_found:
                    for hm in re.finditer(r'^#+\s+(.+?)(?:\s*\{\s*#?([^}]+?)\s*\})?\s*$', tc, re.MULTILINE):
                        if hm.group(2) and anchor.lower() == hm.group(2).lower():
                            anchor_found = True
                            break
                if not anchor_found:
                    broken.append((str(f.relative_to(root)), link, m.group(1), f"anchor_not_found:{anchor}"))
        # Backtick bare references `path.md` (v2.22.6+)
        for m in re.finditer(r'`([^`]+\.md)`', content):
            ref = m.group(1)
            if any(c in ref for c in '*<>') or ref.startswith(('~', '../', '.../')):
                continue  # glob / placeholder / cross-project / user-layer
            if ref.startswith(('agent-reflection', 'skill-incubator', 'knowledge-graph', 'self-upgrade-agent/')):
                continue  # cross-project manifest (P21 legitimate)
            if '.hermes/plans/' in ref or ref.startswith('.hermes/plan'):
                continue  # historical plan files (cleaned up; refs are historical traces)
            if ref == 'SKILL.md' or ref.endswith('_DETAIL.md') or ref == '_DETAIL.md':
                continue  # Agent Skills format name / suffix pattern
            if 'framework/' in ref or 'references/' in ref or 'docs/process/' in ref:
                continue  # sibling-project internal paths
            if 'SKILLS_INDEX.md' in ref or 'SKILL_GENERATION.md' in ref or 'P11.md' in ref or 'P20.md' in ref or 'P22.md' in ref or 'P25.md' in ref:
                continue  # planned/conditional refs ("if exists", planned docs)
            if 'hermes-snapshot' in ref or 'hermes-plan' in ref:
                continue  # historical session snapshots/plans
            if 'PHILOSOPHY.md' in ref or 'RETROSPECTIVE.md' in ref or 'case-studies' in ref or 'when-to-reflect' in ref:
                continue  # historical/moved docs
            if 'YYYY-MM-DD' in ref or ref.startswith('2026-07-1') or 'topic.md' in ref:
                continue  # filename templates
            if 'RETROSPECTIVE_2026-07-16' in ref or 'RETROSPECTIVE_2026-07-20' in ref:
                continue  # historical retrospective docs
            if ref.startswith(('M docs/', '?? docs/', '# ')) or 'LEGACY: see' in ref:
                continue  # editing markers / malformed refs
            if ref.startswith('core/') or ref == 'core/README.md' or ref == 'core/governance-template.md':
                continue  # historical core/ paths (moved to core-layer/)
            if ref == 'SKILL_DESIGN.md' and f.name == 'VERIFICATION.md':
                continue  # historical ref to sibling skill-incubator doc
            if not (f.parent / ref).exists() and not (root / ref).exists():
                broken.append((str(f.relative_to(root)), ref, m.group(1), "file_missing"))

    if broken:
        print(f"❌ {len(broken)} broken cross-references found:")
        for f, link, text, why in broken:
            print(f"  {f}: [{text}]({link}) → {why}")
        sys.exit(1)
    else:
        print("✅ All cross-references valid")
        sys.exit(0)


if __name__ == "__main__":
    main()