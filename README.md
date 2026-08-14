# Agent Skill Validator

![Python Versions](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-stable-green)
![GitHub stars](https://img.shields.io/github/stars/anansyah/agent-skill-validator?style=social)
![PyPI Version](https://img.shields.io/pypi/v/agent-skill-validator)

Auto-test AI agent skills for **broken dependencies**, **compatibility issues**, and **security risks**. Works with **Hermes**, **Claude Code**, **OpenCode**, **Codex**, and any agent using `SKILL.md` / `.claude.md` format.

## Why

Agent skills break all the time:
- Model provider changes API contract
- Dependency updates introduce breaking changes
- Hardcoded secrets leak in public repos
- Skill format evolves and old skills become incompatible

This tool catches those issues **before they hit production**.

## Install

### Desktop / Server

```bash
pip install agent-skill-validator
```

### Termux (Android)

```bash
pkg update -y && pkg upgrade -y
pkg install python -y
pip install pyyaml requests rich jinja2 -q
git clone https://github.com/anansyah/agent-skill-validator.git
cd agent-skill-validator
```

### Portable / No Install

```bash
git clone https://github.com/anansyah/agent-skill-validator.git
cd agent-skill-validator
python3 -m agent_skill_validator validate ./your-skill-repo
```

## Quick Start

```bash
# Validate a local skill repo
agent-skill-validator validate ./my-skill-repo

# Generate markdown report
agent-skill-validator report ./my-skill-repo --output report.md

# Generate HTML report
agent-skill-validator report ./my-skill-repo --format html --output report.html

# Test prompt samples against a model
agent-skill-validator test ./my-skill-repo --model openai/gpt-4o-mini
```

## Supported Skill Formats

| Format | Paths scanned |
|---|---|
| Hermes | `SKILL.md`, `skills/`, `.skills/` |
| Claude Code | `.claude.md`, `CLAUDE.md` |
| OpenCode | `opencode.json`, `agents/` |
| Generic | Any `.md`, `.yaml`, `.json`, `.py`, `.sh`, `.js`, `.ts` |

## Checks Performed

### Dependency Health
- Missing imports in Python/JS/TS files
- Broken `requirements.txt` / `package.json` references
- Unpinned or obviously outdated versions

### Security
- Hardcoded API keys, tokens, passwords
- Unsafe shell commands (`rm -rf`, `curl | bash`)
- Placeholder secrets left in code
- Dangerous patterns (`eval()`, `exec()`, `shell=True`)

### Compatibility
- API endpoint drift between models
- Deprecated parameter usage
- Context length assumptions
- Hardcoded provider base URLs

### Format
- Missing `SKILL.md` frontmatter
- Broken markdown links
- Invalid YAML/JSON configs

## Example Output

```json
{
  "repo": "./my-skill-repo",
  "skills": 3,
  "total_issues": 7,
  "results": [
    {
      "skill": "demo-skill",
      "issue_count": 3,
      "issues": [
        {"level": "error", "message": "Missing SKILL.md frontmatter"},
        {"level": "warn", "message": "Hardcoded API key in bot.py:42"}
      ]
    }
  ]
}
```

## CI Integration

Add to your workflow:

```yaml
- name: Validate agent skills
  run: |
    pip install agent-skill-validator
    agent-skill-validator validate . --output skill-report.json
```

## Roadmap

- [x] Core dependency scanning
- [x] Security scanning
- [x] Compatibility scanning
- [x] Format validation
- [x] Markdown/HTML reports
- [ ] Multi-model prompt testing
- [ ] Diff between skill versions
- [ ] Share anonymized compatibility reports
- [ ] Plugin system for custom checks

## License

MIT
