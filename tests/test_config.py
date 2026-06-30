"""Tests for src/config.py"""
import pytest
import sys, os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import Config, load_config

SAMPLE_YAML = """
research:
  keywords:
    - "test keyword"
  max_papers_per_query: 5

evaluate:
  trials_per_test: 10
"""

def test_defaults_are_sensible():
    """Config should have reasonable defaults for all fields."""
    config = Config()
    assert config.research.max_papers_per_query == 10
    assert config.research.lookback_days == 90
    assert config.filter.min_abstract_score == 6.0
    assert config.filter.min_applicability_score == 5.0
    assert config.filter.min_novelty_score == 5.0
    assert config.filter.max_papers_to_consider == 5
    assert config.implement.max_attempts == 3
    assert config.implement.validate_before_install is True
    assert config.evaluate.trials_per_test == 3
    assert config.evaluate.timeout_seconds == 120
    assert config.decide.min_success_rate_delta == 0.05
    assert config.decide.max_cost_increase_ratio == 1.2
    assert config.pipeline.max_upgrades_per_cycle == 1
    assert config.pipeline.log_level == "INFO"
    assert config.database.path == "upgrades/history.db"

def test_load_config_from_yaml():
    """YAML values should override defaults."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        f.write(SAMPLE_YAML)
        f.flush()
        config = load_config(f.name)
        path = f.name
    os.unlink(path)
    assert "test keyword" in config.research.keywords
    assert config.research.max_papers_per_query == 5
    assert config.evaluate.trials_per_test == 10

def test_load_config_missing_file_returns_defaults():
    """Missing config file should not error — return defaults."""
    config = load_config("/tmp/nonexistent_file_xyz.yaml")
    assert config.research.max_papers_per_query == 10

def test_load_config_empty_yaml_returns_defaults():
    """Empty YAML should return defaults unchanged."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
        f.write("")
        f.flush()
        config = load_config(f.name)
        path = f.name
    os.unlink(path)
    assert config.research.max_papers_per_query == 10
    assert config.decide.min_success_rate_delta == 0.05
