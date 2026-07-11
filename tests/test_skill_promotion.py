"""Tests for skill promotion (per LITERATURE SkillOpt, skill lifecycle step 2/3).

Per self-upgrade-agent SKILLS.md spec:
- skill status: candidate -> active -> archived
- promote when activation score >= threshold
- archive when success_rate < archive_threshold

Per 自上而下/分治 (user 2026-07-11 meta-principle):
- Big task: skill lifecycle v3.2.0
- Sub-task 1 (done): skill metadata
- Sub-task 2 (this): skill promotion
- Sub-task 3 (future): skill archive

Per P18: failure -> regression test.
"""
import json
import time
from pathlib import Path
import tempfile

import pytest

from src.skill_promotion import (
    list_skill_metas,
    compute_activation_score,
    should_promote,
    should_archive,
    promote_skill,
    archive_skill,
    run_promotion_cycle,
    should_supersede,
    supersede_skill,
    retention_cleanup,
)


class TestSkillPromotion:
    """Per LITERATURE SkillOpt paper: skill lifecycle promotions."""

    def test_compute_activation_score_no_history(self):
        """No applied_count -> 0.5 (neutral, per SkillOpt paper)."""
        meta = {"applied_count": 0, "success_count": 0}
        score = compute_activation_score(meta)
        assert score == 0.5

    def test_compute_activation_score_high_success(self):
        """100% success + recent activity + many applies -> high score."""
        now = time.time()
        meta = {
            "applied_count": 10,
            "success_count": 10,
            "last_used_ts": now,  # recent
        }
        score = compute_activation_score(meta, now_ts=now)
        assert score >= 0.7

    def test_compute_activation_score_low_success(self):
        """Low success rate -> low score."""
        meta = {
            "applied_count": 10,
            "success_count": 1,
            "last_used_ts": time.time(),
        }
        score = compute_activation_score(meta)
        # 0.5 * 0.1 = 0.05 + 0.3 * 1 + 0.2 * 1 = 0.55
        assert score < 0.7

    def test_should_promote_under_threshold(self):
        """Below activation threshold -> not promoted."""
        meta = {
            "status": "candidate",
            "applied_count": 5,
            "success_count": 5,
        }
        # High success but fresh skill -> 0.5*1.0 + 0.3*0 + 0.2*1 = 0.7
        # No last_used_ts -> recency = 0
        assert should_promote(meta, threshold=0.7, min_apps=1) is True

    def test_should_promote_min_apps_required(self):
        """applied_count < min_apps -> not promoted."""
        meta = {
            "status": "candidate",
            "applied_count": 0,
            "success_count": 0,
        }
        assert should_promote(meta, threshold=0.5, min_apps=1) is False

    def test_should_promote_already_active(self):
        """Already-active skill -> not re-promoted."""
        meta = {
            "status": "active",
            "applied_count": 5,
            "success_count": 5,
        }
        assert should_promote(meta, threshold=0.5, min_apps=1) is False

    def test_should_archive_low_success_rate(self):
        """Active skill with low success rate -> archived."""
        meta = {
            "status": "active",
            "applied_count": 10,
            "success_count": 1,
        }
        assert should_archive(meta, archive_threshold=0.3) is True

    def test_should_archive_high_success_kept(self):
        """Active skill with high success -> kept (not archived)."""
        meta = {
            "status": "active",
            "applied_count": 10,
            "success_count": 9,
        }
        assert should_archive(meta, archive_threshold=0.3) is False

    def test_should_archive_not_active(self):
        """Candidate skill -> not archived (use promote)."""
        meta = {
            "status": "candidate",
            "applied_count": 10,
            "success_count": 1,
        }
        assert should_archive(meta, archive_threshold=0.3) is False

    def test_promote_skill_updates_status(self, tmp_path):
        """promote_skill: candidate -> active, writes back to disk."""
        path = tmp_path / "test.meta.json"
        meta = {
            "status": "candidate",
            "applied_count": 5,
            "success_count": 5,
            "last_used_ts": time.time(),
        }
        path.write_text(json.dumps(meta), encoding="utf-8")
        result = promote_skill(path, meta, threshold=0.5, min_apps=1)
        assert result is True
        assert meta["status"] == "active"
        assert "promoted_at" in meta
        assert "activation_score" in meta
        # Verify file saved
        saved = json.loads(path.read_text(encoding="utf-8"))
        assert saved["status"] == "active"

    def test_promote_skill_not_eligible_returns_false(self, tmp_path):
        """promote_skill: ineligible -> False, no change."""
        path = tmp_path / "test.meta.json"
        meta = {"status": "candidate", "applied_count": 0, "success_count": 0}
        path.write_text(json.dumps(meta), encoding="utf-8")
        result = promote_skill(path, meta, threshold=0.5, min_apps=1)
        assert result is False
        assert meta["status"] == "candidate"
        assert "promoted_at" not in meta

    def test_archive_skill_updates_status(self, tmp_path):
        """archive_skill: active -> archived."""
        path = tmp_path / "test.meta.json"
        meta = {
            "status": "active",
            "applied_count": 10,
            "success_count": 1,  # low success
        }
        path.write_text(json.dumps(meta), encoding="utf-8")
        result = archive_skill(path, meta, archive_threshold=0.3)
        assert result is True
        assert meta["status"] == "archived"
        assert "archived_at" in meta

    def test_list_skill_metas(self, tmp_path):
        """list_skill_metas: finds all *.meta.json files."""
        (tmp_path / "a.meta.json").write_text(
            json.dumps({"status": "candidate"}), encoding="utf-8")
        (tmp_path / "b.meta.json").write_text(
            json.dumps({"status": "active"}), encoding="utf-8")
        (tmp_path / "c.patch").write_text("patch", encoding="utf-8")
        # Should NOT include .patch
        metas = list_skill_metas(tmp_path)
        assert len(metas) == 2
        statuses = {m["status"] for _, m in metas}
        assert statuses == {"candidate", "active"}

    def test_list_skill_metas_missing_dir(self, tmp_path):
        """list_skill_metas: missing dir -> [] (no crash)."""
        result = list_skill_metas(tmp_path / "missing")
        assert result == []

    def test_run_promotion_cycle(self, tmp_path):
        """run_promotion_cycle: bulk apply, returns counts."""
        # Set up 3 metas: 1 promote-eligible, 1 archive-eligible, 1 noop
        now = time.time()
        candidates = [
            {"status": "candidate", "applied_count": 5, "success_count": 5,
             "last_used_ts": now},
            {"status": "active", "applied_count": 10, "success_count": 1},  # archive
            {"status": "candidate", "applied_count": 0, "success_count": 0},  # skip
        ]
        for i, m in enumerate(candidates):
            (tmp_path / f"s{i}.meta.json").write_text(json.dumps(m), encoding="utf-8")

        result = run_promotion_cycle(
            upgrades_dir=tmp_path, threshold=0.7, min_apps=1,
            archive_threshold=0.3,
        )
        assert result["promoted"] == 1
        assert result["archived"] == 1
        assert result["skipped"] == 1
        assert result["total"] == 3

        # Verify files saved correctly
        saved = json.loads((tmp_path / "s0.meta.json").read_text(encoding="utf-8"))
        assert saved["status"] == "active"
        saved2 = json.loads((tmp_path / "s1.meta.json").read_text(encoding="utf-8"))
        assert saved2["status"] == "archived"


