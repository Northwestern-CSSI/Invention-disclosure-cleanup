#!/bin/bash

# Handle broken pipe errors gracefully
trap '' PIPE

echo "=== PDF Extraction and Desensitization Tool ==="

# Install requirements
pip install -r requirements.txt

# Create directories
mkdir -p "data/raw" "data/disclosure" "data/desensitized" "data/extracted_text"

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

# Step 2: Run the content extraction script
echo "Step 2: Extracting content from disclosure forms..."
python 01-extract-content.py

# Check if output files were created
if [ -f "data/disclosure_content.parquet" ]; then
    echo "Successfully created content parquet file."
fi

if [ -f "data/disclosure_content.csv" ]; then
    echo "Successfully created content CSV file."
fi

# Count extracted text files
TEXT_COUNT=$(ls -1 "data/extracted_text/"*.txt 2>/dev/null | wc -l)
echo "Created $TEXT_COUNT individual text files."

# Step 3: Run the desensitization script
echo "Step 3: Desensitizing disclosure forms..."
python 02-desensitize-disclosure.py

# Count desensitized files
DESENSITIZED_COUNT=$(ls -1 "data/desensitized/"*.pdf 2>/dev/null | wc -l)
echo "Created $DESENSITIZED_COUNT desensitized documents."

echo "Process completed."
echo "Results:"
echo "- Raw PDF files: $PDF_COUNT"
echo "- Identified disclosure forms: $DISCLOSURE_COUNT" 
echo "- Extracted text files: $TEXT_COUNT"
echo "- Content tables: data/disclosure_content.parquet and data/disclosure_content.csv"
echo "- Desensitized documents: $DESENSITIZED_COUNT"
echo "Check data/extracted_text directory for individual text files."