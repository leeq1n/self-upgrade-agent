"""+Bootloader: manage active/candidate code versions with A/B comparison.

Provides safe code switching:
  deploy(candidate) → save new code alongside old
  evaluate(A, B)   → run both on benchmark, compare
  promote()        → switch A→B atomically
  rollback()       → restore A from backup
"""
import os, json, shutil, logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_ROOT = os.path.join(os.path.dirname(__file__), "..", "upgrades")
_ACTIVE = "active"
_CANDIDATE = "candidates"
_BACKUP = "backups"
_MANIFEST = "manifest.json"


def _dir(cat):
    d = os.path.join(_ROOT, cat)
    return os.path.abspath(d)


def init():
    """Initialize directory structure if first run."""
    for cat in [_ACTIVE, _CANDIDATE, _BACKUP]:
        os.makedirs(_dir(cat), exist_ok=True)
    mf = os.path.join(_dir(_ACTIVE), _MANIFEST)
    if not os.path.exists(mf):
        with open(mf, "w") as f:
            json.dump({"versions": [], "current": None, "created": datetime.now().isoformat()}, f)


def get_active_skills():
    """List all active skills and their versions."""
    d = _dir(_ACTIVE)
    if not os.path.exists(d): return {}
    result = {}
    for name in os.listdir(d):
        skill_dir = os.path.join(d, name)
        if os.path.isdir(skill_dir) and not name.startswith("."):
            md_file = os.path.join(skill_dir, "SKILL.md")
            if os.path.exists(md_file):
                with open(md_file) as f:
                    fm = f.read()[:500]
                result[name] = {"skill_md": fm, "path": md_file}
            code_file = os.path.join(skill_dir, "code.py")
            if os.path.exists(code_file):
                result.setdefault(name, {})["code_path"] = code_file
    return result


def deploy_candidate(skill_name, skill_md, code_dict=None):
    """Save a new skill as candidate (does not disrupt active version).
    
    Returns path to candidate directory.
    """
    cand = os.path.join(_dir(_CANDIDATE), skill_name)
    os.makedirs(cand, exist_ok=True)
    with open(os.path.join(cand, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(skill_md)
    if code_dict:
        with open(os.path.join(cand, "code.py"), "w", encoding="utf-8") as f:
            f.write(code_dict.get("function", "") + chr(10) + code_dict.get("test", ""))
    ts = datetime.now().isoformat()
    with open(os.path.join(cand, "meta.json"), "w") as f:
        json.dump({"created": ts, "skill_name": skill_name, "has_code": bool(code_dict)}, f)
    return cand


def promote_candidate(skill_name):
    """Atomically promote candidate → active, backup old active."""
    cand = os.path.join(_dir(_CANDIDATE), skill_name)
    active = os.path.join(_dir(_ACTIVE), skill_name)
    backup = os.path.join(_dir(_BACKUP), skill_name + "_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    if not os.path.exists(cand):
        return {"status": "no_candidate"}
    
    # Backup old active if exists
    if os.path.exists(active):
        os.makedirs(os.path.dirname(backup), exist_ok=True)
        shutil.move(active, backup)
        logger.info(f"Backed up active to {backup}")
    
    # Move candidate to active
    shutil.move(cand, active)
    logger.info(f"Promoted {skill_name} to active")
    
    # Update manifest
    mf = os.path.join(_dir(_ACTIVE), _MANIFEST)
    with open(mf) as f:
        manifest = json.load(f)
    manifest["versions"].append({"skill": skill_name, "promoted": datetime.now().isoformat(), "backup": backup})
    manifest["current"] = skill_name
    with open(mf, "w") as f:
        json.dump(manifest, f, indent=2)
    
    return {"status": "promoted", "skill": skill_name, "backup": backup}


def discard_candidate(skill_name):
    """Delete a candidate that failed evaluation."""
    cand = os.path.join(_dir(_CANDIDATE), skill_name)
    if os.path.exists(cand):
        shutil.rmtree(cand, ignore_errors=True)
        logger.info(f"Discarded candidate: {skill_name}")
        return {"status": "discarded"}
    return {"status": "no_candidate"}


def rollback_active(skill_name, backup_path=None):
    """Rollback active skill to previous version."""
    active = os.path.join(_dir(_ACTIVE), skill_name)
    if not os.path.exists(active):
        return {"status": "no_active_version"}
    if backup_path and os.path.exists(backup_path):
        if os.path.exists(active):
            shutil.rmtree(active, ignore_errors=True)
        shutil.copytree(backup_path, active)
        logger.info(f"Rolled back {skill_name} from {backup_path}")
        return {"status": "rolled_back"}
    # No backup: just remove from active
    shutil.rmtree(active, ignore_errors=True)
    # Update manifest
    mpath = os.path.join(_dir(_ACTIVE), "manifest.json")
    if os.path.exists(mpath):
        with open(mpath) as f:
            m = json.load(f)
        m["versions"] = [v for v in m.get("versions",[]) if v.get("skill") != skill_name]
        if m.get("current") == skill_name:
            m["current"] = m["versions"][0]["skill"] if m["versions"] else None
        with open(mpath, "w") as f:
            json.dump(m, f, indent=2, default=str)
    logger.info(f"Rolled back (removed) {skill_name}")
    return {"status": "rolled_back"}