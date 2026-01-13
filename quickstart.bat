@echo off
REM Quick start script for UV setup (Windows)

echo ==================================
echo Method Analysis Dashboard Setup
echo ==================================
echo.

REM Check if UV is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ UV is not installed!
    echo.
    echo Install UV with:
    echo   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    exit /b 1
)

echo ✅ UV is installed
echo.

REM Create virtual environment and install dependencies
echo 📦 Installing dependencies with UV...
uv sync
echo.

REM Run setup script
echo 🔧 Running setup script...
uv run python setup.py
echo.

echo ==================================
echo ✅ Setup complete!
echo ==================================
echo.
echo Next steps:
echo 1. Move your CSV to data/ folder
echo 2. Add your config JSON files to config/
echo 3. Edit config.py to set CSV_PATH
echo 4. Run dashboard:
echo    uv run python dashboard.py
echo.

pause
