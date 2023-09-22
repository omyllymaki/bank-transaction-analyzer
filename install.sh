#!/usr/bin/env bash

echo "Find Python"
if ! hash python3; then
  echo "Python3 is not installed"
  exit 1
fi

echo "Create virtualenv and install requirements"
pip3 install virtualenv
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
