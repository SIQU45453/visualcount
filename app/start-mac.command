#!/bin/bash
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  echo "First start: setting up, this takes a few minutes..."
  python3 -m venv .venv || { echo "Python not found. Install it from python.org"; read; exit 1; }
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install -r requirements.txt
fi
.venv/bin/python server.py
