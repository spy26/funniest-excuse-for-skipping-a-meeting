#!/usr/bin/env python3
"""Write the meeting-skipping excuse to entry.txt.

The competition wants exactly one line, at most 200 characters, in
/output/entry.txt (or $MAKEFUN_OUTPUT_DIR/entry.txt). This script holds
the line, checks it against the gate, writes it as UTF-8 with no trailing
newline, then reads it back to prove the file matches byte for byte.
Stdlib only; nothing random, no clock, no network.
"""

import hashlib
import os
import sys

EXCUSE = (
    "My dog ate my meeting invite, then my Wi-Fi, then my will to attend "
    "a call that could have been a three-word email."
)

CHAR_LIMIT = 200
DEFAULT_DIR = "/output"
OUT_NAME = "entry.txt"


def guard(line):
    """Fail fast on the first gate rule the line breaks."""
    if not line:
        raise ValueError("entry is empty")
    if len(line) > CHAR_LIMIT:
        raise ValueError(
            "entry is %d characters, over the %d limit" % (len(line), CHAR_LIMIT)
        )
    if line != line.strip():
        raise ValueError("entry has leading or trailing whitespace")
    if line.strip() == "":
        raise ValueError("entry is only whitespace")
    for ch in line:
        if ord(ch) < 32:
            raise ValueError("entry holds a control character")
    if "\n" in line or "\r" in line:
        raise ValueError("entry spans more than one line")
    if "  " in line:
        raise ValueError("entry has a double space")
    marks = line.count(".") + line.count("!") + line.count("?")
    if marks != 1 or not line.endswith("."):
        raise ValueError("entry is not exactly one sentence")


def pick_out_dir():
    """Where the entry goes: the env var wins, otherwise /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or DEFAULT_DIR


def emit(line, directory):
    """Validate, write, and read back; return (path, payload bytes)."""
    guard(line)
    payload = line.encode("utf-8")
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, OUT_NAME)
    with open(path, "wb") as fh:
        fh.write(payload)
    with open(path, "rb") as fh:
        again = fh.read()
    if again != payload:
        raise ValueError(
            "read-back differs: wrote %d bytes, read %d" % (len(payload), len(again))
        )
    return path, payload


def main(argv):
    if len(argv) != 1:
        sys.stderr.write("usage: python3 main.py (no arguments)\n")
        return 2
    try:
        path, payload = emit(EXCUSE, pick_out_dir())
    except (ValueError, OSError) as problem:
        sys.stderr.write("error: %s\n" % problem)
        return 1
    digest = hashlib.sha256(payload).hexdigest()
    text = payload.decode("utf-8")
    if "\n" in text or "\r" in text or len(text) > CHAR_LIMIT:
        sys.stderr.write("error: final entry failed the line/length gate\n")
        return 1
    print(
        "wrote %s (%d characters, %d bytes, sha256 %s)"
        % (path, len(EXCUSE), len(payload), digest)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
