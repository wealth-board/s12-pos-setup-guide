# dongle-key-export

A modular toolkit to inspect, enumerate, read, and extract cryptographic keys from hardware USB security dongles (supporting both HID-class and vendor-class USB transfer paths).

---

## Repository Layout

```text
dongle-export/
├── docs/
│   ├── check-dongle.md              # Detailed dongle model identification workflow
│   ├── purchasing-guide.md          # Hardware identification & purchasing guide
│   └── step-by-step.md              # End-to-end export workflow guide
├── output/
│   ├── dongle_key.bin               # Raw data block read from device (64 bytes)
│   ├── dongle_model_info.txt        # Full USB/HID scan output report
│   └── key.bin                      # Trimmed & checksum-verified key (32 bytes)
├── check_dongle_model.py            # Deep-scan USB and HID subsystems for device info
├── enum_dongle.py                   # Enumerate VID/PID, strings, interfaces, endpoints
├── extract_key.py                   # Slice raw blob, compute checksum, write key.bin
├── read_hid_dongle.py               # Read raw key blob via HID Output/Feature reports
├── read_vendor_dongle.py            # Read raw key blob via USB vendor control transfers
├── requirements.txt                 # Python dependencies (pyusb, hid)
├── run.ps1                          # Automated Windows PowerShell pipeline runner
└── run.sh                           # Automated Linux Bash pipeline runner
```

---

## Prerequisites & Environment Setup

