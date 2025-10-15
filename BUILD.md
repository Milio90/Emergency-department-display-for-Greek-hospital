# Building Windows Executable

This guide explains how to create a standalone Windows executable for the Hospital On-Duty Display application.

## Prerequisites

- Python 3.8 or higher installed on Windows
- Git (optional, for cloning the repository)

## Method 1: Automated Build (Recommended)

### On Windows:

1. Open Command Prompt or PowerShell in the project directory
2. Run the build script:
   ```cmd
   build_windows.bat
   ```
3. The executable will be created at `dist\HospitalOnDutyDisplay.exe`

## Method 2: Manual Build

### Step 1: Install Dependencies

```cmd
pip install -r requirements.txt
```

This will install all required packages including PyInstaller.

### Step 2: Build with PyInstaller

```cmd
pyinstaller cardiology_display.spec
```

### Step 3: Locate the Executable

The executable will be created at:
```
dist\HospitalOnDutyDisplay.exe
```

## Method 3: GitHub Actions (Automated CI/CD)

Every time you push code to GitHub, a Windows executable is automatically built:

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Find the latest "Build Windows Executable" workflow run
4. Download the `HospitalOnDutyDisplay-Windows` artifact
5. Extract the ZIP file to get the `.exe` file

## Distribution

The generated executable is **fully standalone** and can be:

- Copied to any Windows computer
- Run without installing Python
- Run without installing any dependencies
- Stored on a USB drive and run directly

### What's Included

The executable bundles:
- Python runtime
- All required libraries (tkinter, PIL, pdfplumber, etc.)
- The Onassis logo image
- All Python modules (moh_scraper, shift_parser, etc.)

### File Size

The executable will be approximately 80-120 MB due to bundling Python and all dependencies.

## Configuration Files

The application will create these files in the same directory as the executable:

- `shifts_cache.json` - Cached doctor shift schedules
- `hospitals_on_duty.json` - Cached hospital data

## Troubleshooting

### Build Fails with "Module Not Found"

Make sure all dependencies are installed:
```cmd
pip install -r requirements.txt
```

### Logo Image Not Showing

Ensure `onasseio_logo.png` exists in the project directory before building.

### Executable Won't Run

- Check Windows Defender or antivirus - they may flag the executable
- Run as Administrator if you encounter permission issues
- Ensure you're running on Windows 10 or higher

### Large File Size

This is normal. PyInstaller bundles Python and all dependencies. To reduce size:
- Use UPX compression (enabled by default in the spec file)
- Remove unused dependencies from requirements.txt

## Building on Other Platforms

### Cross-Compilation Note

PyInstaller **cannot** cross-compile. To build for Windows, you must run the build on a Windows machine.

Options:
1. Use a Windows computer or VM
2. Use GitHub Actions (automatically builds on Windows in the cloud)
3. Use Wine on Linux (not recommended, may have issues)

## Version Information

To add version information to the executable:

1. Create a version info file using PyInstaller's tools
2. Update the `icon` and `version` parameters in `cardiology_display.spec`
3. Rebuild

## Icon Customization

To add a custom icon:

1. Create or obtain a `.ico` file (Windows icon format)
2. Place it in the project directory
3. Update `cardiology_display.spec`:
   ```python
   icon='path/to/your/icon.ico'
   ```
4. Rebuild

## Testing the Executable

After building:

1. Copy `dist\HospitalOnDutyDisplay.exe` to a test directory
2. Run it to ensure it starts correctly
3. Test loading shift files (DOCX)
4. Test fetching hospital data from MOH website
5. Verify all GUI features work

## Continuous Integration

This project includes GitHub Actions workflow that:
- Automatically builds Windows executables on every push
- Runs on Windows Server in the cloud
- Creates downloadable artifacts
- Can be configured to create releases

See `.github/workflows/build-windows.yml` for details.

## Support

If you encounter issues building the executable:

1. Check that Python version is 3.8+
2. Ensure all files are present (especially `cardiology_display.py`, `moh_scraper.py`, `shift_parser.py`)
3. Verify `onasseio_logo.png` exists
4. Check PyInstaller documentation: https://pyinstaller.org/

## Advanced Options

### Console Window

To show a console window for debugging, edit `cardiology_display.spec`:
```python
console=True  # Shows console window
```

### One-Folder Build

To create a folder with multiple files instead of a single exe, edit `cardiology_display.spec`:
```python
# Replace EXE() section with:
exe = EXE(
    pyz,
    a.scripts,
    [],  # Don't include everything
    exclude_binaries=True,
    name='HospitalOnDutyDisplay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HospitalOnDutyDisplay',
)
```

This creates a folder with the executable and all dependencies as separate files (faster startup, larger folder size).
