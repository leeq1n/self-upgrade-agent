"""Regression tests for prompt hygiene and readable user-facing responses.

Per the 2026-07-20 simplification (M-n 35 + P7 Occam): this
file is intentionally minimal.  It bans a *very specific*
phrase family — the role labels followed by an English noun
that has been observed to prime a decoder repetition loop
in agent output.  Other uses of that noun as a normal
English word (e.g., in literary quotes, technical docs
about round-based reasoning, etc.) are NOT banned.

The exact banned phrases are listed verbatim in the BANNED
tuple below.  The test file itself is the only file that
holds them as literals — structural necessity (you cannot
ban a phrase without naming it).  Every other prompt
surface is audited and must be free of those literals.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT_SURFACES = tuple(
    str(path.relative_to(ROOT))
    for path in ROOT.rglob("*")
    if path.is_file()
    and ".git" not in path.parts
    and path.suffix.lower() in {".md", ".py", ".sh", ".bash", ".yaml", ".yml", ".toml"}
)
# Phrases banned from prompt surfaces (the test file itself is exempt
# because the docstring references them by literal; an explicit
# self-check audit catches that failure mode if needed).
BANNED = (
    "你 turn", "我 turn", "user turn", "assistant turn",
)
TEST_FILE = "tests/test_prompt_hygiene.py"


def _scan(paths, ext=None) -> list[str]:
    """Return list of '<path>:<line>: <text>' for each banned hit."""
    offenders: list[str] = []
    for relative_path in paths:
        if relative_path.replace("\\", "/") == TEST_FILE:
            continue
        p = ROOT / relative_path
        if not p.exists():
            continue
        if ext is not None and p.suffix.lower() not in ext:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for bad in BANNED:
                if bad in line:
                    offenders.append(f"{relative_path}:{line_number}: {line.strip()[:80]}")
    return offenders


def test_prompt_surfaces_avoid_role_phrase():
    """Banned role phrases must not appear in any prompt surface."""
    offenders = _scan(PROMPT_SURFACES)
    assert not offenders, "Banned role phrases in prompt surfaces:\n" + "\n".join(offenders)


def test_core_rules_make_reasoning_checklists_internal_by_default():
    """Normal replies should expose conclusions, not every reasoning scaffold."""
    core = (ROOT / "core-layer/AGENTS_CORE.md").read_text(encoding="utf-8")
    assert "Reasoning checklists are internal by default" in core
    assert "discard the draft and rewrite" in core


def test_agents_index_points_to_live_per_task_rule_source():
    """The cache split must not hide full rules behind invalid references."""
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    detail = (ROOT / "AGENTS_DETAIL.md").read_text(encoding="utf-8")
    assert "**Full content**: in `core-layer/AGENTS_CORE.md`" not in agents
    assert "git show HEAD:AGENTS.md" not in agents
    for heading in (
        '## "继续" protocol',
        '## "学习一下" protocol',
        '## "主动修改 skill"',
        "## Iterative thinking",
        "## Recursive test-verify",
        "## Skill context cleanliness",
        "## Multi-perspective audit angles",
        "## Task-done-notify reminder",
        "## Post-completion verification suggestion",
        "## Operating rules",
        "## Recent cross-project sync",
    ):
        assert heading in detail, f"Missing live rule source: {heading}"


SIBLING_PROJECTS = (
    "agent-reflection-skill",
    "agent-reflection-skill-v1.0.0",
    "skill-incubator",
    "knowledge-graph-seed",
)
SIBLING_ROOT = ROOT.parent
SIBLING_EXT = {".md", ".py", ".sh", ".yaml", ".yml", ".toml", ".txt"}


def test_sibling_projects_avoid_role_phrase():
    """Sibling projects must not reintroduce the banned role phrase."""
    paths = []
    for project in SIBLING_PROJECTS:
        project_root = SIBLING_ROOT / project
        if not project_root.exists():
            continue
        for p in project_root.rglob("*"):
            if not p.is_file() or ".git" in p.parts:
                continue
            if p.suffix.lower() not in SIBLING_EXT:
                continue
            try:
                rel = str(p.relative_to(SIBLING_ROOT / project))
            except ValueError:
                continue
            paths.append(f"{project}/{rel}")
    offenders = _scan(paths, ext=SIBLING_EXT)
    assert not offenders, "Banned role phrases in sibling projects:\n" + "\n".join(offenders)