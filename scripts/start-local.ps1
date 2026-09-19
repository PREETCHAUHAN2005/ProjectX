# Local SIH demo: FastAPI :8000 + Vite :5173
# Usage:  powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$env:PYTHONPATH = "$Root;$Root\backend"
$env:DEMO_MODE = "true"
$env:APP_ENV = "development"
$env:EMOTION_BACKEND = "lexicon"
$env:DEMO_INGEST = "auto"

Write-Host "ProjectX local demo"
Write-Host "  API:        http://127.0.0.1:8000/health"
Write-Host "  Dashboard:  http://127.0.0.1:5173"
Write-Host ""

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  throw "Python is not on PATH. Install Python 3.11+ and retry."
}

if (-not (Test-Path "$Root\.venv\Scripts\python.exe")) {
  Write-Host "Creating .venv ..."
  python -m venv "$Root\.venv"
}

& "$Root\.venv\Scripts\python.exe" -m pip install --upgrade pip
& "$Root\.venv\Scripts\python.exe" -m pip install -r "$Root\backend\requirements.txt" -r "$Root\workers\requirements.txt"

if (-not (Test-Path "$Root\frontend\node_modules")) {
  Write-Host "Installing frontend dependencies ..."
  npm --prefix "$Root\frontend" install
}

Write-Host "Starting FastAPI on :8000 ..."
$api = Start-Process -PassThru -NoNewWindow -WorkingDirectory "$Root\backend" -FilePath "$Root\.venv\Scripts\python.exe" -ArgumentList @(
  "-m", "uvicorn", "app.main:app",
  "--host", "127.0.0.1",
  "--port", "8000"
)

Start-Sleep -Seconds 2
Write-Host "Starting dashboard on :5173 ..."
try {
  npm --prefix "$Root\frontend" run dev -- --host 127.0.0.1 --port 5173
} finally {
  if ($api -and -not $api.HasExited) {
    Stop-Process -Id $api.Id -Force
  }
}
