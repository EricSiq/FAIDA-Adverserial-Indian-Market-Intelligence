@echo off
setlocal enabledelayedexpansion

title FAIDA - Financial Adversarial Indian Data Agents

echo =====================================================================
echo   FAIDA: Financial Adversarial Indian Data Agents
echo   Offline-First Red Team for Indian Capital Markets
echo =====================================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python 3 is not found in your system PATH.
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

:: 2. Check or create virtual environment
if not exist ".venv" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [*] Virtual environment created successfully.
)

:: 3. Activate virtual environment
call .venv\Scripts\activate.bat

:: 4. Check/Install dependencies
echo [*] Checking and updating dependencies...
where uv >nul 2>nul
if %errorlevel% equ 0 (
    echo [*] Detected uv, installing lightning fast...
    uv pip install -q -r requirements.txt --python .venv\Scripts\python.exe
) else (
    python -m pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
)
if %errorlevel% neq 0 (
    echo [ERROR] Dependency installation failed. Check your internet connection.
    pause
    exit /b 1
)

:: 5. Check local Ollama status
echo [*] Checking local Ollama service...
curl -s http://127.0.0.1:11434/api/tags >nul 2>nul
if %errorlevel% neq 0 (
    echo [NOTE] Ollama service not detected on 127.0.0.1:11434.
    echo If you wish to use local inference, please start Ollama ('ollama serve').
    echo You can also use cloud inference via Groq API.
) else (
    echo [OK] Local Ollama is running and accessible.
)

echo.
echo [*] Launching FAIDA Desktop App...
python main.py

pause
