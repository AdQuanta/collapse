#!/usr/bin/env bash
set -euo pipefail
VENV="${VENV:-.venv-resonant}"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"
"$PYTHON_BIN" -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r requirements.txt
"$VENV/bin/python" -m pip show quspin quspin-extensions
"$VENV/bin/python" -c "import sys, quspin, quspin_extensions; print(sys.version); print('imported QuSpin modules successfully')"
