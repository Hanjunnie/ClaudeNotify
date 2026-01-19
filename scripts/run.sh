#!/bin/bash
# Claude Code Notifier - Run Script (macOS/Linux)

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.."

if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "[Error] Virtual environment not found."
    echo "        Please run scripts/install.sh first."
    exit 1
fi

nohup python3 src/main.py "$@" > /dev/null 2>&1 &
disown
