from pathlib import Path
import json
from agent_skill_validator.__main__ import scan_skill, validate


def test_scan_detects_placeholder():
    root = Path("/tmp/agent-skill-validator-test")
    root.mkdir(parents=True, exist_ok=True)
    f = root / "skill.md"
    f.write_text("Authorization: Bearer YOUR_API_KEY\n")
    issues = scan_skill(root)
    assert any("Placeholder API key" in i["message"] for i in issues)


def test_validate_returns_summary(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    skill = repo / "skills" / "demo"
    skill.mkdir(parents=True)
    (skill / "README.md").write_text("Hello")
    summary = validate(str(repo))
    assert summary["skills"] == 1
