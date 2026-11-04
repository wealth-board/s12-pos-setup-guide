#!/usr/bin/env python3
"""Read key blob from a vendor-class dongle via control transfer."""
import os
import sys

if sys.platform == "win32":
    try:
        os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        pass

try:
    import usb.core
    import usb.util
except ImportError:
    sys.exit("missing dependency: pip install pyusb")

VID, PID = 0x3689, 0x8762
BM_REQUEST_TYPE = 0xC0  # vendor, device-to-host
B_REQUEST = 0x00        # restored from capture
W_VALUE, W_INDEX = 0x0000, 0x0000
LEN = 64
OUTPUT_DIR = "output"
RAW_PATH = os.path.join(OUTPUT_DIR, "dongle_key.bin")


def main():
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        sys.exit(f"device not found: VID={hex(VID)} PID={hex(PID)}")
    dev.set_configuration()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        blob = bytes(dev.ctrl_transfer(BM_REQUEST_TYPE, B_REQUEST,
                                       W_VALUE, W_INDEX, LEN))
        print("raw:", blob.hex())
        with open(RAW_PATH, "wb") as f:
            f.write(blob)
    finally:
        usb.util.dispose_resources(dev)


if __name__ == "__main__":
    main()
