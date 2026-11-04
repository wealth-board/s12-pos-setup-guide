#!/usr/bin/env python3
"""Read key blob from a HID dongle via feature/output reports."""
import os
import sys
import ctypes

if sys.platform == "win32":
    try:
        os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        pass

try:
    import hid
except ImportError:
    sys.exit("missing dependency: pip install hidapi")

VID, PID = 0x3689, 0x8762
REPORT_ID = 0x01
CMD_READ = 0x81    # restored from capture
ADDR = 0x0000      # key start address placeholder
LEN = 0x40
OUTPUT_DIR = "output"
RAW_PATH = os.path.join(OUTPUT_DIR, "dongle_key.bin")


def read_block_win32(h_dev, addr, length):
    hid_dll = ctypes.windll.hid
    req = ctypes.create_string_buffer(257)
    req[0] = REPORT_ID
    req[1] = CMD_READ
    req[2] = (addr >> 8) & 0xFF
    req[3] = addr & 0xFF
    req[4] = length & 0xFF
    hid_dll.HidD_SetFeature(h_dev, req, 257)

    resp = ctypes.create_string_buffer(257)
    resp[0] = REPORT_ID
    res = hid_dll.HidD_GetFeature(h_dev, resp, 257)
    if not res:
        raise RuntimeError("HidD_GetFeature failed")
    return bytes(resp.raw[1:1 + length])


def read_block_hid(d, addr, length):
    req = bytes([REPORT_ID, CMD_READ,
                 (addr >> 8) & 0xFF, addr & 0xFF,
                 length & 0xFF, 0, 0, 0])
    d.write(req)
    resp = bytes(d.read(64))
    if not resp:
        raise RuntimeError("empty response")
    return resp[:length]


def main():
    if sys.platform == "win32":
        devs = hid.enumerate(VID, PID)
        if not devs:
            sys.exit(f"device not found: VID={hex(VID)} PID={hex(PID)}")
        path = devs[0]["path"]
        k = ctypes.windll.kernel32
        h_dev = k.CreateFileA(path, 0xC0000000, 1 | 2, None, 3, 0, None)
        if h_dev == -1 or h_dev == 0xFFFFFFFFFFFFFFFF:
            h_dev = k.CreateFileA(path, 0, 1 | 2, None, 3, 0, None)
        if h_dev == -1 or h_dev == 0xFFFFFFFFFFFFFFFF:
            sys.exit("failed to open device handle")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        try:
            blob = b"".join(read_block_win32(h_dev, ADDR + i, 16) for i in range(0, LEN, 16))
            print("raw:", blob.hex())
            with open(RAW_PATH, "wb") as f:
                f.write(blob)
        finally:
            k.CloseHandle(h_dev)
    else:
        if hasattr(hid, "Device"):
            d = hid.Device(VID, PID)
        else:
            d = hid.device()
            d.open(VID, PID)
        if hasattr(d, "set_nonblocking"):
            d.set_nonblocking(0)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        try:
            blob = b"".join(read_block_hid(d, ADDR + i, 16) for i in range(0, LEN, 16))
            print("raw:", blob.hex())
            with open(RAW_PATH, "wb") as f:
                f.write(blob)
        finally:
            d.close()


if __name__ == "__main__":
    main()
