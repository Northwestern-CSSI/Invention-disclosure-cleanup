<<<<<<< HEAD
# PDF Extraction Tool

This tool is designed to process PDF files, specifically to identify and extract technology disclosure forms.

## Project Structure

```
pdf-extraction/
│
├── 00-select-disclosure.py - Script to identify and copy disclosure forms
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

## Requirements

- Python 3.x
- PyPDF2 (version 3.0.1 or higher)

## Installation

```bash
pip install PyPDF2
```

## Data Directory Structure

- `data/raw`: Place original PDF files here for processing
- `data/disclosure`: Contains identified disclosure forms
- `data/desensitized`: Reserved for processed/desensitized data

## Notes

- PDF files are excluded from version control via .gitignore
- The script uses a fuzzy search approach to identify disclosure forms, looking for the keywords on the same line or anywhere in the first page
=======
# UChicago-Disclosure
>>>>>>> ddbb7b971197a8e5b4c214bb6273f23ee0859c08
