"""Tests for code switcher module."""
import pytest, os, shutil

@pytest.fixture
def clean_switcher():
    from src.switcher import init
    init()
    yield
    # Cleanup candidate dirs
    for d in ["upgrades/active", "upgrades/candidates", "upgrades/backups"]:
        if os.path.exists(d):
            for f in os.listdir(d):
                p = os.path.join(d, f)
                if os.path.isdir(p):
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    os.remove(p)

def test_import_switcher():
    from src.switcher import (
        init, deploy_candidate, promote_candidate, 
        discard_candidate, get_active_skills, rollback_active
    )
    assert callable(init)
    assert callable(deploy_candidate)

def test_deploy_discard(clean_switcher):
    from src.switcher import deploy_candidate, discard_candidate
    code = {"function": "def f(): return 1", "test": "def t(): assert f() == 1"}
    path = deploy_candidate("test-skill", "# Test", code)
    assert os.path.exists(path)
    assert os.path.exists(os.path.join(path, "code.py"))
    
    discard_candidate("test-skill")
    assert not os.path.exists(path)

def test_promote_and_rollback(clean_switcher):
    from src.switcher import deploy_candidate, promote_candidate, get_active_skills, rollback_active
    code = {"function": "def f(): pass", "test": "def t(): pass"}
    deploy_candidate("test-skill", "# Test", code)
    promote_candidate("test-skill")
    
    active = get_active_skills()
    assert "test-skill" in active
    
    rollback_active("test-skill")
    active_after = get_active_skills()
    assert "test-skill" not in active_after
