import argparse
import json
import os
import re
import sys
from pathlib import Path


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
        p = repo
        if p.exists():
            candidates.append(p)
    return candidates


def scan_skill(entry: Path):
    issues = []
    for path in entry.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".md", ".yaml", ".yml", ".toml", ".json", ".sh"}:
            text = ""
            try:
                text = path.read_text(errors="ignore")
            except Exception:
                continue
            if "requests.get(" in text and "proxies=" not in text and "urllib.request.ProxyHandler" not in text:
                issues.append({"path": str(path), "level": "warn", "message": "HTTP request without explicit proxy handling"})
            if re.search(r"Authorization[^\n]{0,40}Bearer[^\n]{0,40}YOUR_API_KEY", text):
                issues.append({"path": str(path), "level": "warn", "message": "Placeholder API key remains in code"})
            if "TODO" in text or "FIXME" in text:
                issues.append({"path": str(path), "level": "info", "message": "TODO/FIXME marker found"})
    return issues


def validate(repo_path: str):
    report = []
    for skill_dir in find_skill_dirs(repo_path):
        issues = scan_skill(skill_dir)
        report.append({
            "skill": str(skill_dir.relative_to(Path(repo_path))),
            "issues": issues,
            "issue_count": len(issues),
        })
    summary = {
        "repo": repo_path,
        "skills": len(report),
        "total_issues": sum(item["issue_count"] for item in report),
        "results": report,
    }
    print(json.dumps(summary, indent=2))
    return summary


def build_parser():
    parser = argparse.ArgumentParser(prog="agent-skill-validator")
    parser.add_argument("command", choices=["validate", "report"])
    parser.add_argument("repo")
    parser.add_argument("--output", default=None)
    parser.add_argument("--model", default=None)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "validate":
        summary = validate(args.repo)
    elif args.command == "report":
        summary = validate(args.repo)
        if args.output:
            Path(args.output).write_text(json.dumps(summary, indent=2))
            print(f"Report written to {args.output}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
