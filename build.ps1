# Wave.AI Build Script
# Compiles the application into a standalone executable

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Wave.AI Build Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
Write-Host "Checking for PyInstaller..." -ForegroundColor Yellow
$pyinstallerCheck = python -m pip show pyinstaller 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install PyInstaller" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "PyInstaller is installed" -ForegroundColor Green
}

Write-Host ""

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
Write-Host "Cleanup complete" -ForegroundColor Green

Write-Host ""

# Build the executable
Write-Host "Building Wave.AI executable..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
Write-Host ""

python -m PyInstaller wave-ai.spec --clean --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "  Build Successful!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: dist\Wave.AI.exe" -ForegroundColor Cyan
    Write-Host ""
    
    # Check file size
    if (Test-Path "dist\Wave.AI.exe") {
        $fileSize = (Get-Item "dist\Wave.AI.exe").Length / 1MB
        Write-Host "Executable size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "To run the application:" -ForegroundColor Yellow
    Write-Host "  .\dist\Wave.AI.exe" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host "  Build Failed!" -ForegroundColor Red
    Write-Host "=====================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check the error messages above" -ForegroundColor Yellow
    exit 1
}
