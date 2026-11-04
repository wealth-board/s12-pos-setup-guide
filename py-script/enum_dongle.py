#!/usr/bin/env python3
"""Enumerate USB dongle: VID/PID, strings, interfaces, endpoints."""
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

VID = 0x3689  # vendor id
PID = 0x8762  # product id


def s(dev, idx):
    try:
        return usb.util.get_string(dev, idx)
    except Exception:
        return None


def main():
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        sys.exit(f"device not found: VID={hex(VID)} PID={hex(PID)}")

    print("device:", hex(dev.idVendor), hex(dev.idProduct))
    print("manufacturer:", s(dev, dev.iManufacturer))
    print("product:", s(dev, dev.iProduct))
    print("serial:", s(dev, dev.iSerialNumber))

    for cfg in dev:
        for intf in cfg:
            print(f"iface {intf.bInterfaceNumber} class={intf.bInterfaceClass} "
                  f"sub={intf.bInterfaceSubClass} proto={intf.bInterfaceProtocol}")
            for ep in intf:
                print(f"  ep 0x{ep.bEndpointAddress:02x} "
                      f"attr={ep.bmAttributes} maxpkt={ep.wMaxPacketSize}")


if __name__ == "__main__":
    main()
