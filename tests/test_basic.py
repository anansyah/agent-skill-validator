from pathlib import Path
from agent_skill_validator.scanner import validate, scan_skill


def test_scan_detects_placeholder(tmp_path):
    root = tmp_path / "skill"
    root.mkdir()
    (root / "bot.py").write_text("Authorization: Bearer YOUR_API_KEY\n")
    issues = scan_skill(root)
    assert any("Placeholder API key" in i["message"] for i in issues)


def test_scan_detects_deprecated_model(tmp_path):
    root = tmp_path / "skill"
    root.mkdir()
    (root / "config.yaml").write_text("model: gpt-4-0314\n")
    issues = scan_skill(root)
    assert any("Deprecated model" in i["message"] for i in issues)


def test_scan_detects_unsafe_command(tmp_path):
    root = tmp_path / "skill"
    root.mkdir()
    (root / "setup.sh").write_text("rm -rf /tmp/old\n")
    issues = scan_skill(root)
    assert any("rm -rf" in i["message"] for i in issues)


def test_validate_returns_summary(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    skill = repo / "skills" / "demo"
    skill.mkdir(parents=True)
    (skill / "README.md").write_text("Hello")
    summary = validate(str(repo))
    assert summary["skills"] == 1
    assert summary["total_issues"] >= 0


def test_skill_with_frontmatter(tmp_path):
    root = tmp_path / "skill"
    root.mkdir()
    (root / "SKILL.md").write_text("---\nname: test\n---\nContent")
    issues = scan_skill(root)
    assert not any("Missing SKILL.md frontmatter" in i["message"] for i in issues)


def test_broken_skill_fixture():
    fixture = Path(__file__).parent / "fixtures" / "broken-skill"
    summary = validate(str(fixture))
    assert summary["skills"] == 1
    assert summary["total_issues"] >= 8
    messages = [i["message"] for r in summary["results"] for i in r["issues"]]
    assert any("Deprecated model reference: gpt-4-0314" in m for m in messages)
    assert any("rm -rf" in m for m in messages)
    assert any("API key" in m for m in messages)
    assert any("Missing SKILL.md frontmatter" in m for m in messages)
