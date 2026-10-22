# Capturing dongle ↔ POS communication (for debugging)

This page is for **diagnosing a dongle that isn't being detected** — the POS keeps
falling back to trial mode even though the USB licence dongle is plugged in. It
shows how to capture the USB traffic between the dongle and the POS so you can see
whether they're actually talking to each other.

It is **not** a way to copy, clone or emulate the licence. The dongle answers the
POS with an encrypted challenge-response that changes on every run, so a capture
can't be replayed to a second till. Extra tills need their own dongle from the
vendor — see [Licensing (USB dongle)](../README.md#licensing-usb-dongle).

## What you're looking at

The dongle is a **USB HID device** (USB vendor ID `5148`). At startup the POS
(`PosSale.exe` / `PosAdmin.exe`) loads `Bin\SKRTL.dll`, which finds the dongle and
exchanges a short HID report with it: the POS writes a report, the dongle returns
one. That handshake happens in the **first second or two** after the program
launches, so you need the capture running *before* you start the POS.

A healthy capture shows the device enumerate (control transfers that read its
descriptors) and then interrupt/feature-report transfers back and forth. If you
see the device enumerate but **no** report exchange when the POS starts, the POS
isn't reaching it — that's the thing to take to the vendor. If you see nothing at
all, the dongle isn't enumerating (bad port, bad cable, or Wine/VM isn't passing
it through).

## Identifying the dongle vendor

Before (or while) you capture, it's worth finding out **who made the dongle** — it
tells you which drivers to install and who to contact for support. All of this just
reads information the device and the installed files already expose:

1. **Device Manager / USBView** (Windows): plug the dongle in, find it under *Human
   Interface Devices*, then **Properties → Details → Hardware IDs**. You'll see
   `USB\VID_5148&PID_xxxx`. The same dialog's **Manufacturer** and product strings
   usually name the vendor.
2. **The dongle library's metadata**: right-click `Bin\SKRTL.dll` → **Properties →
   Details**. The *Company name*, *Product name* and *Copyright* fields usually name
   the dongle maker.
3. **Cross-check the vendor ID**: look up `VID 5148` (confirm first whether it's hex,
   `0x5148`, or decimal) against the USB-IF / Linux `usb.ids` database. A VID that
   isn't registered to anyone is itself a hint that it's a smaller vendor.

It is **not** Keysight (that's test-and-measurement equipment, not a software-licence
dongle). The library name and VID don't match the big Western dongle brands
(SafeNet/Sentinel HASP, Wibu CodeMeter, Feitian Rockey, KEYLOK) either, so it's most
likely a smaller — probably Chinese — dongle vendor. The checks above will confirm it.

## Windows: USBPcap

1. Install [Wireshark](https://www.wireshark.org/) and, in its installer, tick
   **Install USBPcap**. (Or install USBPcap on its own.) Reboot if it asks.
2. Plug the dongle in. Open Wireshark; you'll see one or more **USBPcap**
   interfaces (`USBPcap1`, `USBPcap2`, …) — one per USB root hub.
3. Work out which hub the dongle is on: Device Manager → **View → Devices by
   connection**, and trace the dongle up to its root hub. If that's fiddly, just
   capture on each USBPcap interface in turn and see which one shows traffic when
   you launch the POS.
4. **Start the capture first**, then launch `PosSale.exe`. The handshake is over
   quickly, so the order matters.
5. Narrow it down once you can see the device:
   - by address: `usb.device_address == N` (read N from the enumeration packets), or
   - by vendor ID to confirm it's the dongle: `usb.idVendor == 0x5148`.
6. Stop the capture after the POS has finished loading. Save it (`File → Save As`)
   if you want to send it to the vendor.

## Linux (POS under Wine): usbmon

```bash
sudo modprobe usbmon
lsusb | grep -i 5148          # note the bus number, e.g. "Bus 001"
```

Then in Wireshark choose the matching **usbmonN** interface (N = the bus number
from `lsusb`), start the capture, and launch the POS. Filter with
`usb.idVendor == 0x5148`, or by the bus/device address from `lsusb`.

If the dongle doesn't appear in `lsusb` at all, Wine/the kernel isn't seeing it —
check the udev rule in the
[Wine guide, Step 5](linux-wine.md#step-5-printers-the-cash-drawer-and-the-licence-dongle)
and try replugging it.

## Reading the result

| What the capture shows | What it means |
|---|---|
| Device enumerates, report exchange when the POS starts | The dongle and POS are talking. If the POS still shows trial mode, it's a licence/activation issue — contact the vendor. |
| Device enumerates, but no exchange when the POS starts | The POS loaded `SKRTL.dll` but isn't reaching the dongle. Note the POS message ("No encryption lock detected") and send the capture to the vendor. |
| Device never enumerates | Hardware or passthrough problem: try another USB port and cable; under Wine or a VM, confirm the dongle is passed through. |
