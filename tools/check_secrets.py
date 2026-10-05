"""Fail CI on tracked dotenv secrets or recognizable API credentials, without printing them."""
import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = (
    re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}\b"),
    re.compile(r"(?<![A-Za-z0-9_/+=-])SK[A-Za-z0-9]{35,}(?![A-Za-z0-9_/+=-])"),
    re.compile(r"(?<![A-Za-z0-9_/+=-])ID[A-Za-z0-9]{26,}(?![A-Za-z0-9_/+=-])"),
)


def scan(include_untracked=False):
    arguments = ["git", "ls-files", "-z"]
    if include_untracked:
        arguments.extend(["--cached", "--others", "--exclude-standard"])
    paths = subprocess.check_output(arguments, cwd=ROOT).decode().split("\0")
    problems = []
    for name in filter(None, paths):
        path = ROOT / name
        if ".env" in path.name and path.name != ".env.example":
            problems.append(name + ": dotenv file must not be tracked")
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        for number, line in enumerate(contents.splitlines(), 1):
            if any(pattern.search(line) for pattern in PATTERNS):
                problems.append(f"{name}:{number}: possible private API credential")
    return problems


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-untracked", action="store_true")
    findings = scan(parser.parse_args().include_untracked)
    for finding in findings:
        print(finding)
    if findings:
        raise SystemExit(1)
    print("Tracked source secret scan passed (credential values are never printed).")
