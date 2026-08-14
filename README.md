# Agent Skill Validator

Auto-test AI agent skills for broken deps + compatibility report.

## Install

```bash
pip install agent-skill-validator
```

## Usage

```bash
agent-skill-validator validate ./path/to/skill-repo
agent-skill-validator test ./path/to/skill-repo --model openai/gpt-4o-mini
agent-skill-validator report ./path/to/skill-repo --output report.md
```

## Features

- Scan skill repo for missing deps, broken imports, API mismatch
- Test prompt samples against multiple models
- Generate compatibility report (markdown + JSON)
- CI action for auto-testing skills on push
