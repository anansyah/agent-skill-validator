import argparse
import json
from pathlib import Path
from agent_skill_validator.scanner import validate


def build_parser():
    parser = argparse.ArgumentParser(prog="agent-skill-validator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("repo")
    p_validate.add_argument("--output", default=None)

    p_report = sub.add_parser("report")
    p_report.add_argument("repo")
    p_report.add_argument("--output", default=None)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command in {"validate", "report"}:
        summary = validate(args.repo)
        print(json.dumps(summary, indent=2))
        if args.output:
            Path(args.output).write_text(json.dumps(summary, indent=2))
            print(f"Report written to {args.output}")
    else:
        parser.print_help()
        raise SystemExit(1)


if __name__ == "__main__":
    main()
