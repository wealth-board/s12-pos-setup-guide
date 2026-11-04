#!/usr/bin/env python3
"""Trim key from raw blob, checksum, persist."""
import hashlib
import os
import sys

OUTPUT_DIR = "output"
RAW_PATH = os.path.join(OUTPUT_DIR, "dongle_key.bin") if os.path.exists(os.path.join(OUTPUT_DIR, "dongle_key.bin")) else "dongle_key.bin"
KEY_OFFSET = 0x00    # key offset within blob placeholder
KEY_LEN = 32
OUT_PATH = os.path.join(OUTPUT_DIR, "key.bin")


def checksum(b):
    return hashlib.sha256(b).digest()[:4]


def main():
    with open(RAW_PATH, "rb") as f:
        raw = f.read()
    if len(raw) < KEY_OFFSET + KEY_LEN:
        sys.exit(f"blob too short: {len(raw)} bytes, need {KEY_OFFSET + KEY_LEN}")
    key = raw[KEY_OFFSET:KEY_OFFSET + KEY_LEN]
    print("key:", key.hex())
    print("checksum:", checksum(key).hex())
    with open(OUT_PATH, "wb") as f:
        f.write(key)
    print("written:", OUT_PATH)


if __name__ == "__main__":
    main()
