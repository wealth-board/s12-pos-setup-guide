# Running the S12 POS on Linux with Wine

> **Status: untested.** Nobody has run this POS under Wine yet. This page explains what should work, what probably won't, and how to try it. Follow it as an experiment. For a till that has to work every day, use Windows, or Windows in a virtual machine (see [Alternatives](#alternatives)).

## Why it's not straightforward

The S12 POS is a 32-bit Windows program (`PE32` executable), built with Delphi. The installer is NSIS. It talks to SQL Server through **FireDAC** and **ODBC Driver 17 for SQL Server**; you can see both in the [database upgrade error log](../images/07-database-upgrade-error-log.png). The vendor only supports Windows.

[Wine](https://www.winehq.org/) runs Windows programs on Linux without Windows. Delphi programs often run well under Wine. The risky parts are the ones a till depends on:

| Part | Likely under Wine | Notes |
|---|---|---|
| Installer (NSIS) | ✅ Usually works | |
| POS screens (Delphi UI) | ✅ Probably works | Install fonts for Chinese text (see below) |
| Database connection (ODBC → SQL Server) | ⚠️ Uncertain | **The biggest risk.** See [Step 4](#step-4-get-the-database-connection-working) |
| Barcode scanner | ✅ Works | USB scanners act like a keyboard |
| Receipt printer | ⚠️ Possible | Through CUPS, or by mapping a COM port |
| Cash drawer | ⚠️ Possible | Usually opened through the receipt printer |
| Licence / activation | ⚠️ Uncertain | The licence is tied to a **Hardware ID**, which Wine may report differently or change between Wine versions |
| SQL Server itself | ❌ Not under Wine | Run SQL Server **natively** on Linux instead (see [remote-database.md](remote-database.md)) |

## Step 1: Install Wine

Ubuntu / Debian / Mint:

```bash
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install wine wine32 wine64 winetricks
wine --version
```

Fedora: `sudo dnf install wine winetricks`

A newer Wine release (9.0 or later) has better ODBC support than older ones. If your distro's version is old, use the [WineHQ packages](https://gitlab.winehq.org/wine/wine/-/wikis/Download).

## Step 2: Create a separate Wine prefix for the POS

A prefix is a self-contained "fake Windows" folder. Using one just for the POS stops other programs from interfering with it.

```bash
export WINEPREFIX="$HOME/.wine-s12pos"
winecfg            # creates the prefix; set "Windows version" to Windows 10, then OK
winetricks -q corefonts cjkfonts   # Latin and Chinese fonts for the POS screens
```

Run `export WINEPREFIX="$HOME/.wine-s12pos"` in every new terminal before you run the commands below.

## Step 3: Install the POS

```bash
cd ~/Downloads/启明星多语言软件     # wherever you extracted the bundle
wine "../╞Ї├ў╨╟╢р╙я╤╘╚э╝■/POS_OM_ML 12.5-B16.8290.exe"
```

The installer is in the folder with the garbled name. Go through the installer as you would on Windows.

## Step 4: Get the database connection working

SQL Server can't run under Wine. Run it **natively** on Linux (or on another computer) and connect the POS to it over the network. [remote-database.md](remote-database.md) explains how to set that up; on the same laptop, use Docker.

The POS then needs a working SQL Server **ODBC driver** inside Wine. Try these in order:

### Option A: Wine's ODBC bridge to the Linux driver (try this first)

Wine's own `odbc32.dll` can pass ODBC calls through to drivers installed on Linux (unixODBC). Microsoft publishes a Linux build of ODBC Driver 17:

```bash
# Ubuntu 22.04 example: see Microsoft's "Install the Microsoft ODBC driver for SQL Server (Linux)" page for other distros
curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
curl -sSL https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt update
sudo ACCEPT_EULA=Y apt install msodbcsql17 unixodbc
odbcinst -q -d      # should list "ODBC Driver 17 for SQL Server"
```

The POS asks for the driver by name ("ODBC Driver 17 for SQL Server"), so this may work with no further changes.

> **Note:** the POS is a 32-bit program, and Microsoft only ships a 64-bit Linux driver. Newer Wine versions (with "WoW64" mode) can bridge 32-bit programs to 64-bit Linux libraries, but this is the most likely place for things to fail.

### Option B: the Windows driver inside Wine

On the POS's **Database Setting → Advanced Options (SQL)** tab, click **Install SQL Server Native Client**. Or download the **x86** `msodbcsql.msi` (ODBC Driver 17) from Microsoft and run:

```bash
wine msiexec /i msodbcsql.msi
```

Windows ODBC driver installers often fail under Wine, so expect this to need some troubleshooting.

### Test the connection

In **Database Setting**, use the database server's IP address, not `.\SQLEXPRESS`:

| Field | Value |
|---|---|
| Main Address | `127.0.0.1,1433` (SQL Server on the same laptop) or `<server-ip>,1433` |
| User Name / Password | `sa` / your password |
| Database Name | `POS` |

Click **Server Connection Test** and then **Database Test**.

## Step 5: Printers and the cash drawer

- **Network or USB receipt printer:** add it in CUPS (`http://localhost:631`), as a **raw** queue if the POS sends ESC/POS commands. Wine shows CUPS printers to Windows programs automatically.
- **Serial (COM) printer or USB-serial adapter:** map it to a COM port:
  ```bash
  ln -s /dev/ttyUSB0 "$WINEPREFIX/dosdevices/com1"
  sudo usermod -aG dialout "$USER"     # then log out and back in
  ```
- **Cash drawer:** most are wired to the receipt printer and open when the printer gets a "kick" command. If printing works, the drawer usually works too.

## Step 6: Start the POS

```bash
WINEPREFIX="$HOME/.wine-s12pos" wine "$WINEPREFIX/drive_c/Program Files/<POS install folder>/<pos>.exe"
```

The installer normally creates a desktop launcher as well.

## Before you rely on it

Go through this list before you serve customers with it:

- [ ] Log in, ring up a sale and print a receipt
- [ ] Open the cash drawer
- [ ] Scan barcodes
- [ ] Run a refund and an end-of-day report
- [ ] Restart the laptop and check that it all still works
- [ ] **Activation:** check that the licence stays valid after a reboot and after updating Wine. A changed Hardware ID may mean asking the vendor to re-activate.
- [ ] Remember the vendor **won't support** a Wine setup

## Alternatives

| Option | Reliability | Notes |
|---|---|---|
| **Windows virtual machine** (virt-manager/KVM, VirtualBox) | ✅ High | Real Windows, so everything in the [main guide](../README.md) applies. Pass the USB printer and scanner through to the VM. Needs a Windows licence and about 4 GB RAM for the VM. |
| **Linux database server + Windows tills** | ✅ High | See [remote-database.md](remote-database.md). Linux hosts the data, the tills run Windows. |
| **Wine** (this page) | ⚠️ Unknown | No Windows licence needed. Unsupported. |

**Recommendation:** for a till that takes real customers' money, use Windows or a Windows VM. Use Wine only if you can test it fully first and live with problems you'll have to fix yourself.
