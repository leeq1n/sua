"""Bootloader: 安全管理核心模块的代码版本。

[LEGACY API] — candidate staging and rollback surface; terminal promotion is disabled by P30-A3.

Operations:
  deploy_candidate  → 保存候选代码到 upgrades/candidates/
  promote_patch     → 兼容入口：只标记候选已暂存，不写入 core/
  rollback_patch    → 从备份恢复 core/{target_module}
  get_module_versions → 查看当前各核心模块版本

目录结构:
  upgrades/
  ├── candidates/{name}/      # 候选补丁（等待评估）
  │   ├── code.py
  │   ├── meta.json
  │   └── ...metadata
  ├── backups/                 # 核心模块备份
  │   ├── planner_{timestamp}.bak
  │   └── ...
  └── manifest.json            # 当前活跃版本清单
"""
import os
import json
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_ROOT = os.path.join(os.path.dirname(__file__), "..", "upgrades")
_CANDIDATE = "candidates"
_BACKUP = "backups"
_MANIFEST = "manifest.json"

# Core modules that can be patched
CORE_MODULES = {
    "planner.py": os.path.join(os.path.dirname(__file__), "..", "core", "planner.py"),
    "agent.py": os.path.join(os.path.dirname(__file__), "..", "core", "agent.py"),
    "tools.py": os.path.join(os.path.dirname(__file__), "..", "core", "tools.py"),
}


def _dir(cat: str) -> str:
    """Resolve absolute path to upgrades subdirectory."""
    d = os.path.join(_ROOT, cat)
    return os.path.abspath(d)


def init():
    """Initialize directory structure if first run."""
    for cat in [_CANDIDATE, _BACKUP]:
        os.makedirs(_dir(cat), exist_ok=True)
    mf = os.path.join(_ROOT, _MANIFEST)
    if not os.path.exists(mf):
        with open(mf, "w") as f:
            json.dump({
                "created": datetime.now().isoformat(),
                "modules": {},
                "history": [],
            }, f, indent=2)


def _read_manifest() -> dict:
    mf = os.path.join(_ROOT, _MANIFEST)
    if not os.path.exists(mf):
        init()
    with open(mf) as f:
        return json.load(f)


def _write_manifest(data: dict):
    """Atomically write manifest.json.

    v1.8.1 (P0-1 fix): concurrent daemons used to corrupt this file because
    ``open(mf, "w")`` is non-atomic at the OS level — two threads doing
    read-modify-write would interleave their writes and produce invalid
    JSON.  Fixed by writing to ``manifest.json.tmp`` (which is owned by a
    single writer thanks to ``os.replace`` being atomic), fsyncing the data
    to disk before the rename, and finally ``os.replace``-ing into place.
    If the process dies between write and rename, the original manifest
    is untouched and the .tmp is a leftover we can garbage-collect on the
    next read.
    """
    mf = os.path.join(_ROOT, _MANIFEST)
    os.makedirs(os.path.dirname(mf), exist_ok=True)
    tmp = mf + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, mf)
    except Exception:
        # Best-effort cleanup of the orphan .tmp file; never block the
        # caller if cleanup itself fails.
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        raise


