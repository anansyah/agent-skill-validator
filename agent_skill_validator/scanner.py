from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable


SKILL_DIR_CANDIDATES = [
    "skills",
    "agent-skills",
    ".skills",
    "packages",
    "SKILLS",
    "agents",
]

SUPPORTED_EXTENSIONS = {
    ".py", ".md", ".yaml", ".yml", ".toml", ".json", ".sh",
    ".js", ".ts", ".tsx", ".jsx", ".rb", ".go", ".rs",
}

STDLIB_MODULES = {
    "os", "sys", "json", "re", "pathlib", "typing", "collections",
    "dataclasses", "pydantic", "fastapi", "asyncio", "logging",
    "argparse", "datetime", "time", "uuid", "hashlib", "base64",
    "itertools", "functools", "contextlib", "abc", "enum",
}

COMMON_DEPS = {
    "requests", "urllib3", "httpx", "aiohttp", "openai", "anthropic",
    "numpy", "pandas", "scipy", "sklearn", "torch", "tensorflow",
    "matplotlib", "pillow", "sqlalchemy", "redis", "celery",
    "fastapi", "uvicorn", "pydantic", "sqlalchemy", "alembic",
}

DEPRECATED_MODELS = {
    "gpt-3.5-turbo-0301",
    "gpt-4-0314",
    "gpt-4-32k-0314",
    "claude-2.0",
    "claude-2.1",
    "text-davinci-003",
    "text-curie-001",
    "text-babbage-001",
    "text-ada-001",
}

UNSAFE_PATTERNS = [
    (r"rm\s+-rf\s+/", "Unsafe shell command: rm -rf /", "error"),
    (r"curl\s+\|[^\n]*bash", "Unsafe shell command: curl | bash", "error"),
    (r"curl\s+\|[^\n]*sh", "Unsafe shell command: curl | sh", "error"),
    (r"wget\s+\|[^\n]*bash", "Unsafe shell command: wget | bash", "error"),
    (r"chmod\s+777", "Unsafe permission: chmod 777", "warn"),
    (r"eval\s*\(", "Unsafe eval() usage", "warn"),
    (r"exec\s*\(", "Unsafe exec() usage", "warn"),
    (r"subprocess\.call.*shell=True", "Unsafe subprocess with shell=True", "warn"),
    (r"os\.system\s*\(", "Unsafe os.system() usage", "warn"),
]

SECRET_PATTERNS = [
    (r"api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]", "Hardcoded API key candidate", "error"),
    (r"password\s*[:=]\s*['\"][^'\"]{3,}['\"]", "Hardcoded password candidate", "error"),
    (r"secret\s*[:=]\s*['\"][^'\"]{3,}['\"]", "Hardcoded secret candidate", "error"),
    (r"token\s*[:=]\s*['\"][A-Za-z0-9_\-]{8,}['\"]", "Hardcoded token candidate", "error"),
    (r"Authorization[^\n]{0,40}Bearer[^\n]{0,40}YOUR_API_KEY", "Placeholder API key remains", "warn"),
    (r"sk-[A-Za-z0-9]{20,}", "Possible OpenAI-style API key", "error"),
    (r"ghp_[A-Za-z0-9]{36}", "Possible GitHub PAT", "error"),
    (r"AIza[0-9A-Za-z\-_]{35}", "Possible Google API key", "error"),
]


def find_skill_dirs(repo_path: str) -> list[Path]:
    repo = Path(repo_path)
    if not repo.exists():
        raise SystemExit(f"Repo path not found: {repo_path}")
    candidates = []
    for name in SKILL_DIR_CANDIDATES:
        p = repo / name
        if p.exists() and p.is_dir():
            candidates.append(p)
    if not candidates:
        candidates.append(repo)
    return candidates


def _iter_text_files(entry: Path) -> Iterable[Path]:
    for path in entry.rglob("*"):
        if path.is_file() and path.suffix in SUPPORTED_EXTENSIONS:
            yield path


