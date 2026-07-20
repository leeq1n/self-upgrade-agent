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
# Banned role-shorthand strings are stored as fragment concatenations
# to keep this file's source text free of literal banned strings
# (which would make its own self-referential guard trigger a false
# positive).  Each element is built by concatenating two halves; the
# runtime value is identical to the natural-language shorthand.
ROLE_TURN_SHORTHANDS = (
    "你" + " turn",
    "我" + " turn",
    "user" + " turn",
    "assistant" + " turn",
)
REPEATED_ROLE_LABELS = (
    "user" + " message user message",
    "assistant" + " response assistant response",
)
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


# Strict self-reference guard: this test file MUST NOT contain the banned
# role-shorthand in any form, even in docstrings or comments.  If you need
# to reference the banned strings (e.g., to write a new test), use the
# ROLE_TURN_SHORTHANDS tuple at the top of this file (which holds them as
# fragments, not literal strings) — or write 'ROLE_TURN_SHORTHANDS[0]'.
# This guard exists because earlier versions of this test file contained
# the banned strings in their own docstrings, which made them invisible
# to the canonical pytest pass — the test would exempt itself from
# auditing.  Per P17 honest reporting: an exempt test is no test at all.
def _self_referential_ban():
    """Return banned strings by REBUILDING them from fragments.

    Building the strings at runtime means this module's source text
    does NOT literally contain them (so source-text scans cannot
    detect false-positive hits in this file's own comments).  This
    is the placeholder pattern referenced in the file-level note
    above.
    """
    return (
        "你" + " turn",
        "我" + " turn",
        "你" + "turn",
        "我" + "turn",
        "user" + " turn",
        "assistant" + " turn",
    )


def test_test_file_does_not_self_referentially_contain_banned_strings():
    """The prompt-hygiene test must NOT exempt itself by referencing the banned strings.

    This guard prevents the failure mode where this test file contains
    a banned role-shorthand in its own docstrings / comments, then
    the canonical pytest sweep exempts 'tests/test_prompt_hygiene.py'
    from its own check.  Exempting the test would silently disable
    the hygiene gate for the rest of the project.
    """
    text = (ROOT / TEST_FILE).read_text(encoding="utf-8")
    banned = _self_referential_ban()
    hits = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for bad in banned:
            if bad in line:
                hits.append(f"{TEST_FILE}:{line_number}: banned-fragment in: {line.strip()[:80]}")
    assert not hits, (
        "Test file itself contains a banned role-shorthand.  This makes\n"
        "the hygiene gate self-referentially exempt, which is the exact\n"
        "failure mode this guard is designed to catch.  Use the\n"
        "ROLE_TURN_SHORTHANDS tuple or 'ROLE_TURN_SHORTHANDS[0]' instead\n"
        "of writing the banned string as a literal.\n"
        "Hits:\n" + "\n".join(hits)
    )

