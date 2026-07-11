"""Tests for skill dashboard (per v3.2.0 dashboard sub-task).

Per LITERATURE Signal-to-Fix:
- Dashboard is observability tool
- Per P14 docs stay current

Per 自上而下/分治:
- Big: skill lifecycle v3.2.0
- Sub-task 1-3 done (metadata + promotion + archive)
- Sub-task 4 (this): dashboard

Per P18: regression tests required.
"""
import json
from pathlib import Path

import pytest

from src.skill_dashboard import (
    list_skill_metas,
    summarize_skills,
    render_dashboard,
)


class TestSkillDashboard:
    """Per SKILLS.md spec: dashboard for skill lifecycle observability."""

    def test_summarize_skills_empty(self, tmp_path):
        """summarize_skills: empty dir -> 0 total."""
        result = summarize_skills(tmp_path)
        assert result["total"] == 0
        assert result["by_status"] == {}
        assert result["by_target"] == {}

    def test_summarize_skills_with_metas(self, tmp_path):
        """summarize_skills: counts per status + per target."""
        metas = [
            {"status": "candidate", "target_module": "core/X"},
            {"status": "active", "target_module": "core/Y"},
            {"status": "active", "target_module": "core/Y"},
            {"status": "archived", "target_module": "core/Z"},
        ]
        for i, m in enumerate(metas):
            (tmp_path / f"s{i}.meta.json").write_text(
                json.dumps(m), encoding="utf-8")
        result = summarize_skills(tmp_path)
        assert result["total"] == 4
        assert result["by_status"]["active"] == 2
        assert result["by_status"]["candidate"] == 1
        assert result["by_status"]["archived"] == 1
        assert result["by_target"]["core/Y"] == 2

    def test_render_dashboard_text_format(self, tmp_path):
        """render_dashboard: text format shows sections."""
        meta = {"status": "active", "target_module": "core/planner.py"}
        (tmp_path / "s0.meta.json").write_text(json.dumps(meta),
                                                encoding="utf-8")
        output = render_dashboard(upgrades_dir=tmp_path,
                                  state_path=tmp_path / "state.json",
                                  output_format="text")
        assert "=== Skill Dashboard ===" in output
        assert "Total skills: 1" in output
        assert "By status:" in output
        assert "active: 1" in output
        assert "core/planner.py" in output
        assert "=== State ===" in output

    def test_render_dashboard_json_format(self, tmp_path):
        """render_dashboard: json format returns dict."""
        meta = {"status": "candidate", "target_module": "core/X"}
        (tmp_path / "s0.meta.json").write_text(json.dumps(meta),
                                                encoding="utf-8")
        output = render_dashboard(upgrades_dir=tmp_path,
                                  state_path=tmp_path / "state.json",
                                  output_format="json")
        assert isinstance(output, dict)
        assert "skills" in output
        assert "state" in output
        assert output["skills"]["total"] == 1
        assert output["skills"]["by_status"]["candidate"] == 1

    def test_render_dashboard_no_state(self, tmp_path):
        """render_dashboard: missing state.json -> graceful."""
        meta = {"status": "active", "target_module": "core/Z"}
        (tmp_path / "s0.meta.json").write_text(json.dumps(meta),
                                                encoding="utf-8")
        output = render_dashboard(upgrades_dir=tmp_path,
                                  state_path=tmp_path / "missing.json",
                                  output_format="text")
        assert "=== Skill Dashboard ===" in output
        assert "Total skills: 1" in output
        # State should show defaults
        assert "last_round_index: None" in output
        assert "rounds_persisted: 0" in output

    def test_dashboard_empty_dirs(self, tmp_path):
        """render_dashboard: no skills + no state -> empty dashboard."""
        output = render_dashboard(upgrades_dir=tmp_path,
                                  state_path=tmp_path / "missing.json",
                                  output_format="text")
        assert "Total skills: 0" in output
        assert "last_round_index: None" in output

    def test_dashboard_top_targets_limited(self, tmp_path):
            """render_dashboard: by_target sorted, top 10 only."""
            # 20 different targets (more than 10 to ensure truncation)
            for i in range(20):
                meta = {"status": "active", "target_module": f"core/M{i:02d}"}
                (tmp_path / f"s{i}.meta.json").write_text(
                    json.dumps(meta), encoding="utf-8")
            output = render_dashboard(upgrades_dir=tmp_path,
                                      state_path=tmp_path / "missing.json",
                                      output_format="text")
            # First 10 (M00..M09) should be displayed
            for i in range(10):
                assert f"core/M{i:02d}" in output
            # Last 10 (M10..M19) should NOT be displayed (truncated)
            for i in range(10, 20):
                assert f"core/M{i:02d}" not in output