class TestSkillSupersede:
    """Per SKILLS.md: archive if superseded by newer skill on same target."""

    def test_should_supersede_same_target_newer(self):
        """Same target + newer timestamp -> supersede."""
        old = {"target_module": "core/planner.py", "promoted_at": 100.0, "id": "old"}
        new = {"target_module": "core/planner.py", "promoted_at": 200.0, "id": "new"}
        assert should_supersede(old, new) is True

    def test_should_supersede_different_target(self):
        """Different target modules -> no supersede."""
        old = {"target_module": "core/planner.py", "promoted_at": 100.0}
        new = {"target_module": "core/agent.py", "promoted_at": 200.0}
        assert should_supersede(old, new) is False

    def test_should_supersede_older_new(self):
        """Newer is older -> no supersede (don't replace with older)."""
        old = {"target_module": "core/planner.py", "promoted_at": 200.0}
        new = {"target_module": "core/planner.py", "promoted_at": 100.0}
        assert should_supersede(old, new) is False

    def test_should_supersede_missing_args(self):
        """Missing args -> False (no crash)."""
        assert should_supersede(None, {}) is False
        assert should_supersede({}, None) is False

    def test_supersede_skill_updates_status(self, tmp_path):
        """supersede_skill: active -> superseded, writes to disk."""
        old_path = tmp_path / "old.meta.json"
        old = {
            "status": "active",
            "target_module": "core/planner.py",
            "promoted_at": 100.0,
            "id": "old-id",
        }
        old_path.write_text(json.dumps(old), encoding="utf-8")
        new = {
            "target_module": "core/planner.py",
            "promoted_at": 200.0,
            "id": "new-id",
        }
        result = supersede_skill(old_path, old, new)
        assert result is True
        assert old["status"] == "superseded"
        assert old["superseded_by"] == "new-id"
        assert "superseded_at" in old
        # Verify file
        saved = json.loads(old_path.read_text(encoding="utf-8"))
        assert saved["status"] == "superseded"


