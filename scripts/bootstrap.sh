#!/usr/bin/env bash
# Agent-CLI bootstrap — from zero to working `hl` command.
# Usage: bash scripts/bootstrap.sh
set -euo pipefail

PYTHON="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

echo "=== Agent-CLI Bootstrap ==="

# 1. Check Python version (>=3.9)
PY_VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "none")
if [ "$PY_VERSION" = "none" ]; then
    echo "ERROR: python3 not found. Install Python 3.9+."
    exit 1
fi

PY_MAJOR=$($PYTHON -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$($PYTHON -c 'import sys; print(sys.version_info.minor)')
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 9 ]; }; then
    echo "ERROR: Python 3.9+ required (found $PY_VERSION)"
    exit 1
fi
echo "OK  Python $PY_VERSION"

# 2. Create venv if not in one
if [ -z "${VIRTUAL_ENV:-}" ]; then
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating venv at $VENV_DIR ..."
        $PYTHON -m venv "$VENV_DIR"
    fi
    echo "Activating $VENV_DIR ..."
    source "$VENV_DIR/bin/activate"
else
    echo "OK  Already in venv: $VIRTUAL_ENV"
fi

# 3. Install package
echo "Installing agent-cli ..."
pip install -e . --quiet 2>&1 | tail -3

# 4. Verify
echo ""
echo "=== Verification ==="
python3 -m cli.main setup check

echo ""
echo "=== Bootstrap Complete ==="
echo "Activate venv:  source $VENV_DIR/bin/activate"
echo "Next steps:     hl wallet auto  (or hl wallet import --key <key>)"
