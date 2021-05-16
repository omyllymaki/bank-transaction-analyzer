#!/usr/bin/env bash
echo "Launching Bank Transaction Analyzer"
source ./venv/bin/activate
if [ "$#" -eq "0" ]; then
  python main.py
else
  python main.py --config $1
fi
