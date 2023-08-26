#!/usr/bin/env bash
echo "Creating application"
pyinstaller main.py --clean --onefile --distpath bank_transaction_analyzer_app  --name bank-transaction-analyzer-app
cp config.json ./bank_transaction_analyzer_app/
cp -r test_data ./bank_transaction_analyzer_app/
cp README.md ./bank_transaction_analyzer_app/
zip -r bank_transaction_analyzer_app.zip bank_transaction_analyzer_app/