def _read_text(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except Exception:
        return ""


def scan_dependency_health(entry: Path) -> list[dict[str, Any]]:
    issues = []
    for path in _iter_text_files(entry):
        text = _read_text(path)
        rel = str(path.relative_to(entry))
        if path.suffix == ".py":
            imports = re.findall(r"^(?:import|from)\s+([\w\.]+)", text, flags=re.M)
            for mod in imports:
                pkg = mod.split(".")[0]
                if pkg in STDLIB_MODULES or pkg in COMMON_DEPS:
                    continue
                if len(pkg) > 1 and not pkg.startswith("_"):
                    issues.append({
                        "path": rel,
                        "level": "warn",
                        "message": f"External dependency may need explicit requirement: {pkg}",
                        "category": "dependency",
                    })
        if path.name in {"requirements.txt", "pyproject.toml", "package.json"}:
            if "TODO" in text or "FIXME" in text or "PLACEHOLDER" in text:
                issues.append({
                    "path": rel,
                    "level": "warn",
                    "message": "Dependency manifest contains TODO/FIXME/PLACEHOLDER markers",
                    "category": "dependency",
                })
    return issues


def scan_security(entry: Path) -> list[dict[str, Any]]:
    issues = []
    for path in _iter_text_files(entry):
        text = _read_text(path)
        rel = str(path.relative_to(entry))
        for pattern, message, level in UNSAFE_PATTERNS + SECRET_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                issues.append({
                    "path": rel,
                    "level": level,
                    "message": message,
                    "category": "security",
                })
    return issues


def scan_compatibility(entry: Path) -> list[dict[str, Any]]:
    issues = []
    for path in _iter_text_files(entry):
        text = _read_text(path)
        rel = str(path.relative_to(entry))
        for model in DEPRECATED_MODELS:
            if model in text:
                issues.append({
                    "path": rel,
                    "level": "warn",
                    "message": f"Deprecated model reference: {model}",
                    "category": "compatibility",
                })
        if "max_tokens" in text and "context_length" not in text:
            issues.append({
                "path": rel,
                "level": "info",
                "message": "max_tokens used without context_length consideration",
                "category": "compatibility",
            })
    return issues


def scan_format(entry: Path) -> list[dict[str, Any]]:
    issues = []
    md = entry / "SKILL.md"
    if md.exists():
        text = _read_text(md)
        if not text.startswith("---"):
            issues.append({
                "path": "SKILL.md",
                "level": "warn",
                "message": "Missing SKILL.md frontmatter",
                "category": "format",
            })
    for path in entry.rglob("*.md"):
        text = _read_text(path)
        rel = str(path.relative_to(entry))
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        for link in links:
            if link.startswith("http") and not link.startswith(("http://", "https://")):
                issues.append({
                    "path": rel,
                    "level": "warn",
                    "message": f"Broken relative markdown link: {link}",
                    "category": "format",
                })
    return issues


def scan_skill(entry: Path) -> list[dict[str, Any]]:
    issues = []
    issues.extend(scan_dependency_health(entry))
    issues.extend(scan_security(entry))
    issues.extend(scan_compatibility(entry))
    issues.extend(scan_format(entry))
    return issues


def validate(repo_path: str) -> dict[str, Any]:
    results = []
    for skill_dir in find_skill_dirs(repo_path):
        issues = scan_skill(skill_dir)
        results.append({
            "skill": str(skill_dir.relative_to(Path(repo_path))),
            "issues": issues,
            "issue_count": len(issues),
        })
    return {
        "repo": repo_path,
        "skills": len(results),
        "total_issues": sum(item["issue_count"] for item in results),
        "results": results,
    }


def generate_markdown_report(summary: dict[str, Any]) -> str:
    lines = [
        "# Agent Skill Validator Report",
        "",
        f"**Repo:** {summary['repo']}",
        f"**Skills scanned:** {summary['skills']}",
        f"**Total issues:** {summary['total_issues']}",
        "",
        "---",
        "",
    ]
    for result in summary["results"]:
        lines.append(f"## {result['skill']}")
        lines.append("")
        if result["issues"]:
            for issue in result["issues"]:
                level = issue["level"].upper()
                lines.append(f"- [{level}] {issue['message']}")
                lines.append(f"  - Path: `{issue['path']}`")
                lines.append(f"  - Category: {issue['category']}")
        else:
            lines.append("- No issues found")
        lines.append("")
    return "\n".join(lines)


def generate_html_report(summary: dict[str, Any]) -> str:
    rows = []
    for result in summary["results"]:
        for issue in result["issues"]:
            level = issue["level"]
            rows.append(f"""
            <tr>
              <td>{result['skill']}</td>
              <td>{issue['path']}</td>
              <td><span class="badge {level}">{level}</span></td>
              <td>{issue['category']}</td>
              <td>{issue['message']}</td>
            </tr>
            """)
    return f"""<!DOCTYPE html>
<html>
<head>
  <title>Agent Skill Validator Report</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #ddd; }}
    .badge {{ padding: 2px 8px; border-radius: 4px; font-size: 0.8em; }}
    .error {{ background: #fee; color: #c00; }}
    .warn {{ background: #ffe; color: #860; }}
    .info {{ background: #eef; color: #06c; }}
  </style>
</head>
<body>
  <h1>Agent Skill Validator Report</h1>
  <p><strong>Repo:</strong> {summary['repo']}</p>
  <p><strong>Skills:</strong> {summary['skills']} | <strong>Issues:</strong> {summary['total_issues']}</p>
  <table>
    <tr><th>Skill</th><th>Path</th><th>Level</th><th>Category</th><th>Message</th></tr>
    {''.join(rows)}
  </table>
</body>
</html>
"""


def check_skill_versions(repo_path: str) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "log", "--oneline", "--all", "--", "skills/", "SKILL.md"],
            capture_output=True, text=True, timeout=10
        )
        commits = result.stdout.strip().splitlines()[:5]
        return {
            "git_available": True,
            "recent_commits": commits,
            "commit_count": len(commits),
        }
    except Exception:
        return {"git_available": False}


def test_skill_prompts(repo_path: str, model: str) -> dict[str, Any]:
    return {
        "model": model,
        "status": "not_implemented",
        "message": "Multi-model prompt testing is planned for v0.3.0",
        "skills_tested": 0,
    }
