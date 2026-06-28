"""Command-line interface for ACDM Validator."""

import argparse
import sys
from pathlib import Path

from acdm_validator.audit import write_audit_record
from acdm_validator.exceptions import ACDMValidatorError
from acdm_validator.validation import validate_contracts
from acdm_validator.version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="acdm-validate",
        description="Validate design-time ACDM Entity Contracts.",
    )
    parser.add_argument("path", help="YAML contract file or directory")
    parser.add_argument("--format", choices=("console", "json"), default="console")
    parser.add_argument(
        "--fail-on",
        choices=("error", "warning", "L1", "L2", "L3"),
        default="error",
        help="Failure threshold (default: error)",
    )
    parser.add_argument("--output", help="Write the selected report format to a file")
    parser.add_argument("--audit-output", help="Write a governance audit record as JSON")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = validate_contracts(args.path, fail_on=args.fail_on)
        rendered = report.to_json() + "\n" if args.format == "json" else report.to_console()
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        if args.audit_output:
            write_audit_record(report, args.audit_output)
        return 1 if report.status == "failed" else 0
    except (ACDMValidatorError, OSError, ValueError) as exc:
        print(f"acdm-validate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
