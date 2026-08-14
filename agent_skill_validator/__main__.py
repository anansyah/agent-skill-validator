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
        candidates.append(repo)
    return candidates


def scan_skill(entry: Path):
    issues = []
    for path in entry.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".md", ".yaml", ".yml", ".toml", ".json", ".sh"}:
            continue
        text = ""
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue

        if ("requests.get(" in text or "urllib.request" in text) and "proxies=" not in text and "ProxyHandler" not in text:
            issues.append({"path": str(path), "level": "warn", "message": "HTTP request without explicit proxy handling"})
        if re.search(r"Authorization[^\n]{0,40}Bearer[^\n]{0,40}YOUR_API_KEY", text):
            issues.append({"path": str(path), "level": "warn", "message": "Placeholder API key remains in code"})
        if "TODO" in text or "FIXME" in text:
            issues.append({"path": str(path), "level": "info", "message": "TODO/FIXME marker found"})
        if path.name == "SKILL.md" and not text.startswith("---"):
            issues.append({"path": str(path), "level": "warn", "message": "Missing SKILL.md frontmatter"})
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


def test_samples(repo_path: str, model: str):
    summary = {
        "repo": repo_path,
        "model": model,
        "status": "not_implemented",
        "message": "Multi-model prompt testing is planned for a future release.",
    }
    print(json.dumps(summary, indent=2))
    return summary


def build_parser():
    parser = argparse.ArgumentParser(prog="agent-skill-validator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("repo")
    p_validate.add_argument("--output", default=None)

    p_test = sub.add_parser("test")
    p_test.add_argument("repo")
    p_test.add_argument("--model", required=True)
    p_test.add_argument("--output", default=None)

    p_report = sub.add_parser("report")
    p_report.add_argument("repo")
    p_report.add_argument("--output", default=None)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "validate":
        summary = validate(args.repo)
    elif args.command == "test":
        summary = test_samples(args.repo, args.model)
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
