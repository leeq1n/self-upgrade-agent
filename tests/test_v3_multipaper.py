"""Tests for src/v3_multipaper.py - multi-paper reader."""
import os
import sys
import tempfile

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)

from src.v3_multipaper import (
    PaperSummary,
    CatalogParseError,
    parse_literature_catalog,
    read_papers,
    paper_count,
    _infer_arxiv_id,
    DEFAULT_CATALOG,
)


# ── Unit tests for the public API ────────────────────────────────

class TestPaperSummary:
    def test_to_dict(self):
        s = PaperSummary(
            paper_arxiv_id="x",
            title="Test",
            idea="Test idea.",
            viewpoint="Test viewpoint",
            plan="Test plan",
        )
        d = s.to_dict()
        assert d["paper_arxiv_id"] == "x"
        assert d["title"] == "Test"
        assert d["idea"] == "Test idea."
        assert d["viewpoint"] == "Test viewpoint"
        assert d["plan"] == "Test plan"
        assert d["section"] == ""  # default


class TestInferArxivId:
    def test_simple_title(self):
        assert _infer_arxiv_id("Self-Harness") == "self-harness"

    def test_year_suffix(self):
        assert _infer_arxiv_id("Reflexion (2023)") == "reflexion"

    def test_dash_in_title(self):
        assert _infer_arxiv_id("Self-Improving AI Agents") == \
               "self-improving-ai-agents"

    def test_em_dash_in_title(self):
        assert _infer_arxiv_id("Reflexion — Shinn et al.") == "reflexion"

    def test_empty_title(self):
        assert _infer_arxiv_id("") == "unknown"


# ── Catalog parser tests ─────────────────────────────────────────

SAMPLE_CATALOG = """\
# LITERATURE_DETAIL — paper notes

## Reflexion — Shinn et al. 2023 (NeurIPS)

**TL;DR**: Agents reflect verbally on failure and store reflections
in episodic memory; future attempts reference the memory.

**Why we DON'T use it directly**: Our memory writes must NOT mutate
pipeline state.

**Use it for**: inspiration on "remember what went wrong".

---

## Self-Refine — Madaan et al. 2023 (NeurIPS)

**TL;DR**: Generate → feedback → refine, ~20% improvement.

**Use it for**: inspiration on the prompt-critique structure.

---

## One Step Forward, Two Steps Back

**TL;DR**: Empirical study of Self-Refine in code generation;
finds it frequently regresses.

**Why this is decisive**: If Self-Refine can corrupt working code,
we MUST NOT use it for self-improvement without an objective gate.

**Use it for**: justification text in commit messages.
"""


class TestParseLiteratureCatalog:
    def test_parse_three_papers(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(SAMPLE_CATALOG)
            path = f.name
        try:
            papers = parse_literature_catalog(path)
            assert len(papers) == 3
        finally:
            os.unlink(path)

    def test_paper_has_required_fields(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(SAMPLE_CATALOG)
            path = f.name
        try:
            papers = parse_literature_catalog(path)
            for p in papers:
                assert p.paper_arxiv_id
                assert p.title
                assert p.idea  # 1 sentence from TL;DR
                # viewpoint may be empty if no "Why" line
                # plan may be empty if no "Use it for" line
        finally:
            os.unlink(path)

    def test_idea_is_first_sentence(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(SAMPLE_CATALOG)
            path = f.name
        try:
            papers = parse_literature_catalog(path)
            reflexion = papers[0]
            assert reflexion.idea.startswith("Agents reflect verbally")
            assert reflexion.idea.endswith(".")
        finally:
            os.unlink(path)

    def test_viewpoint_and_plan_extracted(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(SAMPLE_CATALOG)
            path = f.name
        try:
            papers = parse_literature_catalog(path)
            reflexion = papers[0]
            assert "memory writes" in reflexion.viewpoint.lower()
            assert "remember what went wrong" in reflexion.plan
        finally:
            os.unlink(path)

    def test_missing_file_raises(self):
        try:
            parse_literature_catalog("/nonexistent/path.md")
            assert False, "should have raised"
        except CatalogParseError as e:
            assert "not found" in e.reason

    def test_real_catalog_exists(self):
        """The real LITERATURE_DETAIL.md in docs/ must parse."""
        papers = parse_literature_catalog(DEFAULT_CATALOG)
        assert len(papers) >= 5  # we have 11 papers
        for p in papers:
            assert p.title
            assert p.paper_arxiv_id


# ── Public read_papers() tests ───────────────────────────────────

class TestReadPapers:
    def test_returns_all_papers_by_default(self):
        """read_papers() with no ids returns the full catalog."""
        papers = read_papers()
        assert len(papers) >= 5

    def test_filters_by_ids(self):
        """read_papers(ids=[...]) returns only matching papers."""
        all_papers = read_papers()
        # Pick a real arxiv_id from the catalog
        target_id = all_papers[0].paper_arxiv_id
        papers = read_papers(ids=[target_id])
        assert len(papers) == 1
        assert papers[0].paper_arxiv_id == target_id

    def test_unknown_ids_returns_empty(self):
        papers = read_papers(ids=["not-a-real-id"])
        assert papers == []

    def test_dedup_in_query(self):
        """Duplicate ids in query are deduped (set semantics)."""
        all_papers = read_papers()
        target_id = all_papers[0].paper_arxiv_id
        papers = read_papers(ids=[target_id, target_id])
        # Set semantics: duplicates collapse
        assert len(papers) == 1
        assert papers[0].paper_arxiv_id == target_id


class TestPaperCount:
    def test_count_matches_read(self):
        count = paper_count()
        all_papers = read_papers()
        assert count == len(all_papers)