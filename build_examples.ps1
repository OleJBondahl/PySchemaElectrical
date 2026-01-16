$ErrorActionPreference = "Stop"

Write-Host "Building all examples..." -ForegroundColor Cyan

# Run the example_all_circuits.py module from the project root
# Using 'uv run' to ensure the environment is correct
try {
    uv run python -m examples.example_all_circuits
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully built all examples." -ForegroundColor Green
    } else {
        Write-Host "Failed to build examples. Exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "An error occurred execution: $_" -ForegroundColor Red
    exit 1
}
