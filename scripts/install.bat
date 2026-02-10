@echo off
setlocal EnableDelayedExpansion

REM Claude Code Notifier - Windows Install Script

echo.
echo ============================================================
echo   Claude Code Notifier - Install Script
echo ============================================================
echo.

REM 프로젝트 루트로 이동
cd /d "%~dp0.."

REM Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [Error] Python is not installed.
    echo.
    echo Please install Python:
    echo   1. Download from https://www.python.org/downloads/
    echo   2. Check "Add Python to PATH" during installation
    echo   3. Run this script again
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo     Python %PYTHON_VERSION% found

REM Check Python version (3.9+)
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)
if %MAJOR% LSS 3 (
    echo [Error] Python 3.9 or higher required. Current: %PYTHON_VERSION%
    pause
    exit /b 1
)
if %MAJOR% EQU 3 if %MINOR% LSS 9 (
    echo [Error] Python 3.9 or higher required. Current: %PYTHON_VERSION%
    pause
    exit /b 1
)

REM Check existing venv
echo.
echo [2/4] Setting up virtual environment...
if exist venv (
    echo     Existing venv found
    set /p RECREATE="    Recreate virtual environment? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo     Removing old venv...
        rmdir /s /q venv
        goto CREATE_VENV
    ) else (
        echo     Using existing venv
        goto INSTALL_DEPS
    )
)

if exist .venv (
    echo     Existing .venv found
    set /p RECREATE="    Recreate virtual environment? (y/N): "
    if /i "!RECREATE!"=="y" (
        echo     Removing old .venv...
        rmdir /s /q .venv
        goto CREATE_VENV
    ) else (
        echo     Using existing .venv
        set VENV_DIR=.venv
        goto INSTALL_DEPS_EXISTING
    )
)

:CREATE_VENV
echo     Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [Error] Failed to create virtual environment
    pause
    exit /b 1
)
echo     Virtual environment created

:INSTALL_DEPS
set VENV_DIR=venv

:INSTALL_DEPS_EXISTING
echo.
echo [3/4] Installing dependencies...
call %VENV_DIR%\Scripts\activate.bat

python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo [Error] Failed to install packages
    pause
    exit /b 1
)

echo.
echo [4/4] Verifying installation...
python -c "from PyQt6.QtCore import PYQT_VERSION_STR; print(f'     PyQt6 {PYQT_VERSION_STR} installed')"
python -c "import watchdog; print('     watchdog installed')"

echo.
echo ============================================================
echo   Installation complete!
echo ============================================================
echo.
echo   To run:
echo     scripts\run.bat
echo.
echo ============================================================
echo.

pause
