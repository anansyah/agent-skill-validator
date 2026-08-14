from pathlib import Path
from agent_skill_validator.scanner import validate, scan_skill


def test_scan_detects_placeholder(tmp_path):
    root = tmp_path / "skill"
    root.mkdir()
    (root / "bot.py").write_text("Authorization: Bearer YOUR_API_KEY\n")
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
