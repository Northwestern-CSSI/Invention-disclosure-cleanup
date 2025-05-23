# PDF Extraction Tool

This tool is designed to process PDF files, specifically to identify, extract, and desensitize technology disclosure forms.

## Project Structure

```
pdf-extraction/
│
├── 00-select-disclosure.py - Script to identify and copy disclosure forms
├── 01-extract-content.py - Script to extract and export content before specific section
├── 02-desensitize-disclosure.py - Script to remove sensitive information from forms
├── run.sh - Shell script to run the complete workflow
├── requirements.txt - Required Python packages
│
├── data/
│   ├── raw/                - Directory for original PDF files
│   ├── disclosure/         - Directory for identified disclosure forms
│   ├── extracted_text/     - Directory for individual text files
│   ├── desensitized/       - Directory for processed, desensitized data
│   ├── disclosure_content.parquet - Parquet file with extracted content
│   └── disclosure_content.csv - CSV file with extracted content
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

### 01-extract-content.py

This script extracts text content from disclosure forms up to the section marker "III. ADDITIONAL INFORMATION & SUPPORTING DOCUMENTS". It processes all PDFs in the `data/disclosure` directory and:

1. Exports individual text files to the `data/extracted_text` directory
2. Creates a pandas DataFrame with the extracted content
3. Saves the DataFrame as both parquet and CSV formats

The script uses highly advanced adaptive matching techniques:

1. **Fuzzy Text Matching**:
   - Normalizes text to handle inconsistent spacing and casing
   - Uses `difflib` sequence matching with similarity thresholds
   - Performs line-by-line and sliding window analysis

2. **Multi-strategy Pattern Detection**:
   - Regular expressions with flexible whitespace handling
   - Roman numeral/numeric detection (III or 3)
   - Section header identification with context analysis
   - Line length analysis to distinguish headers from body text

3. **Structural Document Analysis**:
   - Page-by-page analysis for documents with clear section divisions
   - Section numbering pattern detection
   - Analysis of section sizes and distributions

4. **Progressive Fallback Strategies**:
   - Tries multiple approaches in sequence, from most precise to most general
   - Adapts to different document structures and formatting styles

#### Usage

```bash
python 01-extract-content.py
```

### 02-desensitize-disclosure.py

This script processes PDF files in the disclosure directory and removes sensitive personal information by identifying and removing pages that contain signature sections, contributor information, and other sensitive data. It saves the desensitized versions to the `data/desensitized` directory.

The script uses multiple approaches to identify sensitive content:
- Exact phrase matching
- Regex pattern matching
- Keyword combination scoring
- Heuristic approaches based on document structure

#### Usage

```bash
python 02-desensitize-disclosure.py
```

## Requirements

- Python 3.x
- PyPDF2 (version 3.0.1 or higher)
- pandas (version 2.0.0 or higher)
- pyarrow (version 12.0.0 or higher)
- tqdm

## Installation

```bash
pip install -r requirements.txt
```

## Data Directory Structure

- `data/raw`: Place original PDF files here for processing
- `data/disclosure`: Contains identified disclosure forms
- `data/extracted_text`: Contains individual text files with extracted content
- `data/disclosure_content.parquet`: Parquet file with extracted content
- `data/disclosure_content.csv`: CSV file with extracted content
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
4. Extract content from disclosure forms and save to:
   - Individual text files in `data/extracted_text`
   - Parquet and CSV files for tabular access
5. Desensitize the identified disclosure forms

## Notes

- PDF files are excluded from version control via .gitignore
- The script uses a fuzzy search approach to identify disclosure forms, looking for the keywords on the same line or anywhere in the first page
- The content extraction uses highly adaptive pattern matching to handle messy PDF text extraction
- The content extraction stops at the "III. ADDITIONAL INFORMATION & SUPPORTING DOCUMENTS" section or similar markers, using multiple strategies to identify this boundary
- The desensitization process includes multiple fallback mechanisms to ensure sensitive content is removed even when exact markers cannot be found