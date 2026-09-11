#!/usr/bin/env bash
# =====================================================================
#   FAIDA: Financial Adversarial Indian Data Agents
#   Offline-First Red Team for Indian Capital Markets
#   Cross-Platform Unix/Linux/macOS Launcher
# =====================================================================

set -e

echo "====================================================================="
echo "  FAIDA: Financial Adversarial Indian Data Agents"
echo "  Offline-First Red Team for Indian Capital Markets"
echo "====================================================================="
echo ""

# 1. Detect Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3 is not found in your system PATH."
    echo "Please install Python 3.10+ (Python 3.11 recommended) from https://www.python.org/"
    exit 1
fi

echo "[*] Using Python: $($PYTHON_CMD --version)"

# 2. Check or create virtual environment
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    $PYTHON_CMD -m venv .venv
    echo "[*] Virtual environment created successfully."
fi

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Check/Install dependencies
echo "[*] Checking and updating dependencies..."
if command -v uv &>/dev/null; then
    echo "[*] Detected uv, installing lightning fast..."
    uv pip install -q -r requirements.txt --python .venv/bin/python
else
    python -m pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
fi

# 5. Check local Ollama status
echo "[*] Checking local Ollama service..."
if curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "[OK] Local Ollama is running and accessible on 127.0.0.1:11434."
else
    echo "[NOTE] Ollama service not detected on 127.0.0.1:11434."
    echo "If you wish to use local offline inference, start Ollama ('ollama serve')."
    echo "You can also use cloud inference via Groq API by setting GROQ_API_KEY."
fi

echo ""
echo "[*] Launching FAIDA Desktop App..."
python main.py "$@"
