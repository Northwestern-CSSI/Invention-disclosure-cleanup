import os
import re
import PyPDF2
import argparse
from pathlib import Path
import signal
from tqdm import tqdm

# Handle broken pipe errors in Python
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def process_pdf(input_path, output_path):
    """Process a PDF file to remove sensitive sections."""
    # Marker phrases to identify where to cut the document
    marker_phrases = [
        "contributor must sign this form confirming the accuracy",
        "For additional Contributors, simply copy the table",
        "At least one contributor must sign",
        "confirming the accuracy of the information provided",
        "copy the table below and paste at the end of the document"
    ]
    
    # Regex pattern for more flexible matching
    marker_pattern = re.compile(r'contributor.*sign.*form.*accuracy|copy.*table.*end.*document', re.IGNORECASE)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            total_pages = len(reader.pages)
            
            # Find the page that contains the marker text
            marker_page = None
            
            # Store text of each page for analysis
            page_texts = []
            for i in range(total_pages):
                try:
                    page = reader.pages[i]
                    text = page.extract_text()
                    page_texts.append(text.lower())
                except Exception:
                    page_texts.append("")
            
            # Look for marker page using various methods
            # First: exact phrases
            for i, text in enumerate(page_texts):
                for phrase in marker_phrases:
                    if phrase.lower() in text:
                        marker_page = i
                        break
                if marker_page is not None:
                    break
            
            # Second: regex pattern
            if marker_page is None:
                for i, text in enumerate(page_texts):
                    if marker_pattern.search(text):
                        marker_page = i
                        break
            
            # Third: keyword combinations
            if marker_page is None:
                for i, text in enumerate(page_texts):
                    word_count = sum([
                        1 if "contributor" in text else 0,
                        1 if "sign" in text else 0,
                        1 if "form" in text else 0,
                        1 if "accuracy" in text else 0,
                        1 if "table" in text else 0,
                        1 if "copy" in text else 0
                    ])
                    
                    if word_count >= 3:
                        marker_page = i
                        break
            
            # Last resort: check for signature sections
            if marker_page is None and total_pages > 5:
                start_check = int(total_pages * 0.67)
                for i in range(start_check, total_pages):
                    text = page_texts[i]
                    if "signature" in text or "sign" in text or "contributor" in text:
                        marker_page = i
                        break
            
            # Process based on results
            if marker_page is not None:
                # Keep pages before marker page
                for i in range(marker_page):
                    writer.add_page(reader.pages[i])
                pages_kept = marker_page
            else:
                # Fallback: use heuristics based on document type
                doc_title = reader.metadata.get('/Title', '').lower() if reader.metadata else ''
                
                if (total_pages > 10 and 
                    ('disclosure' in doc_title or 'invention' in doc_title or 'patent' in doc_title)):
                    # Keep first 2/3 of pages
                    safe_pages = int(total_pages * 0.67)
                    for i in range(safe_pages):
                        writer.add_page(reader.pages[i])
                    pages_kept = safe_pages
                else:
                    # Keep first 80% of pages
                    safe_pages = int(total_pages * 0.8)
                    for i in range(safe_pages):
                        writer.add_page(reader.pages[i])
                    pages_kept = safe_pages
            
            # Add blank page if needed
            if pages_kept == 0:
                writer.add_blank_page(width=595, height=842)  # A4 size
                
            # Write the output file
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        return False

def find_pdf_files(directory):
    """Find all PDF files in a directory and its subdirectories."""
    pdf_files = []
    # Use Path.rglob for recursive glob pattern matching
    for file_path in Path(directory).rglob("*.pdf"):
        pdf_files.append(file_path)
    return pdf_files

def batch_process_pdfs(input_dir, output_dir):
    """Process all PDF files in the input directory."""
    print(f"Starting desensitization process from {input_dir}...")
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # Get list of all PDF files (recursively)
    pdf_files = find_pdf_files(input_dir)
    total_files = len(pdf_files)
    print(f"Found {total_files} PDF files to process")
    
    processed_count = 0
    
    # Process with progress bar
    for pdf_file in tqdm(pdf_files, desc="Desensitizing documents", unit="file"):
        output_file = output_path / pdf_file.name
        if process_pdf(str(pdf_file), str(output_file)):
            processed_count += 1
    
    print(f"Completed: {processed_count}/{total_files} files processed")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Desensitize disclosure forms")
    parser.add_argument("--disclosure-dir", default="data/disclosure", help="Directory containing disclosure forms")
    parser.add_argument("--desensitized-dir", default="data/desensitized", help="Directory to save desensitized forms")
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Process PDFs
    batch_process_pdfs(args.disclosure_dir, args.desensitized_dir)