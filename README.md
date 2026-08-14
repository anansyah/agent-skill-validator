# Agent Skill Validator

![Python Versions](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-beta-orange)
![GitHub stars](https://img.shields.io/github/stars/anansyah/agent-skill-validator?style=social)

Auto-test AI agent skills for **broken dependencies**, **compatibility issues**, and **security risks**. Works with **Hermes**, **Claude Code**, **OpenCode**, **Codex**, and any agent using `SKILL.md` / `.claude.md` format.

## Why

Agent skills break all the time:
- Model provider changes API contract
- Dependency updates introduce breaking changes  
- Hardcoded secrets leak in public repos
- Skill format evolves and old skills become incompatible

This tool catches those issues **before they hit production**.

## Install

```bash
pip install agent-skill-validator
```

## Quick Start

```bash
# Validate a local skill repo
agent-skill-validator validate ./my-skill-repo

# Generate markdown report
agent-skill-validator report ./my-skill-repo --output report.md

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

### Compatibility
- API endpoint drift between models
- Deprecated parameter usage
- Context length assumptions

### Security
- Hardcoded API keys, tokens, passwords
- Unsafe shell commands (`rm -rf`, `curl | bash`)
- Placeholder secrets left in code

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
      "skill": "xau-scalper",
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

- [ ] Multi-model prompt testing
- [ ] Diff between skill versions
- [ ] Share anonymized compatibility reports
- [ ] Plugin system for custom checks

## License

MIT