def _backup_module(target_module: str) -> Optional[str]:
    """Backup a core module file to upgrades/backups/. Returns backup path."""
    if target_module not in CORE_MODULES:
        logger.warning(f"Unknown module: {target_module}")
        return None

    src = CORE_MODULES[target_module]
    if not os.path.exists(src):
        logger.warning(f"Module not found: {src}")
        return None

    os.makedirs(_dir(_BACKUP), exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(_dir(_BACKUP), f"{target_module.replace('.py', '')}_{ts}.bak")
    shutil.copy2(src, dst)
    logger.info(f"Backed up {target_module} → {dst}")
    return dst


def _restore_module(backup_path: str, target_module: str) -> bool:
    """Restore a core module from backup."""
    if target_module not in CORE_MODULES:
        return False
    if not os.path.exists(backup_path):
        logger.warning(f"Backup not found: {backup_path}")
        return False

    dst = CORE_MODULES[target_module]
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(backup_path, dst)
    logger.info(f"Restored {target_module} from {backup_path}")
    return True


# ── Candidate management ──────────────────────────

def deploy_candidate(skill_name: str, skill_md: str = "",
                     code_dict: Optional[Dict] = None,
                     target_module: str = "planner.py") -> str:
    """Save a new patch as candidate. Returns path to candidate directory."""
    init()
    cand = os.path.join(_dir(_CANDIDATE), skill_name)
    os.makedirs(cand, exist_ok=True)

    # Save code
    if code_dict and code_dict.get("function"):
        code_path = os.path.join(cand, "code.py")
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code_dict.get("function", "") + "\n")
            f.write("# --- test ---\n")
            f.write(code_dict.get("test", ""))
    else:
        code_path = None

    # Save SKILL.md if provided
    if skill_md:
        with open(os.path.join(cand, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(skill_md)

    # Metadata
    ts = datetime.now().isoformat()
    with open(os.path.join(cand, "meta.json"), "w") as f:
        json.dump({
            "created": ts,
            "skill_name": skill_name,
            "target_module": target_module,
            "has_code": bool(code_dict and code_dict.get("function")),
            "code_size": len(code_dict.get("function", "")) if code_dict else 0,
        }, f)

    return cand


def discard_candidate(skill_name: str) -> dict:
    """Delete a candidate that failed evaluation."""
    cand = os.path.join(_dir(_CANDIDATE), skill_name)
    if os.path.exists(cand):
        shutil.rmtree(cand, ignore_errors=True)
        logger.info(f"Discarded candidate: {skill_name}")
        return {"status": "discarded"}
    return {"status": "no_candidate"}


# ── Candidate staging (not P30 terminal promotion) ─────────

def stage_candidate(skill_name: str) -> dict:
    """Mark an existing candidate as staged without changing ``core/``.

    ``core/`` is an active execution surface, so writing it from a local
    candidate decision would be a material promotion path.  P30-A3 keeps
    candidate generation and retention useful while making this legacy
    promotion API explicitly nonterminal.  A separate external workflow must
    own any later canonical deployment decision.
    """
    init()
    cand = os.path.join(_dir(_CANDIDATE), skill_name)
    if not os.path.isdir(cand):
        return {"status": "no_candidate", "candidate": cand}

    meta_path = os.path.join(cand, "meta.json")
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    return {
        "status": "candidate_staged",
        "candidate": cand,
        "target_module": meta.get("target_module", "planner.py"),
        "p30_artifact_acceptance": "NOT_ISSUED",
        "p30_terminal_status": "READY FOR INDEPENDENT AUDIT",
    }

def promote_patch(skill_name: str) -> dict:
    """Compatibility alias for :func:`stage_candidate`.

    The old name must not retain a material ``candidate → core/`` promotion
    side effect.  It now returns an explicit candidate-only status.
    """
    result = stage_candidate(skill_name)
    result["legacy_api"] = "promote_patch"
    result["promotion_disabled"] = True
    return result


def promote_candidate(skill_name: str) -> dict:
    """Backward-compatible candidate-only wrapper.

    Legacy ``active/`` and ``core/`` writes are intentionally not performed;
    local keep/sandbox success is not P30 acceptance.
    """
    result = stage_candidate(skill_name)
    result["legacy_api"] = "promote_candidate"
    result["promotion_disabled"] = True
    return result


def rollback_patch(target_module: str = "planner.py",
                   backup_path: Optional[str] = None) -> dict:
    """Rollback a core module to a previous version.

    If backup_path is provided, restore that specific backup.
    Otherwise, find the latest backup for the given module.
    """
    if target_module not in CORE_MODULES:
        return {"status": "unknown_module", "target_module": target_module}

    if backup_path and os.path.exists(backup_path):
        ok = _restore_module(backup_path, target_module)
        if ok:
            # Update manifest
            manifest = _read_manifest()
            manifest["history"].append({
                "action": "rollback",
                "target_module": target_module,
                "rolled_back_at": datetime.now().isoformat(),
                "restored_from": backup_path,
            })
            _write_manifest(manifest)
            return {"status": "rolled_back", "target_module": target_module,
                    "restored_from": backup_path}

    # Find latest backup
    backup_dir = _dir(_BACKUP)
    if not os.path.exists(backup_dir):
        return {"status": "no_backups"}

    prefix = target_module.replace(".py", "")
    backups = sorted(
        [f for f in os.listdir(backup_dir) if f.startswith(prefix) and f.endswith(".bak")],
        reverse=True,
    )
    if not backups:
        return {"status": "no_backups_for_module", "target_module": target_module}

    latest = os.path.join(backup_dir, backups[0])
    ok = _restore_module(latest, target_module)
    if ok:
        manifest = _read_manifest()
        manifest["history"].append({
            "action": "rollback",
            "target_module": target_module,
            "rolled_back_at": datetime.now().isoformat(),
            "restored_from": latest,
        })
        _write_manifest(manifest)
        return {"status": "rolled_back", "target_module": target_module,
                "restored_from": latest}

    return {"status": "restore_failed", "target_module": target_module}


def rollback_active(skill_name: str, backup_path: Optional[str] = None) -> dict:
    """Backward-compatible rollback for legacy active/ directory."""
    active = os.path.join(_ROOT, "active", skill_name)
    if backup_path and os.path.exists(backup_path):
        if os.path.exists(active):
            shutil.rmtree(active, ignore_errors=True)
        shutil.copytree(backup_path, active)
        return {"status": "rolled_back"}
    if os.path.exists(active):
        shutil.rmtree(active, ignore_errors=True)
    return {"status": "rolled_back"}


def get_module_versions() -> dict:
    """Return current version info for all tracked core modules."""
    init()
    result = {}
    for name, path in CORE_MODULES.items():
        entry = {"path": os.path.abspath(path), "exists": False, "size": 0}
        if os.path.exists(path):
            entry["exists"] = True
            entry["size"] = os.path.getsize(path)
            entry["mtime"] = datetime.fromtimestamp(
                os.path.getmtime(path)).isoformat()
        result[name] = entry

    # Add manifest info
    manifest = _read_manifest()
    for module_name, info in manifest.get("modules", {}).items():
        if module_name in result:
            result[module_name]["last_promoted"] = info.get("promoted_at")
            result[module_name]["last_skill"] = info.get("skill_name")

    return result


def get_active_skills() -> dict:
    """Backward-compatible: list legacy active skills. Also show core module versions."""
    result = {}

    # Legacy active dir
    active_dir = os.path.join(_ROOT, "active")
    if os.path.exists(active_dir):
        for name in os.listdir(active_dir):
            skill_dir = os.path.join(active_dir, name)
            if os.path.isdir(skill_dir) and not name.startswith("."):
                md_file = os.path.join(skill_dir, "SKILL.md")
                if os.path.exists(md_file):
                    with open(md_file) as f:
                        fm = f.read()[:500]
                    result[name] = {"skill_md": fm, "path": md_file}
                code_file = os.path.join(skill_dir, "code.py")
                if os.path.exists(code_file):
                    result.setdefault(name, {})["code_path"] = code_file

    # Core module versions
    manifest = _read_manifest()
    for module_name, info in manifest.get("modules", {}).items():
        result[f"core/{module_name}"] = {
            "skill_md": f"Active version from {info.get('promoted_at', 'unknown')}",
            "code_path": CORE_MODULES.get(module_name, ""),
            "patched_by": info.get("skill_name", ""),
        }

    return result


def list_backups(target_module: str = None) -> List[dict]:
    """List all backups, optionally filtered by module name."""
    backup_dir = _dir(_BACKUP)
    if not os.path.exists(backup_dir):
        return []

    backups = []
    for f in sorted(os.listdir(backup_dir), reverse=True):
        if not f.endswith(".bak"):
            continue
        path = os.path.join(backup_dir, f)
        if target_module and not f.startswith(target_module.replace(".py", "")):
            continue
        backups.append({
            "filename": f,
            "path": path,
            "size": os.path.getsize(path),
            "mtime": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(),
        })
    return backups
