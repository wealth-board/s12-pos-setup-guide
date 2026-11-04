# Dongle Key Export: Step-by-Step Workflow Guide

A structured guide for enumerating a USB hardware protection key, reading the key blob via HID or vendor control transfer, and extracting the checksummed cryptographic key.

---

## Workflow Overview

| Step | Task | Target File | Output / Artifact |
|---|---|---|---|
| **1** | Connect USB Hardware Dongle | Physical Port | OS Detection |
| **2** | Workspace Setup | Project Directory | Project Structure |
| **3** | Environment Activation | Virtual Environment | `.venv/` Dependencies |
| **4** | Dongle Enumeration | `enum_dongle.py` | VID, PID, Endpoints |
| **5** | Protocol Configuration | Reader Scripts | Configured Protocol Params |
| **6** | Execute Export Pipeline | `run.ps1` / `run.sh` | Automated Execution |
| **7** | Output Verification | Checksum & Hex | `output/dongle_key.bin`, `output/key.bin` |

---

## Step 1: Connect the USB Dongle

Plug the hardware dongle into an available USB port prior to running tools or scripts. This ensures the host operating system registers the device and assigns its Vendor ID (`VID`) and Product ID (`PID`).

---

## Step 2: Workspace Directory Structure

Ensure the project is positioned in your workspace with the standard directory layout:

```text
dongle-export/
├── docs/
│   ├── check-dongle.md
│   └── step-by-step.md
├── output/
│   ├── dongle_key.bin
│   └── key.bin
├── enum_dongle.py
├── extract_key.py
├── read_hid_dongle.py
├── read_vendor_dongle.py
├── requirements.txt
├── run.ps1
└── run.sh
```

---

## Step 3: Open Terminal and Set Up Environment

### On Windows (PowerShell):
```powershell
# Navigate to the workspace directory
cd <path-to-workspace>\dongle-export

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt
```

> [!NOTE]
> If script execution is restricted by PowerShell policy, run:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

### On Linux / WSL (Bash):
```bash
cd /path/to/dongle-export
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Step 4: Enumerate the Dongle (VID / PID & Interface Analysis)

Inspect the hardware identifiers, interface classes, and endpoint configurations:

### Windows:
```powershell
python enum_dongle.py
```

### Linux:
```bash
python3 enum_dongle.py
```

### Expected Output Fields:
* **Vendor ID (VID) & Product ID (PID):** USB identifier pair (e.g., `0x3689` / `0x8762`).
* **Interface Class:**
  - `class=3`: Human Interface Device (HID)
  - `class=255`: Vendor-specific device
* **Endpoints:** IN / OUT endpoint addresses and packet sizes (e.g., `0x81`, `0x01`, `maxpkt=64`).

---

## Step 5: Fill in Protocol Parameters

Configure protocol parameters in the corresponding reader script based on the device interface class:

### For HID Dongles (`read_hid_dongle.py`):
Update protocol constants according to the device specification or bus capture:
```python
VID, PID = 0x3689, 0x8762
REPORT_ID = 0x01
CMD_READ = 0x81
ADDR = 0x0000
LEN = 0x40
```

### For Vendor-Class Dongles (`read_vendor_dongle.py`):
Update control transfer parameters:
```python
VID, PID = 0x3689, 0x8762
BM_REQUEST_TYPE = 0xC0
B_REQUEST = 0x00
W_VALUE, W_INDEX = 0x0000, 0x0000
LEN = 64
```

### For Key Extraction (`extract_key.py`):
Set the slice offset and byte length matching the device key layout:
```python
KEY_OFFSET = 0x00
KEY_LEN = 32
```

---

## Step 6: Run the Full Workflow Automatically

Execute the unified automation script to run enumeration, extraction, and verification sequentially:

### Windows (PowerShell):
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\run.ps1
```

### Linux (Bash):
```bash
chmod +x run.sh
./run.sh
```

---

## Step 7: Verify Output Artifacts

All exported keys and raw blobs are persisted into the `output/` directory:

* [`output/dongle_key.bin`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/dongle_key.bin): The complete raw data block read from the hardware key (e.g., 64 bytes).
* [`output/key.bin`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/key.bin): The sliced cryptographic key (e.g., 32 bytes) along with its SHA-256 integrity checksum prefix.

### Verification Checklist:
1. Confirm `output/dongle_key.bin` byte size equals `LEN`.
2. Confirm `output/key.bin` byte size equals `KEY_LEN`.
3. Compare checksum outputs between multiple sequential runs to ensure reproducible reads.
