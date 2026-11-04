# Dongle Model Identification Workflow

A technical workflow to inspect connected USB devices, query internal descriptors, extract manufacturer/product strings, and identify hardware protection dongle models.

---

## Workflow Overview

When analyzing unknown security dongles or cryptographic keys, identifying the exact manufacturer, product strings, and interface descriptor tree is necessary to determine the proper communication protocol (HID Reports vs. Vendor Control Transfers).

This workflow utilizes `check_dongle_model.py` to scan across two separate hardware access layers:
1. **PyUSB (USB Bus Layer):** Queries standard USB descriptors (device descriptor, configurations, interfaces, endpoints, string descriptors).
2. **HIDAPI (HID Subsystem Layer):** Queries the operating system's native HID subsystem to resolve device paths, usage pages, and report descriptors without requiring custom kernel drivers.

---

## Workspace Script: `check_dongle_model.py`

Place or verify `check_dongle_model.py` in the project root:

```python
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
    print("=== Scanning USB Bus (PyUSB) ===")
    try:
        devices = list(usb.core.find(find_all=True))
    except Exception as exc:
        print(f"Error querying USB bus: {exc}")
        return

    found = False
    for dev in devices:
        found = True
        vid = f"0x{dev.idVendor:04x}"
        pid = f"0x{dev.idProduct:04x}"
        mfr = get_usb_string(dev, dev.iManufacturer)
        prod = get_usb_string(dev, dev.iProduct)
        serial = get_usb_string(dev, dev.iSerialNumber)

        print(f"Device Found -> VID: {vid} | PID: {pid}")
        print(f"  Manufacturer:  {mfr}")
        print(f"  Product Name:  {prod}")
        print(f"  Serial Number: {serial}")
        print("-" * 50)

    if not found:
        print("No USB devices found via PyUSB backend.")


def scan_hid_devices():
    print("\n=== Scanning HID Devices (HIDAPI) ===")
    devices = hid.enumerate()
    if not devices:
        print("No HID devices detected.")
        return

    for device in devices:
        vid = f"0x{device['vendor_id']:04x}"
        pid = f"0x{device['product_id']:04x}"
        path = device.get("path", b"").decode("utf-8", errors="replace") if isinstance(device.get("path"), bytes) else str(device.get("path"))

        print(f"HID Device -> VID: {vid} | PID: {pid}")
        print(f"  Device Path:    {path}")
        print(f"  Manufacturer:   {device.get('manufacturer_string') or 'N/A'}")
        print(f"  Product:        {device.get('product_string') or 'N/A'}")
        print(f"  Serial Number:  {device.get('serial_number') or 'N/A'}")
        print(f"  Interface Num:  {device.get('interface_number', 'N/A')}")
        print(f"  Usage Page:     {hex(device.get('usage_page', 0))}")
        print(f"  Usage:          {hex(device.get('usage', 0))}")
        print("-" * 50)


def main():
    print("Starting dongle model identification workflow...\n")
    scan_usb_bus()
    scan_hid_devices()


if __name__ == "__main__":
    main()
```

---

## Execution Instructions

### On Windows (PowerShell):
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run model scanner
python check_dongle_model.py
```

### On Linux / WSL (Bash):
```bash
# Activate virtual environment
source .venv/bin/activate

# Run model scanner
python3 check_dongle_model.py
```

---

## Interpreting Output

* **Device Match:** Locate entries matching your dongle's `VID` and `PID`.
* **Manufacturer & Product Names:** Distinguish between generic chips (e.g., FTDI, Prolific) and specialized encryption keys (e.g., `USBKey`, `Syunew`, `SafeNet`, `WibuKey`).
* **Usage Page & Usage:**
  - `0xFF00` - `0xFFFF`: Vendor-defined usage page (standard for cryptographic dongles and custom feature reports).
  - Standard HID pages (e.g., `0x01` Generic Desktop, `0x0C` Consumer): Standard peripheral devices.

---

## Troubleshooting Driver Access

> [!NOTE]
> On Windows, the HID scan (`hidapi`) communicates directly through Windows native `hid.dll` without requiring driver replacement.
>
> If the PyUSB scan reports `NoBackendError` or fails to claim interfaces:
> 1. Ensure `libusb-1.0.dll` resides in the project root or `.venv\Scripts`.
> 2. For vendor-class transfers requiring raw USB pipes, [Zadig](https://zadig.akeo.ie/) can bind the `WinUSB` driver to the vendor interface.
