#!/usr/bin/env python3
"""Deep-scan connected USB and HID devices to identify dongle models and descriptors."""
import os
import sys

# Ensure Windows DLL search includes script root for libusb/hidapi
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

try:
    import hid
except ImportError:
    sys.exit("missing dependency: pip install hid")


def get_usb_string(dev, index):
    if not index:
        return "N/A"
    try:
        return usb.util.get_string(dev, index)
    except Exception:
        return "N/A"


def scan_usb_bus():
    lines = ["=== Scanning USB Bus (PyUSB) ==="]
    try:
        devices = list(usb.core.find(find_all=True))
    except Exception as exc:
        lines.append(f"Error querying USB bus: {exc}")
        for l in lines:
            print(l)
        return lines

    found = False
    for dev in devices:
        found = True
        vid = f"0x{dev.idVendor:04x}"
        pid = f"0x{dev.idProduct:04x}"
        mfr = get_usb_string(dev, dev.iManufacturer)
        prod = get_usb_string(dev, dev.iProduct)
        serial = get_usb_string(dev, dev.iSerialNumber)

        lines.append(f"Device Found -> VID: {vid} | PID: {pid}")
        lines.append(f"  Manufacturer:  {mfr}")
        lines.append(f"  Product Name:  {prod}")
        lines.append(f"  Serial Number: {serial}")
        lines.append("-" * 50)

    if not found:
        lines.append("No USB devices found via PyUSB backend.")

    for l in lines:
        print(l)
    return lines


def scan_hid_devices():
    lines = ["\n=== Scanning HID Devices (HIDAPI) ==="]
    devices = hid.enumerate()
    if not devices:
        lines.append("No HID devices detected.")
        for l in lines:
            print(l)
        return lines

    for device in devices:
        vid = f"0x{device['vendor_id']:04x}"
        pid = f"0x{device['product_id']:04x}"
        raw_path = device.get("path", b"")
        path = raw_path.decode("utf-8", errors="replace") if isinstance(raw_path, bytes) else str(raw_path)

        lines.append(f"HID Device -> VID: {vid} | PID: {pid}")
        lines.append(f"  Device Path:    {path}")
        lines.append(f"  Manufacturer:   {device.get('manufacturer_string') or 'N/A'}")
        lines.append(f"  Product:        {device.get('product_string') or 'N/A'}")
        lines.append(f"  Serial Number:  {device.get('serial_number') or 'N/A'}")
        lines.append(f"  Interface Num:  {device.get('interface_number', 'N/A')}")
        lines.append(f"  Usage Page:     {hex(device.get('usage_page', 0))}")
        lines.append(f"  Usage:          {hex(device.get('usage', 0))}")
        lines.append("-" * 50)

    for l in lines:
        print(l)
    return lines


def main():
    print("Starting dongle model identification workflow...\n")
    report = []
    report.extend(scan_usb_bus())
    report.extend(scan_hid_devices())

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "dongle_model_info.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    print(f"\nScan results saved to: {report_path}")


if __name__ == "__main__":
    main()
