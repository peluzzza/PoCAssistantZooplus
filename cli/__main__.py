"""zooplus Assistant operator CLI."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="zooplus-cli", description="zooplus PoC operator CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("eda", help="Run dataset EDA → docs/01-eda-report.md")
    sub.add_parser("ingest", help="Build RAG index from data/raw/")
    sub.add_parser("evaluate", help="Run golden query evaluation")
    sub.add_parser("chat-local", help="Smoke-test chat without HTTP")

    args = parser.parse_args(argv)
    if args.command == "eda":
        from cli.commands.eda import run_eda

        return run_eda()
    if args.command == "ingest":
        from cli.commands.ingest import run as run_ingest

        return run_ingest()
    if args.command == "evaluate":
        print("evaluate: not implemented yet (T5)", file=sys.stderr)
        return 1
    if args.command == "chat-local":
        print("chat-local: not implemented yet (T5)", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
