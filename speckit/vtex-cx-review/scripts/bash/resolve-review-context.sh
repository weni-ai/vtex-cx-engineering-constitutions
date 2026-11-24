#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(CDPATH="" cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/../python/resolve_review_context.py"

if [[ -n "${SPECKIT_PYTHON_EXECUTABLE:-}" ]]; then
    exec "$SPECKIT_PYTHON_EXECUTABLE" "$PY_SCRIPT" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 "$PY_SCRIPT" "$@"
elif command -v python >/dev/null 2>&1; then
    exec python "$PY_SCRIPT" "$@"
else
    echo "ERROR: Python 3 is required to run resolve_review_context.py." >&2
    exit 1
fi
