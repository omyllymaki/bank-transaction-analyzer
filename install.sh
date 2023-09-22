#!/usr/bin/env bash

echo "Find Python"
if ! hash python; then
  echo "Python is not installed"
  exit 1
fi

ver=$(python3 -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
if [ "$ver" -lt "38" ]; then
  echo "This app requires python 3.6 or greater"
  exit 1
else
  echo "Found suitable Python version for app"
fi

echo "Create virtualenv and install requirements"
pip3 install virtualenv
virtualenv -p python3 venv
source venv/bin/activate
pip3 install -r requirements.txt
