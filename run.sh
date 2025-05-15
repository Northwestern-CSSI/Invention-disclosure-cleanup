#!/bin/bash

# Script to run the PDF extraction process

# Set the base directory to the script's location
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BASE_DIR"

echo "=== PDF Extraction Tool ==="
echo "Working directory: $BASE_DIR"

# Check if Python and required packages are installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Install requirements if needed
echo "Checking requirements..."
if ! pip list | grep -q "PyPDF2"; then
    echo "Installing required packages..."
    pip install -r requirements.txt
else
    echo "Requirements already installed."
fi

# Create directory structure if it doesn't exist
mkdir -p data/raw data/disclosure data/desensitized

# Count PDFs in raw directory
PDF_COUNT=$(ls -1 data/raw/*.pdf 2>/dev/null | wc -l)
if [ "$PDF_COUNT" -eq 0 ]; then
    echo "No PDF files found in data/raw directory."
    echo "Please place PDF files in the data/raw directory and run again."
    exit 1
fi

echo "Found $PDF_COUNT PDF files in data/raw directory."
echo "Starting processing..."

# Run the disclosure form identification script
python3 00-select-disclosure.py

echo "Process completed."
echo "Check data/disclosure directory for identified disclosure forms."