### 1. Install Python (Host System Requirement)
Before running the tools, ensure Python is installed on your computer:
* **Download:** [python.org/downloads](https://www.python.org/downloads/) (Python 3.8 or newer recommended).
* **Crucial for Windows:** During installation, check the box **"Add python.exe to PATH"**.
* **Verify Installation:**
  ```powershell
  python --version
  ```

---

### 2. Connect Hardware Dongle
Plug your USB hardware dongle into an available USB port so the host operating system detects the device and assigns its hardware IDs (`VID`/`PID`).

---

### 3. Initialize Virtual Environment

#### Windows (PowerShell):
```powershell
# Navigate to project folder
cd <path-to-workspace>\dongle-export

# Create virtual environment (first time only)
python -m venv .venv

# Activate environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

> [!TIP]
> If PowerShell blocks script activation, run:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

#### Linux / WSL (Bash):
```bash
cd /path/to/dongle-export
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Step-by-Step Script Guide

### 1. `check_dongle_model.py`

#### **Purpose:**
Scans both the low-level **USB bus (via PyUSB)** and the operating system's native **HID layer (via HIDAPI)** to discover connected security devices. It extracts vendor IDs, product IDs, manufacturer strings, product descriptions, interface numbers, and HID usage pages to help determine the exact model and communication protocol.

#### **How to Run:**
* **Windows:**
  ```powershell
  python check_dongle_model.py
  ```
* **Linux:**
  ```bash
  python3 check_dongle_model.py
  ```

#### **Output:**
* Prints connected device summaries to the console.
* Automatically saves a full device scan report to [`output/dongle_model_info.txt`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/dongle_model_info.txt).

---

### 2. `enum_dongle.py`

#### **Purpose:**
Performs focused USB descriptor inspection on the target dongle specified by `VID` and `PID`. It queries manufacturer, product, serial strings, interface descriptors, and lists all endpoint addresses (IN/OUT) and their maximum packet sizes.

#### **Configuration:**
Ensure `VID` and `PID` at the top of the file match your device (e.g., `VID = 0x3689`, `PID = 0x8762`).

#### **How to Run:**
* **Windows:**
  ```powershell
  python enum_dongle.py
  ```
* **Linux:**
  ```bash
  python3 enum_dongle.py
  ```

#### **Output:**
* Prints interface class numbers (e.g., `class=3` for HID, `class=255` for Vendor-specific) and endpoint addresses (e.g., `ep 0x81 IN`, `ep 0x01 OUT`).

---

### 3. `read_hid_dongle.py`

#### **Purpose:**
Communicates with **HID-class dongles** (`bInterfaceClass = 3`). It constructs read command packets and retrieves the raw memory blob from the hardware key. It supports standard HID Output/Interrupt reports and falls back to Windows HID **Feature Reports** (`HidD_SetFeature` / `HidD_GetFeature`) for driverless cryptographic keys.

#### **Configuration:**
Review parameters at the top of the script:
* `VID`, `PID`: Target USB hardware identifiers.
* `REPORT_ID`: HID Report ID (default: `0x01`).
* `CMD_READ`: Read opcode (default: `0x81`).
* `ADDR`: Starting memory address offset (default: `0x0000`).
* `LEN`: Total bytes to read (default: `0x40` / 64 bytes).

#### **How to Run:**
* **Windows:**
  ```powershell
  python read_hid_dongle.py
  ```
* **Linux:**
  ```bash
  python3 read_hid_dongle.py
  ```

#### **Output:**
* Generates [`output/dongle_key.bin`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/dongle_key.bin) containing the raw byte dump read from the device.

---

### 4. `read_vendor_dongle.py`

#### **Purpose:**
Communicates with **vendor-class dongles** (`bInterfaceClass = 255`) that use USB default pipe control transfers rather than HID reports.

#### **Configuration:**
Configure control transfer parameters:
* `VID`, `PID`: USB Vendor & Product ID.
* `BM_REQUEST_TYPE`: Transfer direction and type (e.g., `0xC0` for Vendor Device-to-Host).
* `B_REQUEST`: Control transfer request code.
* `W_VALUE`, `W_INDEX`: Transfer parameters.
* `LEN`: Expected payload length in bytes.

#### **How to Run:**
* **Windows:**
  ```powershell
  python read_vendor_dongle.py
  ```
* **Linux:**
  ```bash
  python3 read_vendor_dongle.py
  ```

#### **Output:**
* Generates [`output/dongle_key.bin`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/dongle_key.bin).

> [!NOTE]
> On Windows, vendor control transfers via PyUSB require the **WinUSB** driver bound to the device using [Zadig](https://zadig.akeo.ie/).

---

### 5. `extract_key.py`

#### **Purpose:**
Reads the raw memory blob [`output/dongle_key.bin`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/dongle_key.bin), slices the exact cryptographic key payload starting at `KEY_OFFSET` for `KEY_LEN` bytes, computes a SHA-256 verification checksum, and writes the clean key.

#### **Configuration:**
* `KEY_OFFSET`: Starting byte index of the key inside the raw dump (default: `0x00`).
* `KEY_LEN`: Length of the final key in bytes (default: `32`).

#### **How to Run:**
* **Windows:**
  ```powershell
  python extract_key.py
  ```
* **Linux:**
  ```bash
  python3 extract_key.py
  ```

#### **Output:**
* Prints the extracted key hex string and its 4-byte checksum.
* Writes [`output/key.bin`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/key.bin).

---

### 6. Automated Pipeline Runners: `run.ps1` & `run.sh`

#### **Purpose:**
Orchestrates the entire export workflow end-to-end automatically:
1. Validates or initializes the virtual environment (`.venv/`).
2. Installs required dependencies (`requirements.txt`).
3. Runs device enumeration (`enum_dongle.py`).
4. Executes the primary HID reader (`read_hid_dongle.py`) with automatic fallback to vendor control transfers (`read_vendor_dongle.py`).
5. Extracts and checksums the final key into [`output/key.bin`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/key.bin).

#### **How to Run:**
* **On Windows (PowerShell):**
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\run.ps1
  ```
* **On Linux (Bash):**
  ```bash
  chmod +x run.sh
  ./run.sh
  ```

---

## Output Verification

After executing the pipeline, verify the files in [`output/`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/):

| File | Expected Size | Verification Criteria |
|---|---|---|
| [`output/dongle_key.bin`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/dongle_key.bin) | Matches `LEN` (e.g. 64 bytes) | Identical contents across repeated reads |
| [`output/key.bin`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/key.bin) | Matches `KEY_LEN` (e.g. 32 bytes) | Verified SHA-256 checksum prefix |
| [`output/dongle_model_info.txt`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/dongle_model_info.txt) | Text report | Matches device `VID:PID` and descriptor tree |

---

## Detailed Documentation Guides

For in-depth explanations, refer to the guides in [`docs/`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/docs/):
* 📖 [**Step-by-Step Workflow Guide**](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/docs/step-by-step.md): Complete walkthrough of setup, protocol tuning, and troubleshooting.
* 📖 [**Dongle Model Identification Workflow**](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/docs/check-dongle.md): In-depth scanning reference for PyUSB and HIDAPI layers.
* 📖 [**Hardware Sourcing & Purchasing Guide**](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/docs/purchasing-guide.md): Details on manufacturer contacts, marketplace search terms, and flashing blank replacement keys.
