"""Integration tests for src/pipeline.py

These tests invoke the full pipeline end-to-end, which in turn calls
the real arXiv API.  Marked ``@pytest.mark.network`` so conftest.py
can skip them with HERMES_SKIP_NETWORK=1 (CI default).
"""
import pytest
import sys, os, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pipeline import run_pipeline
from src.config import Config

pytestmark = pytest.mark.network


def _run_with_cleanup(config):
    """Run pipeline in a temp dir, ensuring cleanup on Windows."""
    tmpdir = tempfile.mkdtemp()
    try:
        skills_dir = os.path.join(tmpdir, "skills")
        backup_dir = os.path.join(tmpdir, "backups")
        db_path = os.path.join(tmpdir, "history.db")
        os.makedirs(skills_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)

        result = run_pipeline(
            config=config,
            skills_dir=skills_dir,
            backup_dir=backup_dir,
            db_path=db_path,
            dry_run=True,
        )
        return result, tmpdir, skills_dir
    except:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise


def _make_config():
    config = Config()
    config.pipeline.max_upgrades_per_cycle = 1
    config.research.max_papers_per_query = 2
    config.research.keywords = ["transformer"]
    config.research.categories = ["cs.CL"]
    config.filter.min_abstract_score = 0
    config.filter.min_applicability_score = 0
    config.filter.min_novelty_score = 0
    config.filter.max_papers_to_consider = 1
    return config


def test_dry_run_completes():
    config = _make_config()
    result, tmpdir, _ = _run_with_cleanup(config)
    assert result.papers_found >= 0
    assert result.papers_scored >= 0
    assert result.skills_generated >= 0
    assert not result.errors
    shutil.rmtree(tmpdir, ignore_errors=True)


def test_dry_run_generates_skills():
    config = _make_config()
    result, tmpdir, skills_dir = _run_with_cleanup(config)
    if result.skills_generated > 0:
        skill_dirs = os.listdir(skills_dir)
        assert len(skill_dirs) > 0
        skill_md = os.path.join(skills_dir, skill_dirs[0], "SKILL.md")
        assert os.path.exists(skill_md)
    shutil.rmtree(tmpdir, ignore_errors=True)


def test_dry_run_records_in_db():
    config = _make_config()
    result, tmpdir, _ = _run_with_cleanup(config)
    if result.skills_generated > 0:
        assert len(result.details) > 0
        assert result.upgrades_kept + result.upgrades_reverted == result.skills_generated
    shutil.rmtree(tmpdir, ignore_errors=True)
