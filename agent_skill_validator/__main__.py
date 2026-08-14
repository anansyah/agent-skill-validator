import argparse
import json
import sys
from pathlib import Path
from agent_skill_validator.scanner import validate, generate_markdown_report, generate_html_report, test_skill_prompts


def build_parser():
    parser = argparse.ArgumentParser(
        prog="agent-skill-validator",
        description="Validate AI agent skills for broken deps, security, and compatibility",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Validate a skill repo")
    p_validate.add_argument("repo", help="Path to skill repo")
    p_validate.add_argument("--output", "-o", help="Output file path")
    p_validate.add_argument("--format", choices=["json", "md", "html"], default="json")

    p_test = sub.add_parser("test", help="Test skill prompts against a model")
    p_test.add_argument("repo", help="Path to skill repo")
    p_test.add_argument("--model", required=True, help="Model to test against")
    p_test.add_argument("--output", "-o", help="Output file path")

    p_report = sub.add_parser("report", help="Generate validation report")
    p_report.add_argument("repo", help="Path to skill repo")
    p_report.add_argument("--output", "-o", help="Output file path")
    p_report.add_argument("--format", choices=["md", "html"], default="md")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "validate":
        summary = validate(args.repo)
        if args.format == "json" or not args.format:
            output = json.dumps(summary, indent=2)
        elif args.format == "md":
            output = generate_markdown_report(summary)
        elif args.format == "html":
            output = generate_html_report(summary)
        
        print(output)
        if args.output:
            Path(args.output).write_text(output)
            print(f"\nReport written to {args.output}", file=sys.stderr)

    elif args.command == "test":
        summary = test_skill_prompts(args.repo, args.model)
        print(json.dumps(summary, indent=2))
        if args.output:
            Path(args.output).write_text(json.dumps(summary, indent=2))

    elif args.command == "report":
        summary = validate(args.repo)
        output = generate_markdown_report(summary) if args.format == "md" else generate_html_report(summary)
        print(output)
        if args.output:
            Path(args.output).write_text(output)
            print(f"\nReport written to {args.output}", file=sys.stderr)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
