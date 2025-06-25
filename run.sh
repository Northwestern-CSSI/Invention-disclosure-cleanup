#!/bin/bash
RAW_DIR="raw"

# Set default directories
BASE_DIR="data"
DISCLOSURE_DIR="data/invention_disclosure"
DISCLOSURE_TEXT_DIR="data/invention_disclosure_text"
SUPPLEMENTARY_DIR="data/supplementary_information"

pip install -r requirements.txt

python 00-select-disclosure.py \
    --raw-dir "$RAW_DIR" \
    --disclosure-dir "$DISCLOSURE_DIR" \
    --supplementary-dir "$SUPPLEMENTARY_DIR"

python 01-extract-content.py \
    --disclosure-dir "$DISCLOSURE_DIR" \
    --disclosure-text-dir "$DISCLOSURE_TEXT_DIR" \
    --output-dir "$BASE_DIR"