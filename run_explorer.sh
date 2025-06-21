#!/bin/bash
# Script to run the Hand History Explorer with virtual environment

# Change to the project directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the application
python scripts/hh_explorer.py 