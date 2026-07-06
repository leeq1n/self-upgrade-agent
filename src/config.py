"""Configuration loading and validation for self-upgrade agent.

[FROZEN v1.1.0] — stable dataclass schema, tested, do not modify.
"""
import yaml
from dataclasses import dataclass, field
from typing import List


@dataclass
class ResearchConfig:
    keywords: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=lambda: ["cs.AI", "cs.CL", "cs.LG"])
    max_papers_per_query: int = 10
    sort_by: str = "submittedDate"
    lookback_days: int = 90
    multi_source: bool = False   # Enable arXiv+S2+PwC+GitHub search
    arxiv_selenium_first: bool = True  # Selenium as primary, API as fallback


@dataclass
class FilterConfig:
    min_abstract_score: float = 6.0
    min_applicability_score: float = 5.0
    min_novelty_score: float = 5.0
    max_papers_to_consider: int = 5


@dataclass
class ImplementConfig:
    max_attempts: int = 3
    validate_before_install: bool = True
    backup_existing_skill: bool = True


@dataclass
class EvaluateConfig:
    mode: str = "llm"
    trials_per_test: int = 3
    timeout_seconds: int = 120


@dataclass
class DecideConfig:
    min_success_rate_delta: float = 0.05
    max_cost_increase_ratio: float = 1.2
    min_response_quality_delta: float = 0.1


@dataclass
class PipelineConfig:
    schedule: str = "manual"
    max_upgrades_per_cycle: int = 1
    require_manual_approval: bool = False
    auto_promote: bool = False
    log_level: str = "INFO"
    # v1.8.0: how often to run skill_audit (0=disabled, 1=every round, 5=every 5 rounds)
    skill_audit_every: int = 1


@dataclass
class DatabaseConfig:
    path: str = "upgrades/history.db"


@dataclass
class LifecycleConfig:
    enabled: bool = True
    max_active_skills: int = 10
    eval_interval_days: int = 7
    inactivity_days: int = 30
    min_context_budget: int = 4000


@dataclass
class Config:
    """Root config aggregating all sub-configs."""
    research: ResearchConfig = field(default_factory=ResearchConfig)
    filter: FilterConfig = field(default_factory=FilterConfig)
    implement: ImplementConfig = field(default_factory=ImplementConfig)
    evaluate: EvaluateConfig = field(default_factory=EvaluateConfig)
    decide: DecideConfig = field(default_factory=DecideConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    lifecycle: LifecycleConfig = field(default_factory=LifecycleConfig)


# Mapping of YAML paths to sub-config classes
_SECTION_MAP = {
    "research": (ResearchConfig, [
        ("keywords", "keywords", []),
        ("categories", "categories", ["cs.AI", "cs.CL", "cs.LG"]),
        ("max_papers_per_query", "max_papers_per_query", 10),
        ("sort_by", "sort_by", "submittedDate"),
        ("lookback_days", "lookback_days", 90),
    ]),
    "filter": (FilterConfig, [
        ("min_abstract_score", "min_abstract_score", 6.0),
        ("min_applicability_score", "min_applicability_score", 5.0),
        ("min_novelty_score", "min_novelty_score", 5.0),
        ("max_papers_to_consider", "max_papers_to_consider", 5),
    ]),
    "implement": (ImplementConfig, [
        ("max_attempts", "max_attempts", 3),
        ("validate_before_install", "validate_before_install", True),
        ("backup_existing_skill", "backup_existing_skill", True),
    ]),
    "evaluate": (EvaluateConfig, [
        ("trials_per_test", "trials_per_test", 3),
        ("timeout_seconds", "timeout_seconds", 120),
    ]),
    "decide": (DecideConfig, [
        ("min_success_rate_delta", "min_success_rate_delta", 0.05),
        ("max_cost_increase_ratio", "max_cost_increase_ratio", 1.2),
        ("min_response_quality_delta", "min_response_quality_delta", 0.1),
    ]),
    "pipeline": (PipelineConfig, [
        ("schedule", "schedule", "manual"),
        ("max_upgrades_per_cycle", "max_upgrades_per_cycle", 1),
        ("require_manual_approval", "require_manual_approval", False),
        ("auto_promote", "auto_promote", False),
        ("log_level", "log_level", "INFO"),
    ]),
    "database": (DatabaseConfig, [
        ("path", "path", "upgrades/history.db"),
    ]),
    "lifecycle": (LifecycleConfig, [
        ("enabled", "enabled", True),
        ("max_active_skills", "max_active_skills", 10),
        ("eval_interval_days", "eval_interval_days", 7),
        ("inactivity_days", "inactivity_days", 30),
        ("min_context_budget", "min_context_budget", 4000),
    ]),
}


def _build_subconfig(section_name: str, raw_section: dict):
    """Build a sub-config dataclass from a YAML section dict."""
    cls_cls, fields = _SECTION_MAP[section_name]
    kwargs = {}
    for yaml_key, attr_name, default in fields:
        kwargs[attr_name] = raw_section.get(yaml_key, default)
    return cls_cls(**kwargs)


def load_config(path: str = "config.yaml") -> Config:
    """Load config from YAML file, filling in defaults for missing values."""
    config = Config()

    try:
        with open(path, 'r', encoding='utf-8') as f:
            raw = yaml.safe_load(f) or {}
    except FileNotFoundError:
        return config

    for section_name in _SECTION_MAP:
        if section_name in raw:
            sub = _build_subconfig(section_name, raw[section_name])
            setattr(config, section_name, sub)

    return config
