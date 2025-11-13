#!/usr/bin/env python3
"""
Decode HID keyboard reports exported from a USB PCAP (tshark usb.capdata).

By default the script reads usbkeystrok.txt (one hex report per line) and
prints the recovered text to STDOUT. Pass an alternate file path as the first
argument if you generated your reports elsewhere.

To regenerate usbkeystrok.txt from the PCAP:
tshark -r MyKeyMouse.pcap \
  -Y "usb.endpoint_address.direction == 0x81 && usb.data_len == 8" \
  -T fields -e usb.capdata > usbkeystrok.txt
"""

from pathlib import Path
import sys

# Mapping HID usage codes → printable characters (no modifiers applied yet).
HID_KEYCODES = {
    0x04: "a", 0x05: "b", 0x06: "c", 0x07: "d", 0x08: "e",
    0x09: "f", 0x0A: "g", 0x0B: "h", 0x0C: "i", 0x0D: "j",
    0x0E: "k", 0x0F: "l", 0x10: "m", 0x11: "n", 0x12: "o",
    0x13: "p", 0x14: "q", 0x15: "r", 0x16: "s", 0x17: "t",
    0x18: "u", 0x19: "v", 0x1A: "w", 0x1B: "x", 0x1C: "y",
    0x1D: "z", 0x1E: "1", 0x1F: "2", 0x20: "3", 0x21: "4",
    0x22: "5", 0x23: "6", 0x24: "7", 0x25: "8", 0x26: "9",
    0x27: "0", 0x28: "\n", 0x2C: " ", 0x2D: "-", 0x2E: "=",
    0x2F: "[", 0x30: "]", 0x31: "\\", 0x32: "#", 0x33: ";",
    0x34: "'", 0x35: "`", 0x36: ",", 0x37: ".", 0x38: "/"
}

SHIFTED_CHARS = {
    "1": "!", "2": "@", "3": "#", "4": "$", "5": "%",
    "6": "^", "7": "&", "8": "*", "9": "(", "0": ")",
    "-": "_", "=": "+", "[": "{", "]": "}", "\\": "|",
    ";": ":", "'": "\"", "`": "~", ",": "<", ".": ">",
    "/": "?"
}

SHIFT_MASK = 0x22          # Left (0x02) or Right (0x20) shift bits inside modifier byte.
IGNORED_KEYCODES = {0, 1, 255}  # Reserved/filler values that carry no text.
BACKSPACE_CODE = 0x2A
TAB_CODE = 0x2B
REPORT_BYTES = 8           # Keyboard interrupt transfers are 8 bytes: [mods][reserved][6 keycodes]


def _clean_line(raw: str) -> str:
    """Remove whitespace and separators from a report line."""
    return raw.replace(":", "").replace(" ", "").strip()


def _parse_report(raw: str) -> list[int] | None:
    """Return the first 8 bytes of a HID report, or None if the line is malformed."""
    raw = _clean_line(raw)
    if not raw or len(raw) < REPORT_BYTES * 2 or len(raw) % 2:
        return None

    try:
        bytes_list = [int(raw[i:i + 2], 16) for i in range(0, len(raw), 2)]
    except ValueError:
        return None

    if len(bytes_list) < REPORT_BYTES:
        return None
    return bytes_list[:REPORT_BYTES]


def _code_to_char(keycode: int, shift: bool) -> str:
    """Convert a HID key code to its printable representation."""
    char = HID_KEYCODES.get(keycode, "")
    if not char:
        return ""
    if shift:
        return SHIFTED_CHARS.get(char, char.upper())
    return char


def decode_reports(path: Path) -> str:
    """
    Decode every valid report in the capture file.

    We keep track of the previously pressed keys to avoid repeating characters when a
    key is held down, and we handle simple editing keys (Backspace / Tab) to stay close
    to what the user actually typed while recording the PCAP.
    """
    decoded_chars: list[str] = []
    previous_keys: set[int] = set()

    for line in path.read_text().splitlines():
        report = _parse_report(line)
        if not report:
            continue

        modifier = report[0]  # Modifier byte holds shift, ctrl, alt bits.
        shift_pressed = bool(modifier & SHIFT_MASK)

        # Reports contain up to 6 simultaneous keycodes; ignore padding entries.
        keycodes = [code for code in report[2:] if code not in IGNORED_KEYCODES]

        for code in keycodes:
            if code in previous_keys:
                # Key is being held, we already emitted its character.
                continue
            if code == BACKSPACE_CODE:
                if decoded_chars:
                    decoded_chars.pop()
                continue
            if code == TAB_CODE:
                decoded_chars.append("\t")
                continue

            char = _code_to_char(code, shift_pressed)
            if char:
                decoded_chars.append(char)

        # Cache currently pressed keys for the next USB interrupt packet.
        previous_keys = set(keycodes)

    return "".join(decoded_chars)


def main(argv: list[str]) -> None:
    source = Path(argv[1]) if len(argv) > 1 else Path("usbkeystrok.txt")
    if not source.is_file():
        raise SystemExit(f"Input file not found: {source}")
    sys.stdout.write(decode_reports(source))


if __name__ == "__main__":
    main(sys.argv)