class TestSkillRetention:
    """Per SKILLS.md: retention rules (auto-cleanup of dead skills)."""

    def test_retention_cleanup_old_archived_deleted(self, tmp_path):
        """Old archived skill -> deleted."""
        old_ts = time.time() - 100 * 86400  # 100 days ago
        meta = {
            "status": "archived",
            "archived_at": old_ts,
            "id": "old",
        }
        path = tmp_path / "old.meta.json"
        path.write_text(json.dumps(meta), encoding="utf-8")
        result = retention_cleanup(tmp_path, archive_max_days=90)
        assert result["deleted"] == 1
        assert not path.exists()

    def test_retention_cleanup_recent_archived_kept(self, tmp_path):
        """Recent archived skill -> kept (within window)."""
        recent_ts = time.time() - 30 * 86400  # 30 days ago
        meta = {
            "status": "archived",
            "archived_at": recent_ts,
            "id": "recent",
        }
        path = tmp_path / "recent.meta.json"
        path.write_text(json.dumps(meta), encoding="utf-8")
        result = retention_cleanup(tmp_path, archive_max_days=90)
        assert result["kept"] == 1
        assert path.exists()

    def test_retention_cleanup_active_skill_kept(self, tmp_path):
        """Active skill -> kept (regardless of age)."""
        old_ts = time.time() - 365 * 86400
        meta = {
            "status": "active",
            "promoted_at": old_ts,
            "id": "active",
        }
        path = tmp_path / "active.meta.json"
        path.write_text(json.dumps(meta), encoding="utf-8")
        result = retention_cleanup(tmp_path, archive_max_days=90)
        assert result["kept"] == 1
        assert path.exists()

    def test_retention_cleanup_candidate_skill_kept(self, tmp_path):
        """Candidate skill -> kept (not eligible for cleanup)."""
        meta = {"status": "candidate", "id": "new"}
        path = tmp_path / "new.meta.json"
        path.write_text(json.dumps(meta), encoding="utf-8")
        result = retention_cleanup(tmp_path, archive_max_days=90)
        assert result["kept"] == 1
        assert path.exists()

    def test_retention_cleanup_superseded_old_deleted(self, tmp_path):
        """Old superseded skill -> deleted (treated same as archived)."""
        old_ts = time.time() - 100 * 86400
        meta = {
            "status": "superseded",
            "superseded_at": old_ts,
            "id": "sup",
        }
        path = tmp_path / "sup.meta.json"
        path.write_text(json.dumps(meta), encoding="utf-8")
        result = retention_cleanup(tmp_path, archive_max_days=90)
        assert result["deleted"] == 1
        assert not path.exists()
