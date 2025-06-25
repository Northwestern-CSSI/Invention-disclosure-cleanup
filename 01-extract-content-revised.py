import os
import re
import PyPDF2
import pandas as pd
import glob
import signal
import difflib
import argparse
from tqdm import tqdm
from pathlib import Path

# Handle broken pipe errors in Python
# signal.signal(signal.SIGPIPE, signal.SIG_DFL)
if hasattr(signal, 'SIGPIPE'):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def normalize_text(text):
    """Normalize text for fuzzy matching."""
    # Remove whitespace and convert to lowercase
    return re.sub(r'\s+', '', text.lower())

def find_section_marker_fuzzy(text, markers, threshold=0.7):
    """Use fuzzy matching to find section markers in text."""
    text_normalized = normalize_text(text)
    lines = text.splitlines()
    
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
    
    # If no match by lines, try scanning whole text with sliding window
    for marker in markers:
        marker_normalized = normalize_text(marker)
        for i in range(len(text_normalized) - len(marker_normalized) + 1):
            window = text_normalized[i:i+len(marker_normalized)]
            similarity = difflib.SequenceMatcher(None, marker_normalized, window).ratio()
            if similarity >= threshold:
                # Find the closest line break before this position
                pos = approximate_original_position(text, text_normalized, i)
                if pos > 0:
                    # Find the nearest line break before this position
                    line_break = text.rfind('\n', 0, pos)
                    if line_break > 0:
                        return text[:line_break]
    
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
            section_markers = [
                "III. ADDITIONAL INFORMATION & SUPPORTING DOCUMENTS",
                "III ADDITIONAL INFORMATION & SUPPORTING DOCUMENTS",
                "III. ADDITIONAL INFORMATION AND SUPPORTING DOCUMENTS",
                "III ADDITIONAL INFORMATION AND SUPPORTING DOCUMENTS",
                "III. ADDITIONAL INFORMATION",
                "III ADDITIONAL INFORMATION",
                "ADDITIONAL INFORMATION & SUPPORTING DOCUMENTS",
                "ADDITIONAL INFORMATION AND SUPPORTING DOCUMENTS",
                "SECTION III ADDITIONAL INFORMATION",
                "SECTION III: ADDITIONAL INFORMATION",
                "3. ADDITIONAL INFORMATION"
            ]
            
            # Try multiple approaches for finding the section
            
            # 1. First try fuzzy matching approach
            result = find_section_marker_fuzzy(full_text, section_markers)
            if result:
                return result.strip()
            
            # 2. Try regex-based approaches
            # Look for Roman numeral III or digit 3 followed by "Additional Information"
            patterns = [
                r'(?:^|\n|\s+)(?:III|3)\.?\s+.*?(?:ADDITIONAL|SUPPORTING).*?(?:INFORMATION|DOCUMENTS)',
                r'(?:^|\n|\s+)ADDITIONAL\s+INFORMATION(?:\s+(?:&|AND)\s+SUPPORTING\s+DOCUMENTS)?',
                r'(?:^|\n|\s+)(?:SECTION|PART)\s+(?:III|3)(?:\:|\.|,)?\s+',
                r'(?:^|\n|\s+)(?:III|3)(?:\:|\.|,)\s*ADDITIONAL'
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Check if this appears to be a section header (short line)
                    match_line = get_containing_line(full_text, match.start())
                    if len(match_line) < 100:  # Likely a header not regular text
                        return full_text[:match.start()].strip()
            
            # 3. Try page-by-page analysis for documents with clear section divisions
            for i, page_text in enumerate(page_texts):
                # Check if page starts with section marker patterns
                for pattern in patterns:
                    if re.search(pattern, page_text[:200], re.IGNORECASE):
                        # Return all text from previous pages
                        return "\n".join(page_texts[:i]).strip()
                
                # Look for page headers/footers that might indicate sections
                page_lines = page_text.splitlines()
                for j, line in enumerate(page_lines[:5]):  # Check first few lines
                    if re.search(r'(?:III|3)\.?\s+.*?INFORMATION', line, re.IGNORECASE):
                        # If found in first page, return nothing; otherwise return previous pages
                        if i > 0:
                            return "\n".join(page_texts[:i]).strip()
                        else:
                            return ""
            
            # 4. Try structural analysis - look for consistent section numbering
            # section_matches = re.finditer(r'(?:^|\n|\s+)(?:(?:I|II|III|IV|V)|(?:1|2|3|4|5))\.?\s+[A-Z]', full_text, re.MULTILINE)
            # section_positions = [match.start() for match in section_matches]
            
            # if len(section_positions) >= 3:  # We have at least 3 sections
            #     # Look for the third section (which would be section III or 3)
            #     # But first, verify these appear to be actual sections (reasonable spacing between them)
            #     diffs = [section_positions[i+1] - section_positions[i] for i in range(len(section_positions)-1)]
            #     median_diff = sorted(diffs)[len(diffs)//2]
                
            #     if median_diff > 100:  # Reasonable section size
            #         # The third section position
            #         if len(section_positions) >= 3:
            #             third_section_pos = section_positions[2]
            #             return full_text[:third_section_pos].strip()
            
            # If we couldn't find a clear marker, default to returning the full text
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