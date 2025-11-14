#!/usr/bin/env python3
"""
Decode the XOR-obfuscated integer arrays embedded in the attacker PowerShell scripts.

Example (reads disable.ps1, extracts the numbers inside "-join (...)", XORs them
with the default key 0x6834783072 and prints the recovered payload):

    ./decode_xor_payload.py disable.ps1
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_KEY = 0x6834783072


def _extract_numbers(raw: str) -> list[int]:
    """
    Return the list of integers from the "-join (...)" section if present, otherwise
    fall back to every integer value found in the input text.
    """
    match = re.search(r"-join\s*\((.*?)\|\s*ForEach-Object", raw, re.S)
    numbers_blob = match.group(1) if match else raw
    return [int(token) for token in re.findall(r"-?\d+", numbers_blob)]


def decode_file(path: Path, key: int) -> str:
    content = path.read_text(encoding="utf-8", errors="ignore")
    numbers = _extract_numbers(content)
    if not numbers:
        raise ValueError("No integers found to decode.")

    decoded_chars: list[str] = []
    for value in numbers:
        char_code = value ^ key
        if char_code < 0 or char_code > sys.maxunicode:
            raise ValueError(f"Decoded code point out of range: {char_code}")
        decoded_chars.append(chr(char_code))
    return "".join(decoded_chars)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decode XOR-obfuscated PowerShell payloads.")
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        help="File containing the comma-separated integers (default: disable.ps1 next to this script)",
    )
    parser.add_argument(
        "--key",
        default=f"0x{DEFAULT_KEY:x}",
        help="XOR key as integer or hex literal (default: 0x6834783072)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source or Path(__file__).with_name("disable.ps1")
    if not source.is_file():
        raise SystemExit(f"Input file not found: {source}")

    try:
        key = int(args.key, 0)
    except ValueError as exc:
        raise SystemExit(f"Invalid key value: {args.key}") from exc

    try:
        decoded = decode_file(source, key)
    except Exception as exc:  # pragma: no cover - CLI utility
        raise SystemExit(f"Decoding failed: {exc}") from exc

    print(decoded)


if __name__ == "__main__":
    main()
