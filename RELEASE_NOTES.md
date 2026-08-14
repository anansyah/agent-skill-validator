# Agent Skill Validator v0.2.0

## What's new

- **Security scanning**: detect hardcoded secrets, unsafe shell commands, placeholder keys
- **Compatibility scanning**: deprecated model references, context-length blind spots
- **Format validation**: SKILL.md frontmatter, broken markdown links
- **Reports**: JSON, Markdown, and HTML output
- **Tests**: pytest suite with broken-skill fixture
- **Examples**: sample-skill and xau-scalper

## Install

```bash
pip install agent-skill-validator
```

## Quick test

```bash
git clone https://github.com/anansyah/agent-skill-validator.git
cd agent-skill-validator
python3 -m agent_skill_validator validate ./tests/fixtures/broken-skill
```

## Full diff

See commits since v0.1.0:
- feat: add comprehensive scanner, reports, tests, examples
- feat: add scanner core, landing page, tests, CI workflow
- chore: scaffold agent-skill-validator repo
