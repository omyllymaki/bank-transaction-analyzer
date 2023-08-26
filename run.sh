#!/usr/bin/env bash
echo "Launching Bank Transaction Analyzer"
if [ -d "./venv/bin" ]; then
  echo "Found virtualenv venv. Using that."
  source ./venv/bin/activate
fi
if [ "$#" -eq "0" ]; then
  python main.py
else
  python main.py --config $1
fi
