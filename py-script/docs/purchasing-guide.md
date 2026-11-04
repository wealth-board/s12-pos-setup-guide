# Hardware Identification & Dongle Purchasing Guide

A sourcing and hardware profile guide based on the device identifiers captured in [`output/dongle_model_info.md`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/dongle_model_info.md).

---

## 1. Hardware Profile

| Parameter | Value | Details |
|---|---|---|
| **Vendor ID (VID)** | `0x3689` | Registered to Dongguan Yutian Software Co., Ltd. |
| **Product ID (PID)** | `0x8762` | Password-Type Driverless USB Hardware Key |
| **Manufacturer String** | `USBKey` | Generic USB descriptor string |
| **Product Name** | `USBKey` | Generic USB descriptor string |
| **Interface Class** | `3` | HID (Human Interface Device) |
| **HID Usage Page** | `0xff00` | Vendor-defined cryptographic usage page |
| **HID Usage** | `0x01` | Primary collection |
| **Device Path** | `\\?\HID#VID_3689&PID_8762#...` | Native Windows HID device handle |

---

## 2. Model & Manufacturer Identification

* **Manufacturer:** **Dongguan Yutian Software Development Co., Ltd.** (东莞市域天软件开发有限公司)
* **Brand / Trade Names:** **YuTian (域天)**, **Syunew (域之天)**
* **Series / Model:** **YuTian Driverless Password-Type Dongle** (*域天密码型无驱加密狗* / *YT88 / D8 / USL-F2K driverless series*)
* **Purpose:** Anti-piracy software protection, hardware license verification, and internal key storage.

---

## 3. Where to Purchase

### A. Direct from the Manufacturer (OEM / Bulk / Developer Units)
Purchasing directly from the original vendor ensures authentic chips and provides access to official developer SDKs:
* **Official Website:** [www.dgyzt.com](http://www.dgyzt.com)
* **Company Name:** Dongguan Yutian Software Development Co., Ltd.
* **Sales Hotline:** `+86-769-22686137`
* **Direct Sales & WeChat:** `+86-13316642000` (梁先生 / 刘小姐)
* **Customer Support QQ:** `2180985017`
* **Address:** 27 Changning Road, Huayuan New Village, Dongcheng District, Dongguan, Guangdong, China

---

### B. Online Marketplaces (Small Quantities & Blanks)

#### **Domestic Platforms (China):**
Blank developer units typically cost between **$3–$10 USD (20–60 RMB)** each:
* **Taobao / Tmall / JD.com:**
  - Search terms:
    - `域天加密狗 密码型`
    - `域天无驱加密锁`
    - `YT88 加密锁`
    - `VID 3689 PID 8762`
* **1688.com (Alibaba Wholesale):**
  - Search term: `东莞市域天软件 密码型加密锁`

#### **International Platforms (Cross-Border Shipping):**
* **AliExpress / Made-in-China:**
  - Search terms:
    - `Yutian USB dongle`
    - `Syunew encryption lock`
    - `YT88 USB dongle`
* **Package Forwarders:**
  - If buying directly from Chinese platforms like Taobao or 1688 for international delivery, third-party forwarding services (e.g., Superbuy) can handle international shipping.

---

## 4. Programming a Replacement Dongle

> [!IMPORTANT]
> **Blank Hardware Notice:**
> Replacement units purchased from suppliers arrive as **blank programmable developer dongles**. 
> 
> * The hardware identifiers (`VID: 0x3689`, `PID: 0x8762`) will match.
> * The internal memory storage and passwords will be set to factory defaults.
> 
> To function as an exact clone or valid authorization key for your software:
> 1. Use the YuTian SDK / programming tool (e.g., `Syunew3D.dll` / developer utility).
> 2. Flash the raw data from [`output/dongle_key.bin`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/dongle_key.bin) or key from [`output/key.bin`](file:///C:/Users/onsta/Downloads/dongle-export/dongle-export/output/key.bin) into the new dongle.
> 3. Configure the corresponding Read/Write access passwords (`HKey` / `LKey`).
