from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable


SKILL_DIR_CANDIDATES = [
    "skills",
    "agent-skills",
    ".skills",
    "packages",
    "SKILLS",
]


def find_skill_dirs(repo_path: str):
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
        if path.is_file() and path.suffix in {".py", ".md", ".yaml", ".yml", ".toml", ".json", ".sh", ".js", ".ts"}:
            yield path


def _read_text(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except Exception:
        return ""


def scan_dependency_health(entry: Path):
    issues = []
    for path in _iter_text_files(entry):
        text = _read_text(path)
        rel = str(path.relative_to(entry))
        if path.suffix == ".py":
            imports = re.findall(r"^(?:import|from)\s+([\w\.]+)", text, flags=re.M)
            for mod in imports:
                pkg = mod.split(".")[0]
                if pkg in {"requests", "urllib3", "httpx", "aiohttp", "openai", "anthropic"}:
                    continue
                if pkg in {"os", "sys", "json", "re", "pathlib", "typing", "collections", "dataclasses", "pydantic", "fastapi"}:
                    continue
                issues.append({
                    "path": rel,
                    "level": "warn",
                    "message": f"External dependency import may need explicit requirement: {pkg}",
                })
        if path.name in {"requirements.txt", "pyproject.toml", "package.json"}:
            if "TODO" in text or "FIXME" in text or "PLACEHOLDER" in text:
                issues.append({
                    "path": rel,
                    "level": "warn",
                    "message": "Dependency manifest contains TODO/FIXME/PLACEHOLDER markers",
                })
    return issues


def scan_security(entry: Path):
    issues = []
    patterns = [
        (r"Authorization[^\n]{0,40}Bearer[^\n]{0,40}YOUR_API_KEY", "Placeholder API key remains in code"),
        (r"api[_-]?key\s*[:=]\s*['"][A-Za-z0-9_\-]{8,}['"]", "Hardcoded API key candidate"),
        (r"password\s*[:=]\s*['"][^'"]{3,}['"]", "Hardcoded password candidate"),
        (r"rm -rf\s+/", "Unsafe shell command: rm -rf /"),
        (r"curl\s+\|[^\n]*bash", "Unsafe shell command: curl | bash"),
        (r"curl\s+\|[^\n]*sh", "Unsafe shell command: curl | sh"),
        (r"wget\s+\|[^\n]*bash", "Unsafe shell command: wget | bash"),
    ]
    for path in _iter_text_files(entry):
        text = _read_text(path)
        rel = str(path.relative_to(entry))
        for pattern, message in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                issues.append({"path": rel, "level": "error", "message": message})
    return issues


def scan_compatibility(entry: Path):
    issues = []
    deprecated_models = {"gpt-3.5-turbo-0301", "gpt-4-0314", "claude-2.0"}
    for path in _iter_text_files(entry):
        text = _read_text(path)
        rel = str(path.relative_to(entry))
        for model in deprecated_models:
            if model in text:
                issues.append({
                    "path": rel,
                    "level": "warn",
                    "message": f"Deprecated model reference: {model}",
                })
        if "max_tokens" in text and "context_length" not in text:
            issues.append({
                "path": rel,
                "level": "info",
                "message": "max_tokens used without context_length consideration",
            })
    return issues


def scan_format(entry: Path):
    issues = []
    md = entry / "SKILL.md"
    if md.exists():
        text = _read_text(md)
        if not text.startswith("---"):
            issues.append({"path": "SKILL.md", "level": "warn", "message": "Missing SKILL.md frontmatter"})
    for path in entry.rglob("*.md"):
        text = _read_text(path)
        rel = str(path.relative_to(entry))
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        for link in links:
            if link.startswith("http") and not link.startswith(("http://", "https://")):
                issues.append({"path": rel, "level": "warn", "message": f"Broken relative markdown link: {link}"})
    return issues


def scan_skill(entry: Path):
    issues = []
    issues.extend(scan_dependency_health(entry))
    issues.extend(scan_security(entry))
    issues.extend(scan_compatibility(entry))
    issues.extend(scan_format(entry))
    return issues


def validate(repo_path: str):
    results = []
    for skill_dir in find_skill_dirs(repo_path):
        issues = scan_skill(skill_dir)
        results.append({
            "skill": str(skill_dir.relative_to(Path(repo_path))),
            "issues": issues,
            "issue_count": len(issues),
        })
    summary = {
        "repo": repo_path,
        "skills": len(results),
        "total_issues": sum(item["issue_count"] for item in results),
        "results": results,
    }
    return summary
