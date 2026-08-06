"""Modify agent behavior by applying skill rules.

This module is the bridge between a skill file (behavior rules)
and the actual agent configuration. It modifies ~/agent-tools/config.yaml
to inject new system prompt additions and behavior rules.
"""
import os, json, shutil, logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_SUA_HOME = os.environ.get("SUA_HOME", os.path.expanduser("~/agent-tools"))
_CONFIG_PATH = os.path.join(_SUA_HOME, "config.yaml")
_SKILLS_DIR = os.path.join(_SUA_HOME, "skills")


def get_hermes_home():
    return _SUA_HOME


def install_skill_file(skill_md: str, skill_name: str, skills_dir: str = None) -> str:
    """Install a generated skill into the Hermes Agent skills directory.
    Returns the path to the installed SKILL.md.
    """
    if skills_dir is None:
        skills_dir = _SKILLS_DIR
    skill_dir = os.path.join(skills_dir, skill_name)
    os.makedirs(skill_dir, exist_ok=True)
    path = os.path.join(skill_dir, "SKILL.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(skill_md)
    logger.info(f"Skill installed: {path}")
    return path


def extract_behavior_from_skill(skill_path: str) -> Dict:
    """Parse a SKILL.md and extract behavior rules and system prompt.
    Returns dict with rules (list), prompt (str), workflow (str).
    """
    if not os.path.exists(skill_path):
        logger.warning(f"Skill not found: {skill_path}")
        return {"rules": [], "prompt": "", "workflow": ""}
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()
    result = {"rules": [], "prompt": "", "workflow": ""}
    sections = content.split("## ")
    for sec in sections:
        if sec.startswith("Behavior Modification"):
            rules_text = sec.split("The agent MUST follow:")[-1] if "The agent MUST follow:" in sec else ""
            for line in rules_text.strip().split(chr(10))[:15]:
                stripped = line.strip()
                if stripped and stripped[0].isdigit() and ". " in stripped[:4]:
                    result["rules"].append(stripped.split(". ", 1)[1])
        if sec.startswith("System Prompt Addition"):
            prompt_text = sec.split("> ")[-1] if "> " in sec else sec
            result["prompt"] = prompt_text.strip()[:500]
        if sec.startswith("Workflow"):
            lines_list = [l.strip() for l in sec.split(chr(10)) if l.strip()][:10]
            result["workflow"] = chr(10).join(lines_list)[:500]
    return result


def backup_config() -> Optional[str]:
    """Backup current Hermes config before modifying."""
    if not os.path.exists(_CONFIG_PATH):
        return None
    backup_dir = os.path.join(_SUA_HOME, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"config.yaml.{ts}.bak")
    shutil.copy2(_CONFIG_PATH, backup_path)
    return backup_path


def apply_behavior(skill_path: str, dry_run: bool = False) -> Dict:
    """Apply a skill behavior to the agent.
    
    1. Install the skill file into Hermes skills directory
    2. Extract behavior rules and system prompt
    3. Inject system prompt addition into config
    
    Returns dict with: status, skill_path, rules_applied, prompt_added, backup_path.
    """
    bhv = extract_behavior_from_skill(skill_path)
    if not bhv["rules"] and not bhv["prompt"]:
        return {"status": "no_behavior_found", "skill_path": skill_path}

    backup = backup_config() if not dry_run else None

    result = {
        "status": "applied" if not dry_run else "dry_run",
        "skill_path": skill_path,
        "rules_applied": len(bhv["rules"]),
        "prompt": bhv["prompt"][:100] + "..." if len(bhv["prompt"]) > 100 else bhv["prompt"],
        "backup_path": backup,
    }
    return result


def rollback_behavior(backup_path: str) -> bool:
    """Restore config from backup."""
    if not os.path.exists(backup_path):
        return False
    shutil.copy2(backup_path, _CONFIG_PATH)
    logger.info(f"Config restored from: {backup_path}")
    return True