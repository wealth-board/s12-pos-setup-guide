#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python3 -m venv .venv 2>/dev/null || true
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --quiet -r requirements.txt

python enum_dongle.py || true
python read_hid_dongle.py || python read_vendor_dongle.py
python extract_key.py
