# PDF Extraction Tool

This tool is designed to process PDF files, specifically to identify, extract, and desensitize technology disclosure forms.

## Project Structure

```
pdf-extraction/
│
├── 00-select-disclosure.py - Script to identify and copy disclosure forms
├── 01-desensitize-disclosure.py - Script to remove sensitive information from forms
├── run.sh - Shell script to run the complete workflow
├── requirements.txt - Required Python packages
│
├── data/
│   ├── raw/                - Directory for original PDF files
│   ├── disclosure/         - Directory for identified disclosure forms
│   └── desensitized/       - Directory for processed, desensitized data
│
└── README.md               - This file
```

## Scripts

### 00-select-disclosure.py

This script processes PDF files in the `data/raw` directory, looking for technology disclosure forms by searching for specific keywords ("TECHNOLOGY", "DISCLOSURE", "FORM") in the first page of each PDF. When it identifies a disclosure form, it copies the file to the `data/disclosure` directory.

#### Usage

```bash
python 00-select-disclosure.py
```

### 01-desensitize-disclosure.py

This script processes PDF files in the disclosure directory and removes sensitive personal information by identifying and removing pages that contain signature sections, contributor information, and other sensitive data. It saves the desensitized versions to the `data/desensitized` directory.

The script uses multiple approaches to identify sensitive content:
- Exact phrase matching
- Regex pattern matching
- Keyword combination scoring
- Heuristic approaches based on document structure

#### Usage

```bash
python 01-desensitize-disclosure.py
```

## Requirements

- Python 3.x
- PyPDF2 (version 3.0.1 or higher)

## Installation

```bash
pip install -r requirements.txt
```

## Data Directory Structure

- `data/raw`: Place original PDF files here for processing
- `data/disclosure`: Contains identified disclosure forms
- `data/desensitized`: Contains desensitized versions of disclosure forms

## Running the Complete Workflow

Use the provided shell script to run the complete workflow:

```bash
./run.sh
```

This will:
1. Check and install dependencies
2. Create the necessary directory structure
3. Identify disclosure forms in raw PDFs
4. Desensitize the identified disclosure forms

## Notes

- PDF files are excluded from version control via .gitignore
- The script uses a fuzzy search approach to identify disclosure forms, looking for the keywords on the same line or anywhere in the first page
- The desensitization process includes multiple fallback mechanisms to ensure sensitive content is removed even when exact markers cannot be found