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
