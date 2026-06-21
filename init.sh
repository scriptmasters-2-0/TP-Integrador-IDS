#!/bin/sh
set -eu

if ! command -v uv >/dev/null 2>&1; then
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_BIN=python3
    elif command -v python >/dev/null 2>&1; then
        PYTHON_BIN=python
    else
        echo "Error: uv no está instalado y no se encontró Python para instalarlo." >&2
        exit 1
    fi

    echo "uv no está instalado. Instalando uv con $PYTHON_BIN..."
    "$PYTHON_BIN" -m pip install --user uv

    USER_BASE=$("$PYTHON_BIN" -m site --user-base)
    export PATH="$USER_BASE/bin:$USER_BASE/Scripts:$PATH"

    if ! command -v uv >/dev/null 2>&1; then
        echo "Error: uv se instaló, pero no quedo disponible en PATH." >&2
        exit 1
    fi
fi

(
    cd app_backend
    uv sync --locked
)

(
    cd app_frontend
    uv sync --locked
)
