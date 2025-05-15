#!/bin/bash

# Handle broken pipe errors gracefully
trap '' PIPE

echo "=== PDF Extraction and Desensitization Tool ==="

# Install requirements
pip install -r requirements.txt

# Create directories
mkdir -p "data/raw" "data/disclosure" "data/desensitized"

# Count PDFs in raw directory
PDF_COUNT=$(ls -1 "data/raw/"*.pdf 2>/dev/null | wc -l)
if [ "$PDF_COUNT" -eq 0 ]; then
    echo "No PDF files found in data/raw directory."
    echo "Please place PDF files in the data/raw directory and run again."
    exit 1
fi

echo "Found $PDF_COUNT PDF files in data/raw directory."

# Step 1: Run the disclosure form identification script
echo "Step 1: Identifying disclosure forms..."
python 00-select-disclosure.py

# Count identified disclosure forms
DISCLOSURE_COUNT=$(ls -1 "data/disclosure/"*.pdf 2>/dev/null | wc -l)
if [ "$DISCLOSURE_COUNT" -eq 0 ]; then
    echo "No disclosure forms were identified."
    echo "Process completed with no output."
    exit 0
fi

echo "Found $DISCLOSURE_COUNT disclosure forms."

# Step 2: Run the desensitization script
echo "Step 2: Desensitizing disclosure forms..."
python 01-desensitize-disclosure.py

# Count desensitized files
DESENSITIZED_COUNT=$(ls -1 "data/desensitized/"*.pdf 2>/dev/null | wc -l)
echo "Created $DESENSITIZED_COUNT desensitized documents."

echo "Process completed."
echo "Results:"
echo "- Raw PDF files: $PDF_COUNT"
echo "- Identified disclosure forms: $DISCLOSURE_COUNT"
echo "- Desensitized documents: $DESENSITIZED_COUNT"
echo "Check data/desensitized directory for final processed documents."