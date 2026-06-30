#!/bin/bash

# Navigate to the directory where this script is located
cd "$(dirname "$0")"

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment (.venv) not found! Installing..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install .
else
    source .venv/bin/activate
fi

# Run the tool
echo "Launching ciscoreset..."
ciscoreset
