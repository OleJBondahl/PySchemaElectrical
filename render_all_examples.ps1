$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$SrcPath = Join-Path $ProjectRoot "src"
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (Test-Path $VenvPython) {
    Write-Host "Using virtual environment: $VenvPython" -ForegroundColor Cyan
    $PythonExe = $VenvPython
} else {
    Write-Host "Using system python..." -ForegroundColor Yellow
    $PythonExe = "python"
}

$env:PYTHONPATH = "$SrcPath;$ProjectRoot"

Write-Host "Running examples module..." -ForegroundColor Cyan

try {
    & $PythonExe -m examples.example_all_circuits
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "All examples rendered successfully." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Failed to render examples. Exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "An error occurred: $_" -ForegroundColor Red
    exit 1
}
