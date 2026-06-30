"""Tests for src/skillgen.py"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.skillgen import generate_skill_md, validate_skill, save_skill, backup_skill, extract_behavior
from src.research import Paper


SAMPLE_PAPER = Paper(
    arxiv_id="2402.03300",
    title="Improving Agent Planning with Tree Search",
    authors="A. Author, B. Researcher",
    published="2024-02-03",
    abstract="We propose a novel tree-search method that improves agent "
             "planning by 15% on standard benchmarks by exploring multiple "
             "paths and pruning low-probability branches early.",
    categories="cs.AI, cs.LG",
)


class TestBehaviorExtraction:
    def test_behavior_has_required_fields(self):
        """extract_behavior should return a dict with rules, prompt, workflow."""
        bhv = extract_behavior(SAMPLE_PAPER, use_llm=False)
        assert "rules" in bhv
        assert "prompt" in bhv
        assert "workflow" in bhv
        assert isinstance(bhv["rules"], list)
        assert len(bhv["rules"]) > 0
        assert len(bhv["prompt"]) > 50
        assert len(bhv["workflow"]) > 50

    def test_template_rules_mention_paper_topic(self):
        bhv = extract_behavior(SAMPLE_PAPER, use_llm=False)
        rules_text = " ".join(bhv["rules"]).lower()
        assert "approach" in rules_text


class TestSkillGeneration:
    def test_skill_has_frontmatter(self):
        md = generate_skill_md(SAMPLE_PAPER, use_llm=False)
        assert md.strip().startswith("---")
        assert "name:" in md
        assert "description:" in md

    def test_skill_has_behavior_section(self):
        md = generate_skill_md(SAMPLE_PAPER, use_llm=False)
        assert "## Behavior Modification" in md
        assert "## Workflow" in md

    def test_skill_includes_paper_id(self):
        md = generate_skill_md(SAMPLE_PAPER, use_llm=False)
        assert "2402-03300" in md or "2402.03300" in md


class TestValidation:
    def test_validate_rejects_empty(self):
        errors = validate_skill("")
        assert len(errors) > 0

    def test_validate_accepts_valid(self):
        md = generate_skill_md(SAMPLE_PAPER, use_llm=False)
        errors = validate_skill(md)
        assert len(errors) == 0


@pytest.mark.llm
class TestLLMGeneration:
    def test_llm_generates_actionable_rules(self):
        md = generate_skill_md(SAMPLE_PAPER, use_llm=True)
        assert "Behavior Modification" in md
        assert "explore" in md.lower() or "plan" in md.lower() or "approach" in md.lower()

    def test_llm_behavior_passes_validation(self):
        md = generate_skill_md(SAMPLE_PAPER, use_llm=True)
        errors = validate_skill(md)
        assert len(errors) == 0, f"LLM skill invalid: {errors}"


class TestFileOperations:
    def test_save_and_backup(self, tmp_path):
        md = generate_skill_md(SAMPLE_PAPER, use_llm=False)
        skills_dir = str(tmp_path / "skills")
        backup_dir = str(tmp_path / "snapshots")
        path = save_skill(md, "save-test", skills_dir)
        assert os.path.exists(path)
        backup = backup_skill(path, backup_dir)
        assert backup is not None
        assert os.path.exists(backup)
