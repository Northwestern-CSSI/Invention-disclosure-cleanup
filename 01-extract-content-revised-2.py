import os
import re
import PyPDF2
import pandas as pd
import glob
import difflib
import argparse
from tqdm import tqdm
from pathlib import Path


# section markers
section_markers = [
    "iii. additional information & supporting documents",
    "iii additional information & supporting documents",
    "iii. additional information and supporting documents",
    "iii additional information and supporting documents",
    "iii. additional information",
    "iii additional information",
    "additional information & supporting documents",
    "additional information and supporting documents",
    "section iii additional information",
    "section iii: additional information",
    "3. additional information"
]

# threshold for fuzzy matching
threshold = 0.8



def normalize_text(text):
    # remove all repeated whitespaces into single space
    text = text.lower()
    while True:
        new_text = text.replace("  ", " ")
        if new_text == text:
            break
        text = new_text
    return text


def find_section_marker_fuzzy(text, markers, threshold=threshold):
    """Use fuzzy matching to find section markers in text."""
    text_normalized = normalize_text(text)
    lines = text_normalized.splitlines()
    
    # Try to find a close match for each marker
    for marker in markers:
        marker_normalized = normalize_text(marker)
        
        # Try by lines (more accurate for section headers)
        for i, line in enumerate(lines):
            line_normalized = normalize_text(line)
            
            # First try exact substring match
            if marker_normalized in line_normalized:
                return "\n".join(lines[:i])
            
            # Then try fuzzy ratio matching
            if len(line_normalized) > 5:  # Avoid matching very short lines
                similarity = difflib.SequenceMatcher(None, marker_normalized, line_normalized).ratio()
                if similarity >= threshold:
                    return "\n".join(lines[:i])
    
    return None

def approximate_original_position(original_text, normalized_text, normalized_pos):
    """Approximate the position in the original text based on the normalized position."""
    # Calculate the ratio of positions
    if len(normalized_text) == 0:
        return 0
        
    ratio = len(original_text) / len(normalized_text)
    approx_pos = int(normalized_pos * ratio)
    
    # Ensure the position is within bounds
    return min(approx_pos, len(original_text) - 1)

def extract_text_until_section(pdf_path):
    """
    Extract text from a PDF file until the section marker 
    "III. ADDITIONAL INFORMATION & SUPPORTING DOCUMENTS"
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            full_text = ""
            page_texts = []  # Keep individual page texts
            
            # Extract text from all pages
            for page in reader.pages:
                page_text = page.extract_text()
                full_text += page_text + "\n"
                page_texts.append(page_text)
            
            # Define target section markers

            
            # Try multiple approaches for finding the section
            
            # 1. First try fuzzy matching approach
            result = find_section_marker_fuzzy(full_text, section_markers)
            if result:
                return result.strip()
            
            return None
    
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return ""

def get_containing_line(text, position):
    """Get the line containing the given position in the text."""
    start = text.rfind('\n', 0, position) + 1
    end = text.find('\n', position)
    if end == -1:
        end = len(text)
    return text[start:end]

def find_pdf_files(directory):
    """Find all PDF files in a directory and its subdirectories."""
    pdf_files = []
    # Use Path.rglob for recursive glob pattern matching
    for file_path in Path(directory).rglob("*.pdf"):
        pdf_files.append(str(file_path))
    return pdf_files

def process_pdfs(disclosure_dir, disclosure_text_dir, output_dir):
    """Process PDFs and extract text before the section marker."""
    print(f"Starting content extraction from {disclosure_dir}...")
    
    # Create output directories
    os.makedirs(disclosure_text_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all PDF files in disclosure directory and subdirectories
    pdf_files = find_pdf_files(disclosure_dir)
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Create DataFrame to store results
    data = []
    
    # Process each PDF with progress bar
    for pdf_path in tqdm(pdf_files, desc="Extracting content", unit="file"):
        # txt_filename = pdf_path.replace(disclosure_dir, disclosure_text_dir).replace(".pdf", ".txt")
        rel_path = os.path.relpath(pdf_path, disclosure_dir)
        parts = Path(rel_path).parts
        clean_parts = [p + "-clean" if i == 0 else p for i, p in enumerate(parts[:-1])]
        clean_filename = Path(*clean_parts) / (Path(parts[-1]).stem + ".txt")
        txt_filename = Path(disclosure_text_dir) / clean_filename
        txt_filename = str(txt_filename)

        text = extract_text_until_section(pdf_path)
        
        if text:
            # Save to DataFrame
            data.append({
                'filename': txt_filename,
                'text': text
            })

            # Ensure the directory exists for the text file
            os.makedirs(os.path.dirname(txt_filename), exist_ok=True)
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(text)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    print(f"Extracted content from {len(data)} files")
    return df

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Extract content from disclosure forms")
    parser.add_argument("--disclosure-dir", default="data/invention_disclosure", help="Directory containing disclosure forms")
    parser.add_argument("--disclosure-text-dir", default="data/invention_disclosure_txt", help="Directory to save extracted text files")
    parser.add_argument("--output-dir", default="data", help="Directory to save output parquet and CSV files")
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Process PDFs and get DataFrame
    df = process_pdfs(args.disclosure_dir, args.disclosure_text_dir, args.output_dir)

    df.to_parquet(os.path.join(args.output_dir, "all_extracted_texts.parquet"), index=False)
    
    # Print sample information
    print(f"\nDataFrame shape: {df.shape}")
    if not df.empty:
        print("\nSample filenames:")
        for filename in df['filename'].head(5):
            print(f"  - {filename}")
        
        # Print text file output info
        txt_files = glob.glob(os.path.join(args.disclosure_text_dir, "**/*.txt"))
        print(f"\nCreated {len(txt_files)} text files in {args.disclosure_text_dir}")