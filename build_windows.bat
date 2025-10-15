@echo off
REM Build script for creating Windows executable
REM This script uses PyInstaller to create a standalone .exe file

echo ========================================
echo Hospital On-Duty Display - Windows Build
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo Step 3: Building executable with PyInstaller...
pyinstaller cardiology_display.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo The executable can be found at:
echo   dist\HospitalOnDutyDisplay.exe
echo.
echo You can copy this file to any Windows computer
echo and run it without installing Python.
echo.
pause
