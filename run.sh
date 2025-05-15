#!/bin/bash

# Script to run the PDF extraction and desensitization process

# Set the base directory to the script's location
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BASE_DIR"

echo "=== PDF Extraction and Desensitization Tool ==="
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

# Step 1: Run the disclosure form identification script
echo "Step 1: Identifying disclosure forms..."
python3 00-select-disclosure.py

# Count identified disclosure forms
DISCLOSURE_COUNT=$(ls -1 data/disclosure/*.pdf 2>/dev/null | wc -l)
if [ "$DISCLOSURE_COUNT" -eq 0 ]; then
    echo "No disclosure forms were identified."
    echo "Process completed with no output."
    exit 0
fi

echo "Found $DISCLOSURE_COUNT disclosure forms."

# Step 2: Run the desensitization script
echo "Step 2: Desensitizing disclosure forms..."
python3 01-desensitize-disclosure.py

# Count desensitized files
DESENSITIZED_COUNT=$(ls -1 data/desensitized/*.pdf 2>/dev/null | wc -l)
echo "Created $DESENSITIZED_COUNT desensitized documents."

echo "Process completed."
echo "Results:"
echo "- Raw PDF files: $PDF_COUNT"
echo "- Identified disclosure forms: $DISCLOSURE_COUNT"
echo "- Desensitized documents: $DESENSITIZED_COUNT"
echo ""
echo "Check data/desensitized directory for final processed documents."