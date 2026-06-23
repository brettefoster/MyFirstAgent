#!/usr/bin/env bash
#
# setup.sh - Prepare the workspace for running Stage 0 examples
#
# This script:
#   1. Checks Python 3 is available
#   2. Creates a virtual environment (optional)
#   3. Installs Python dependencies
#   4. Sets up .env from .env.example if missing
#   5. Verifies the API endpoint is reachable
#
# Usage:
#   bash scripts/setup.sh
#   source .venv/bin/activate  # if using virtual environment
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo " MyFirstAgent - Environment Setup"
echo "=============================================="
echo ""

# --- 1. Check Python 3 ---
echo "[1/5] Checking Python 3..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "  ✓ $PYTHON_VERSION"
else
    echo "  ✗ Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

# --- 2. Create virtual environment (optional) ---
echo ""
echo "[2/5] Setting up virtual environment..."
VENV_DIR="$PROJECT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "  Creating virtual environment at $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
    echo "  ✓ Virtual environment created."
    echo "  To activate: source $VENV_DIR/bin/activate"
else
    echo "  ✓ Virtual environment already exists at $VENV_DIR"
fi

# Activate venv for remaining steps
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
fi

# --- 3. Install dependencies ---
echo ""
echo "[3/5] Installing Python dependencies..."
cd "$PROJECT_DIR"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "  ✗ requirements.txt not found!"
    exit 1
fi

pip install -r requirements.txt 2>&1 | tail -3
echo "  ✓ Dependencies installed."

# --- 4. Set up .env ---
echo ""
echo "[4/5] Checking .env configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "  ✓ Created .env from .env.example"
        echo "  Please edit .env to match your API configuration."
    else
        echo "  ✗ Neither .env nor .env.example found."
        exit 1
    fi
else
    echo "  ✓ .env already exists."
fi

# --- 5. Check API connectivity ---
echo ""
echo "[5/5] Checking API connectivity..."

# Read API_BASE and MODEL from .env (simple grep approach)
API_BASE=$(grep "^API_BASE=" .env 2>/dev/null | cut -d'=' -f2- || echo "http://localhost:8080")
MODEL=$(grep "^MODEL=" .env 2>/dev/null | cut -d'=' -f2- || echo "llama3")
# Append /v1/chat/completions if not already present
API_URL="${API_BASE}/v1/chat/completions"

echo "  Testing: $API_URL"

# Try a lightweight connectivity check
if command -v curl &>/dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        --connect-timeout 5 \
        --max-time 10 \
        -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"${MODEL}\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hi\"}],\"max_tokens\":10,\"stream\":false}" \
        2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        echo "  ✓ API is reachable and responded with HTTP 200."
    elif [ "$HTTP_CODE" = "000" ]; then
        echo "  ⚠ Cannot connect to API at $API_BASE"
        echo "    Make sure your API server (e.g., Ollama) is running."
        echo "    Start Ollama with:  ollama serve"
    else
        echo "  ⚠ API responded with HTTP $HTTP_CODE"
        echo "    Check your API configuration in .env"
    fi
else
    echo "  ⚠ curl not available, skipping connectivity check."
fi

# --- Done ---
echo ""
echo "=============================================="
echo " Setup Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. If you don't have a model, pull one:"
echo "     ollama pull llama3"
echo ""
echo "  2. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  3. Run an example:"
echo "     python3 examples/stage0/exercise_1.py"
echo ""