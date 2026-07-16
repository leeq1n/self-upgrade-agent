#!/usr/bin/env python3
r"""
.hermes/scripts/snapshot.py - Tier 1 session snapshot helper.

Per docs/TODO_SESSION_PERSISTENCE.md (proposal, codified
in commit 37 as part of implementation roadmap commit 2/5).

This is the Tier 1 (ephemeral) snapshot helper.  Snapshots
are written to ~/AppData/Local/Temp/hermes-snapshot-<topic>-<date>.md
and follow a minimum-schema YAML header + markdown body.

Public API:
  write_snapshot(topic, task, sections, ...) -> str  (returns path)
  list_snapshots(topic=None)                 -> List[Path]
  read_snapshot(path)                        -> dict  (parsed sections)

Usage from agent session:
  from hermes_scripts.snapshot import write_snapshot
  path = write_snapshot(
      topic="sua-doc-cleanup",
      task="Verify P25 lift + parent verification",
      sections={
          "Project state": "...git status...",
          "Recent commits": "...",
          "Pending TODOs": "...",
          "Decisions made": "...",
          "Open questions": "...",
          "Next action": "...",
          "See also": "...",
      },
  )

Per M-context-snapshot rule (OPERATING_RULES.md), snapshots
are created when M-context-snapshot fires (5 signals in
SWITCH_SIGNALS.md).  This helper just standardizes the
format so snapshots are discoverable + consumable.

Per P23 doc>script with nuance: this script implements
what the proposal doc already specifies.  The proposal
(doc-only) was the spec; this script is the runtime.

Per M_RULE_AUTHORING 3-condition gate: implemented because
3 snapshot files were observed (in Temp, ad-hoc created
across sessions) — satisfies P23 trigger for script
implementation.
"""
import datetime
import re
from pathlib import Path
from typing import Dict, List, Optional

# Tier 1 location per TODO_SESSION_PERSISTENCE.md
DEFAULT_TIER1_DIR = Path.home() / "AppData" / "Local" / "Temp"

# Filename pattern: hermes-snapshot-<topic>-<date>.md
FILENAME_PATTERN = re.compile(r"^hermes-snapshot-(?P<topic>[^-]+(?:-[^-]+)*)-(?P<date>\d{4}-\d{2}-\d{2})\.md$")


def _format_header(topic: str, task: str, session_id: Optional[str] = None) -> str:
    """Format the YAML front matter per the proposal's minimum schema."""
    today = datetime.date.today().isoformat()
    lines = ["---"]
    lines.append(f"topic: {topic}")
    lines.append(f"date: {today}")
    if session_id:
        lines.append(f"session_id: {session_id}")
    lines.append(f"task: {task}")
    lines.append("---")
    return "\n".join(lines)


def _format_sections(sections: Dict[str, str]) -> str:
    """Format the body sections as ## headings + content."""
    out = []
    for title, content in sections.items():
        out.append(f"## {title}")
        out.append("")
        out.append(content)
        out.append("")
    return "\n".join(out)


def write_snapshot(
    topic: str,
    task: str,
    sections: Dict[str, str],
    session_id: Optional[str] = None,
    output_dir: Path = DEFAULT_TIER1_DIR,
) -> str:
    """Write a Tier 1 snapshot file.  Returns the absolute path."""
    if not topic or not task:
        raise ValueError("topic and task are required")
    today = datetime.date.today().isoformat()
    filename = f"hermes-snapshot-{topic}-{today}.md"
    path = Path(output_dir) / filename
    content = _format_header(topic, task, session_id) + "\n\n" + _format_sections(sections)
    path.write_text(content, encoding="utf-8")
    return str(path)


def list_snapshots(topic: Optional[str] = None, output_dir: Path = DEFAULT_TIER1_DIR) -> List[Path]:
    """List Tier 1 snapshot files, optionally filtered by topic."""
    if not output_dir.exists():
        return []
    pattern = f"hermes-snapshot-{topic}-" if topic else "hermes-snapshot-"
    matches = sorted(output_dir.glob(pattern + "*.md"))
    return matches


def read_snapshot(path: Path) -> Dict[str, str]:
    """Read a snapshot file and return header + sections as a dict."""
    text = Path(path).read_text(encoding="utf-8")
    # Parse YAML front matter
    parts = text.split("---", 2)
    header = {}
    if len(parts) >= 3:
        for line in parts[1].strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                header[k.strip()] = v.strip()
    # Parse sections
    sections = {}
    body = parts[2] if len(parts) >= 3 else text
    current_title = None
    current_content = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                sections[current_title] = "\n".join(current_content).strip()
            current_title = line[3:].strip()
            current_content = []
        else:
            current_content.append(line)
    if current_title is not None:
        sections[current_title] = "\n".join(current_content).strip()
    return {"header": header, "sections": sections}


if __name__ == "__main__":
    # Smoke test: list existing snapshots
    snaps = list_snapshots()
    print(f"Found {len(snaps)} snapshot files in {DEFAULT_TIER1_DIR}")
    for s in snaps[-3:]:  # most recent 3
        print(f"  {s.name}")