"""Tests for code switcher / bootloader module."""
import pytest
import os
import shutil


@pytest.fixture
def clean_switcher():
    """Initialize switcher and protect core/ modules from test corruption."""
    from src.switcher import init

    init()

    # Backup core/planner.py before tests that may write to it
    planner_path = os.path.join(os.path.dirname(__file__), "..", "core", "planner.py")
    planner_bak = planner_path + ".test_bak"
    if os.path.exists(planner_path):
        with open(planner_path, "r", encoding="utf-8") as f:
            planner_original = f.read()
        shutil.copy2(planner_path, planner_bak)
    else:
        planner_original = ""

    yield

    # Restore core/planner.py
    if os.path.exists(planner_bak):
        shutil.move(planner_bak, planner_path)
    elif planner_original:
        os.makedirs(os.path.dirname(planner_path), exist_ok=True)
        with open(planner_path, "w", encoding="utf-8") as f:
            f.write(planner_original)

    # Cleanup candidate/backup dirs
    for d in ["upgrades/active", "upgrades/candidates", "upgrades/backups"]:
        dpath = os.path.join(os.path.dirname(__file__), "..", d)
        if os.path.exists(dpath):
            for f in os.listdir(dpath):
                p = os.path.join(dpath, f)
                if os.path.isdir(p):
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    try:
                        os.remove(p)
                    except PermissionError:
                        pass


def test_import_switcher():
    from src.switcher import (
        init, deploy_candidate, promote_candidate, promote_patch,
        discard_candidate, get_active_skills, rollback_active,
        rollback_patch, get_module_versions, list_backups,
    )
    assert callable(init)
    assert callable(deploy_candidate)
    assert callable(promote_patch)
    assert callable(rollback_patch)


def test_deploy_discard(clean_switcher):
    from src.switcher import deploy_candidate, discard_candidate
    code = {"function": "def f(): return 1", "test": "def t(): assert f() == 1", "module": "planner.py"}
    path = deploy_candidate("test-deploy", "# Test", code, target_module="planner.py")
    assert os.path.exists(path)
    assert os.path.exists(os.path.join(path, "code.py"))

    discard_candidate("test-deploy")
    assert not os.path.exists(path)


def test_get_module_versions(clean_switcher):
    from src.switcher import get_module_versions
    versions = get_module_versions()
    assert "planner.py" in versions
    assert versions["planner.py"]["exists"]


def test_promotion_api_stages_candidate_without_writing_core(clean_switcher):
    """Legacy promotion names remain candidate-only under P30-A3."""
    from src.switcher import (
        deploy_candidate, promote_candidate, promote_patch,
    )

    # Create candidate targeting planner.py
    code = {
        "function": "# patched planner\ndef plan_task(task, llm_call):\n    return ['step1', 'step2']",
        "test": "def test_plan(): pass",
        "module": "planner.py",
    }
    deploy_candidate("test-boot", "# Test", code, target_module="planner.py")

    # Read original planner content before the compatibility call.
    planner_path = os.path.join(os.path.dirname(__file__), "..", "core", "planner.py")
    with open(planner_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    # The old API name must not write to core/ or create a P30 acceptance.
    result = promote_patch("test-boot")
    assert result["status"] == "candidate_staged"
    assert result["target_module"] == "planner.py"
    assert result["p30_artifact_acceptance"] == "NOT_ISSUED"
    assert result["promotion_disabled"] is True

    candidate_result = promote_candidate("test-boot")
    assert candidate_result["status"] == "candidate_staged"
    assert candidate_result["p30_artifact_acceptance"] == "NOT_ISSUED"
    assert candidate_result["promotion_disabled"] is True

    # Verify core/planner.py was not changed.
    with open(planner_path, "r", encoding="utf-8") as f:
        current_content = f.read()
    assert current_content == original_content
