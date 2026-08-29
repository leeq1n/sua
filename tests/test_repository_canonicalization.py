"""Regression checks for the canonical SUA repository migration."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_URL = "https://github.com/leeq1n/sua"
LEGACY_URL = "https://github.com/leeq1n/self-upgrade-agent"


def test_readme_declares_canonical_repository_and_install_path():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert CANONICAL_URL in readme
    assert "git clone https://github.com/leeq1n/sua.git .sua/" in readme
    assert "git clone https://github.com/leeq1n/self-upgrade-agent.git .sua/" not in readme


def test_legacy_url_is_only_retained_in_explicit_history():
    """Active docs/config must not bootstrap from the deprecated predecessor."""
    allowed_historical_files = {
        "CHANGELOG.md", "README.md", "tests/test_repository_canonicalization.py"
    }
    stale_hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.relative_to(ROOT).as_posix() in allowed_historical_files:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if LEGACY_URL in text or "self-upgrade-agent.git" in text:
            stale_hits.append(path.relative_to(ROOT).as_posix())
    assert stale_hits == [], f"active legacy repository references: {stale_hits}"
