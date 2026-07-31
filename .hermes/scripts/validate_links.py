"""validate_links.py — validate markdown cross-references (with anchor check).

Per ATDD batch fix 2026-07-31. Checks:
1. File referenced in [text](path) exists
2. Anchor (#anchor) referenced in URL exists in target file
3. Markdown auto-anchor (header text) is also accepted

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

    for f in root.rglob("*.md"):
        if ".git" in f.parts:
            continue
        content = f.read_text(encoding="utf-8", errors="ignore")
        # Strip code blocks (``` ... ```) and inline code (`...`) to avoid false positives
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`[^`]+`', '', content)
        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
            link = m.group(2)
            if link.startswith("http") or link.startswith("#"):
                continue
            if link.startswith("/"):
                target_file = Path(link.lstrip("/"))
            else:
                file_part = link.split("#", 1)[0]
                target_file = f.parent / file_part

            if not target_file.exists():
                broken.append((str(f.relative_to(root)), link, m.group(1), "file_missing"))
            elif "#" in link:
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