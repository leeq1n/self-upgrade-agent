"""Tests for cross_repo_audit.py (Q3 principle-collapse prevention).

These tests use tmp_path to construct synthetic sibling repos. No real
filesystem is mutated outside tmp_path.
"""
import json
import subprocess
import sys
from pathlib import Path

# Import the script module
SUA_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUA_ROOT / ".hermes" / "scripts"))
import cross_repo_audit  # noqa: E402


def _make_sibling(tmp_path, *, with_adapter=True, mirror_files=None,
                  internal_refs=False, has_submodule=False,
                  submodule_uses_tag=False):
    """Build a synthetic sibling repo under tmp_path."""
    sibling = tmp_path / "fake-sibling"
    sibling.mkdir()
    if with_adapter:
        (sibling / "adapter").mkdir()
        (sibling / "adapter" / "main.py").write_text("# stub")
    for dirname, nfiles in (mirror_files or {}).items():
        (sibling / dirname).mkdir()
        for i in range(nfiles):
            (sibling / dirname / f"f{i}.md").write_text("# stub")
    if internal_refs:
        (sibling / "AGENTS.md").write_text(
            "Per user message 2026-07-16: do X.\n"
            "Per c95: do Y.\n"
            "See AGENTS_DETAIL.md for details.\n"
        )
        (sibling / "README.md").write_text(
            "Per c42: install.\n"
        )
    else:
        (sibling / "AGENTS.md").write_text("# Adapter contract (clean)\n")
        (sibling / "README.md").write_text("# Fake sibling\n")
    if has_submodule:
        if submodule_uses_tag:
            submodule_text = (
                "[submodule \".sua\"]\n"
                "\tpath = .sua\n"
                "\turl = https://example.com/sua.git\n"
                "\ttag = v2.5.3\n"
            )
        else:
            submodule_text = (
                "[submodule \".sua\"]\n"
                "\tpath = .sua\n"
                "\turl = https://example.com/sua.git\n"
                "\tbranch = main\n"
            )
        (sibling / ".gitmodules").write_text(submodule_text)
    return sibling


def test_has_adapter_passes_with_adapter_dir(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=True)
    failures = cross_repo_audit.audit_sibling_has_adapter(sibling)
    assert failures == []


def test_has_adapter_fails_when_adapter_missing(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=False)
    # Remove AGENTS.md requirement; just test adapter check
    failures = cross_repo_audit.audit_sibling_has_adapter(sibling)
    assert any("adapter" in f for f in failures)


def test_has_adapter_fails_when_adapter_empty(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=True)
    # Empty the adapter dir
    for f in (sibling / "adapter").iterdir():
        f.unlink()
    failures = cross_repo_audit.audit_sibling_has_adapter(sibling)
    assert any("empty" in f for f in failures)


def test_no_mirror_passes_for_clean_sibling(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=True)
    failures = cross_repo_audit.audit_sibling_no_mirror(sibling)
    assert failures == []


def test_no_mirror_fails_for_docs_pollution(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=True,
                            mirror_files={"docs": 10})
    failures = cross_repo_audit.audit_sibling_no_mirror(sibling)
    assert any("docs/" in f for f in failures)


def test_no_mirror_fails_for_src_pollution(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=True,
                            mirror_files={"src": 50})
    failures = cross_repo_audit.audit_sibling_no_mirror(sibling)
    assert any("src/" in f for f in failures)


def test_self_contained_passes_for_clean_files(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=True, internal_refs=False)
    failures = cross_repo_audit.audit_sibling_self_contained(sibling)
    assert failures == []


def test_self_contained_fails_for_per_user_message(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=True, internal_refs=True)
    failures = cross_repo_audit.audit_sibling_self_contained(sibling)
    assert any("per-user-message" in f for f in failures)


def test_self_contained_fails_for_agents_detail_ref(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=True, internal_refs=True)
    failures = cross_repo_audit.audit_sibling_self_contained(sibling)
    assert any("AGENTS_DETAIL" in f for f in failures)


def test_submodule_pinned_passes_for_tag_pinning(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=True,
                            has_submodule=True, submodule_uses_tag=True)
    failures = cross_repo_audit.audit_sibling_submodule_pinned(sibling)
    assert failures == []


def test_submodule_pinned_fails_for_branch_pinning(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=True,
                            has_submodule=True, submodule_uses_tag=False)
    failures = cross_repo_audit.audit_sibling_submodule_pinned(sibling)
    assert any("branch" in f for f in failures)


def test_audit_one_sibling_returns_full_report(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=False,
                            mirror_files={"docs": 20}, internal_refs=True)
    result = cross_repo_audit.audit_one_sibling(sibling)
    assert result["path"] == str(sibling)
    assert result["exists"] is True
    assert len(result["checks"]["has_adapter"]) > 0
    assert len(result["checks"]["no_mirror_files"]) > 0
    assert len(result["checks"]["agencies_md_self_contained"]) > 0


def test_cli_runs_and_returns_json(tmp_path):
    """End-to-end CLI test: pass synthetic sibling via --sibling flag."""
    sibling = _make_sibling(tmp_path, with_adapter=True)
    proc = subprocess.run(
        ["python", str(SUA_ROOT / ".hermes" / "scripts" / "cross_repo_audit.py"),
         "--sibling", str(sibling)],
        capture_output=True, text=True, timeout=15,
    )
    assert proc.returncode == 0, f"unexpected exit: {proc.returncode}\n{proc.stderr}"
    output = json.loads(proc.stdout)
    assert output["audit"] == "cross_repo_audit"
    assert output["siblings_audited"] == 1
    assert output["verdict"] in ("PASS", "FAIL")


def test_cli_strict_mode_exits_nonzero_on_failure(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=False)
    proc = subprocess.run(
        ["python", str(SUA_ROOT / ".hermes" / "scripts" / "cross_repo_audit.py"),
         "--sibling", str(sibling), "--strict"],
        capture_output=True, text=True, timeout=15,
    )
    assert proc.returncode != 0, "expected nonzero exit in --strict on failure"


def test_cli_advisory_mode_exits_zero_despite_failures(tmp_path):
    sibling = _make_sibling(tmp_path, with_adapter=False)
    proc = subprocess.run(
        ["python", str(SUA_ROOT / ".hermes" / "scripts" / "cross_repo_audit.py"),
         "--sibling", str(sibling)],
        capture_output=True, text=True, timeout=15,
    )
    assert proc.returncode == 0, "advisory mode should not block"
    output = json.loads(proc.stdout)
    assert output["verdict"] == "FAIL"
    assert output["total_failures"] > 0