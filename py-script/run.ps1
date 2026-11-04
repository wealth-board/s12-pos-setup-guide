$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) { python -m venv .venv }
& .\.venv\Scripts\Activate.ps1
pip install --quiet -r requirements.txt

python enum_dongle.py
if ($LASTEXITCODE -ne 0) { Write-Host "enum failed, continuing" }
python read_hid_dongle.py
if ($LASTEXITCODE -ne 0) { python read_vendor_dongle.py }
python extract_key.py
