"""Regression tests for prompt hygiene and readable user-facing responses."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT_SURFACES = tuple(
    str(path.relative_to(ROOT))
    for path in ROOT.rglob("*")
    if path.is_file()
    and ".git" not in path.parts
    and path.suffix.lower() in {".md", ".py", ".sh", ".bash", ".yaml", ".yml", ".toml"}
)
ROLE_TURN_SHORTHANDS = ("你" + " turn", "我" + " turn")
REPEATED_ROLE_LABELS = ("user message user message", "assistant response assistant response")
# The test file itself documents the banned strings; allow it to
# reference them in docstrings + assertions by name, but block any
# non-test file from containing them.
TEST_FILE = "tests/test_prompt_hygiene.py"


def test_mandatory_prompt_surfaces_avoid_role_turn_shorthand():
    """High-frequency role shorthand must not prime a decoder repetition loop.

    The test file itself is exempt (it must reference the banned
    strings to test for them) but is audited by a separate check
    via the ad-hoc verification script.
    """
    offenders: list[str] = []
    for relative_path in PROMPT_SURFACES:
        if relative_path.replace("\\", "/") == TEST_FILE:
            continue
        path = ROOT / relative_path
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(shorthand in line for shorthand in ROLE_TURN_SHORTHANDS):
                offenders.append(f"{relative_path}:{line_number}: {line.strip()}")

    assert not offenders, "Role/turn shorthand found in prompt surfaces:\n" + "\n".join(offenders)


def test_core_rules_make_reasoning_checklists_internal_by_default():
    """Normal replies should expose conclusions, not every reasoning scaffold."""
    core = (ROOT / "core-layer/AGENTS_CORE.md").read_text(encoding="utf-8")

    assert "Reasoning checklists are internal by default" in core
    assert "discard the draft and rewrite" in core


def test_prompt_surfaces_avoid_repeated_role_labels():
    """The replacement vocabulary must not recreate the same repetition hazard."""
    offenders: list[str] = []
    for relative_path in PROMPT_SURFACES:
        if relative_path.replace("\\", "/") == TEST_FILE:
            continue
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for label in REPEATED_ROLE_LABELS:
            if label in text:
                offenders.append(f"{relative_path}: {label}")

    assert not offenders, "Repeated role labels found:\n" + "\n".join(offenders)


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


def test_sibling_projects_avoid_role_turn_shorthand():
    """Siblings of SUA must not reintroduce the repetition-loop shorthand.

    The 4 hermes-root siblings share the same agent load order at
    session start, so any banned role-shorthand they contain is loaded
    into the system prompt and can prime the same decoder loop SUA
    was cleaned to avoid.  Idempotent guard: any new commit in any
    sibling that re-introduces these strings fails the gate.
    """
    offenders: list[str] = []
    for project in SIBLING_PROJECTS:
        project_root = SIBLING_ROOT / project
        if not project_root.exists():
            continue
        for path in project_root.rglob("*"):
            if not path.is_file() or ".git" in path.parts:
                continue
            if path.suffix.lower() not in SIBLING_EXT:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for line_number, line in enumerate(text.splitlines(), start=1):
                if any(shorthand in line for shorthand in ROLE_TURN_SHORTHANDS):
                    offenders.append(
                        f"{project}/{path.relative_to(project_root)}:{line_number}: {line.strip()[:80]}"
                    )
    assert not offenders, "Role/turn shorthand in sibling projects:\n" + "\n".join(offenders)

