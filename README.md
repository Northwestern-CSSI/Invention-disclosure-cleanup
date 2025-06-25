# PDF Extraction Tool

This tool is designed to process PDF files, specifically to identify, extract, and desensitize technology disclosure forms.

## Project Structure

```
pdf-extraction/
│
├── 00-select-disclosure.py - Script to identify and copy disclosure forms
├── 01-extract-content.py - Script to extract and export content before specific section
├── run.sh - Shell script to run the complete workflow
├── requirements.txt - Required Python packages
│
├── raw/ (INPUT)            - Directory for original PDF files organized in subdirectories
│   ├── XX-T-XXX/
│   │   ├── InventionDisclosureXXX.pdf
│   │   └── Other non-sensitive files
│   ├── XX-T-XXX/
│       ├── ...
│
├── data/ (GENERATED OUTPUT)
│   ├── invention_disclosure/     - Identified disclosure forms (PDFs)
│   ├── invention_disclosure_text/ - Extracted text files without sensitive information (.txt)
│   ├── supplementary_information/ - Non-disclosure documents (PDFs)
│   └── all_extracted_texts.parquet - Consolidated extracted content (same to `invention_disclosure_text`)
│
└── README.md               - This file
```

## Scripts

### 00-select-disclosure.py

This script processes PDF files in the `raw` directory and its subdirectories, looking for technology disclosure forms by searching for specific keywords ("TECHNOLOGY", "DISCLOSURE", "FORM") in the first page of each PDF. When it identifies a disclosure form, it copies the file to the `data/invention_disclosure` directory, and other documents to the `data/supplementary_information` directory.

### 01-extract-content.py

This script extracts text content from disclosure forms up to the section marker "III. ADDITIONAL INFORMATION & SUPPORTING DOCUMENTS". It processes all PDFs in the `data/invention_disclosure` directory and its subdirectories, and:

1. Exports individual text files to the `data/invention_disclosure_text` directory
2. Creates a pandas DataFrame with the extracted content
3. Saves the DataFrame as `all_extracted_texts.parquet`

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

## Requirements

- Python 3.x
- PyPDF2 (version 3.0.1 or higher)
- pandas (version 2.0.0 or higher)
- pyarrow (version 12.0.0 or higher)
- tqdm

## Data Directory Structure

### Input Directory
- `raw/` (INPUT): Place original PDF files here organized in subdirectories
  - Example: `raw/02-T-019/`, `raw/02-T-020/`, etc.
  - Contains mixed document types: disclosure forms and supplementary documents

### Generated Output Directories
- `data/invention_disclosure/` (GENERATED): Identified disclosure forms (PDF files)
  - Contains only PDFs identified as invention disclosure forms
  - Maintains original subdirectory structure from raw/
- `data/invention_disclosure_text/` (GENERATED): Extracted text files (.txt)
  - Contains text content extracted from disclosure forms
  - One .txt file per disclosure PDF, preserving directory structure
- `data/supplementary_information/` (GENERATED): Non-disclosure documents (PDF files)
  - Contains PDFs that were not identified as disclosure forms
  - Research papers, supporting documents, etc.
- `data/all_extracted_texts.parquet` (GENERATED): Consolidated extracted content
  - Parquet file containing all extracted text content in tabular format
  - Includes metadata like file paths and directory structure

## Running the Complete Workflow

Use the provided shell script to run the complete workflow:

```bash
./run.sh
```

This will:
1. Install required dependencies
2. Identify disclosure forms in raw PDFs and categorize them:
   - Disclosure forms → `data/invention_disclosure/`
   - Other documents → `data/supplementary_information/`
3. Extract content from disclosure forms and save to:
   - Individual text files in `data/invention_disclosure_text/`
   - Consolidated parquet file: `data/all_extracted_texts.parquet`

## Notes

- PDF files are excluded from version control via .gitignore
- The script recursively searches directories using `**/*.pdf` pattern to find PDFs in subdirectories
- The script uses a fuzzy search approach to identify disclosure forms, looking for the keywords on the same line or anywhere in the first page
- Documents not identified as disclosure forms are categorized as supplementary information
- The content extraction uses highly adaptive pattern matching to handle messy PDF text extraction
- The content extraction stops at the "III. ADDITIONAL INFORMATION & SUPPORTING DOCUMENTS" section or similar markers, using multiple strategies to identify this boundary
