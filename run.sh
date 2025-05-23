#!/bin/bash

# Handle broken pipe errors gracefully
trap '' PIPE

echo "=== PDF Extraction and Desensitization Tool ==="

# Set default directories
BASE_DIR="data"
RAW_DIR="${BASE_DIR}/raw"
DISCLOSURE_DIR="${BASE_DIR}/disclosure"
EXTRACTED_TEXT_DIR="${BASE_DIR}/extracted_text"
DESENSITIZED_DIR="${BASE_DIR}/desensitized"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --base-dir)
      BASE_DIR="$2"
      RAW_DIR="${BASE_DIR}/raw"
      DISCLOSURE_DIR="${BASE_DIR}/disclosure"
      EXTRACTED_TEXT_DIR="${BASE_DIR}/extracted_text"
      DESENSITIZED_DIR="${BASE_DIR}/desensitized"
      shift 2
      ;;
    --raw-dir)
      RAW_DIR="$2"
      shift 2
      ;;
    --disclosure-dir)
      DISCLOSURE_DIR="$2"
      shift 2
      ;;
    --text-dir)
      EXTRACTED_TEXT_DIR="$2"
      shift 2
      ;;
    --desensitized-dir)
      DESENSITIZED_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--base-dir path] [--raw-dir path] [--disclosure-dir path] [--text-dir path] [--desensitized-dir path]"
      exit 1
      ;;
  esac
done

echo "Using the following directories:"
echo "- Raw PDFs: $RAW_DIR"
echo "- Disclosure forms: $DISCLOSURE_DIR"
echo "- Extracted text: $EXTRACTED_TEXT_DIR"
echo "- Desensitized documents: $DESENSITIZED_DIR"

# Install requirements
pip install -r requirements.txt

# Create directories
mkdir -p "$RAW_DIR" "$DISCLOSURE_DIR" "$DESENSITIZED_DIR" "$EXTRACTED_TEXT_DIR"

# Count PDFs in raw directory (recursively)
PDF_COUNT=$(find "$RAW_DIR" -type f -name "*.pdf" | wc -l)
if [ "$PDF_COUNT" -eq 0 ]; then
    echo "No PDF files found in $RAW_DIR directory (including subdirectories)."
    echo "Please place PDF files in the $RAW_DIR directory and run again."
    exit 1
fi

echo "Found $PDF_COUNT PDF files in $RAW_DIR directory (including subdirectories)."

# Step 1: Run the disclosure form identification script
echo "Step 1: Identifying disclosure forms..."
python 00-select-disclosure.py --raw-dir "$RAW_DIR" --disclosure-dir "$DISCLOSURE_DIR"

# Count identified disclosure forms
DISCLOSURE_COUNT=$(find "$DISCLOSURE_DIR" -type f -name "*.pdf" | wc -l)
if [ "$DISCLOSURE_COUNT" -eq 0 ]; then
    echo "No disclosure forms were identified."
    echo "Process completed with no output."
    exit 0
fi

echo "Found $DISCLOSURE_COUNT disclosure forms."

# Step 2: Run the content extraction script
echo "Step 2: Extracting content from disclosure forms..."
python 01-extract-content.py --disclosure-dir "$DISCLOSURE_DIR" --text-dir "$EXTRACTED_TEXT_DIR" --output-dir "$BASE_DIR"

# Check if output files were created
PARQUET_FILE="${BASE_DIR}/disclosure_content.parquet"
CSV_FILE="${BASE_DIR}/disclosure_content.csv"

if [ -f "$PARQUET_FILE" ]; then
    echo "Successfully created content parquet file: $PARQUET_FILE"
fi

if [ -f "$CSV_FILE" ]; then
    echo "Successfully created content CSV file: $CSV_FILE"
fi

# Count extracted text files
TEXT_COUNT=$(find "$EXTRACTED_TEXT_DIR" -type f -name "*.txt" | wc -l)
echo "Created $TEXT_COUNT individual text files."

# Step 3: Run the desensitization script
echo "Step 3: Desensitizing disclosure forms..."
python 02-desensitize-disclosure.py --disclosure-dir "$DISCLOSURE_DIR" --desensitized-dir "$DESENSITIZED_DIR"

# Count desensitized files
DESENSITIZED_COUNT=$(find "$DESENSITIZED_DIR" -type f -name "*.pdf" | wc -l)
echo "Created $DESENSITIZED_COUNT desensitized documents."

echo "Process completed."
echo "Results:"
echo "- Raw PDF files: $PDF_COUNT"
echo "- Identified disclosure forms: $DISCLOSURE_COUNT" 
echo "- Extracted text files: $TEXT_COUNT"
echo "- Content tables: $PARQUET_FILE and $CSV_FILE"
echo "- Desensitized documents: $DESENSITIZED_COUNT"
echo "Check $EXTRACTED_TEXT_DIR directory for individual text files."