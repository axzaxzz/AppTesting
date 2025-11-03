# Wave.AI Build & Installation Guide

This guide explains how to build Wave.AI into a standalone executable and create an installer.

## Prerequisites

1. **Python 3.8+** installed
2. **Git** installed
3. All dependencies from `requirements.txt` installed

## Quick Build (Recommended)

### Option 1: Automatic Build Script

Simply run the build script:

```powershell
.\build.ps1
```

This will:
- Check for PyInstaller and install if needed
- Clean previous builds
- Compile Wave.AI into a standalone executable
- Output the .exe to `dist\Wave.AI.exe`

### Option 2: Manual Build

```powershell
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller wave-ai.spec --clean --noconfirm
```

The executable will be created at: `dist\Wave.AI.exe`

## Creating an Installer

To create a professional installer for easy distribution:

### Prerequisites

Download and install **Inno Setup**: https://jrsoftware.org/isdl.php

### Steps

1. **Build the executable first** (see above)

2. **Open Inno Setup Compiler**

3. **Open the installer script:**
   - File → Open → Select `installer.iss`

4. **Compile the installer:**
   - Build → Compile (or press Ctrl+F9)

5. **Find the installer:**
   - The installer will be created in `installer_output\WaveAI-Setup-v1.0.0.exe`

### Quick Command (if ISCC is in PATH)

```powershell
iscc installer.iss
```

## Distribution

After building:

1. **Standalone Executable**: Share `dist\Wave.AI.exe` (no installation needed)
2. **Installer**: Share `installer_output\WaveAI-Setup-v1.0.0.exe` (includes uninstaller)

## File Sizes (Approximate)

- **Executable**: ~40-60 MB (includes Python runtime and dependencies)
- **Installer**: ~40-60 MB (compressed)

## Troubleshooting

### Build Fails with Import Errors

If PyInstaller fails to find modules:

```powershell
pip install --upgrade pyinstaller
pip install --upgrade -r requirements.txt
```

### Executable Won't Run

1. **Missing DLLs**: Make sure all dependencies are bundled in the spec file
2. **Antivirus**: Windows Defender may block unknown executables - add an exception
3. **Git Not Found**: Make sure Git is installed and in PATH

### Reducing File Size

To create a smaller executable, you can:

1. Remove unused dependencies from `requirements.txt`
2. Use UPX compression (already enabled in spec file)
3. Exclude unnecessary modules in `wave-ai.spec`

## Advanced Configuration

### Customizing the Build

Edit `wave-ai.spec` to:
- Add/remove bundled files in `datas`
- Add hidden imports in `hiddenimports`
- Change executable name
- Enable/disable console window

### Customizing the Installer

Edit `installer.iss` to:
- Change app name, version, publisher
- Add more files to include
- Customize installation directory
- Add registry entries
- Create file associations

## Build Optimization

For production builds:

```powershell
# Clean build with optimizations
pyinstaller wave-ai.spec --clean --noconfirm

# Test the executable
.\dist\Wave.AI.exe

# Create installer
iscc installer.iss
```

## Signing the Executable (Optional)

For production distribution, consider code signing:

```powershell
# Using signtool (requires certificate)
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\Wave.AI.exe
```

## CI/CD Integration

For automated builds, you can use GitHub Actions:

```yaml
- name: Build with PyInstaller
  run: |
    pip install pyinstaller
    pyinstaller wave-ai.spec --clean --noconfirm
    
- name: Create Installer
  run: |
    iscc installer.iss
```

## Notes

- **First Run**: The app will create `config` and `logs` directories on first run
- **Updates**: Users can simply replace the .exe file or reinstall
- **Uninstall**: If using the installer, uninstall via Windows Settings
- **Portable**: The executable can run from any location (portable mode)

## Getting Help

If you encounter issues:
1. Check the build logs in the terminal
2. Review PyInstaller documentation: https://pyinstaller.org/
3. Check Inno Setup documentation: https://jrsoftware.org/ishelp/

## License

This build system is part of Wave.AI and follows the same MIT License.
