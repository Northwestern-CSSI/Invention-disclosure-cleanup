import PyPDF2
import os
import shutil
import glob
import signal
from tqdm import tqdm

# Handle broken pipe errors in Python
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def extract_first_page_text(pdf_path):
    """Extract text from the first page of a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if len(reader.pages) > 0:
                return reader.pages[0].extract_text()
            else:
                return ""
    except Exception:
        return ""

def is_disclosure_form(text):
    """Check if text contains keywords indicating a disclosure form."""
    # Check if all keywords are in the same line
    lines = text.splitlines()
    for line in lines:
        if all(keyword.lower() in line.lower() for keyword in ["TECHNOLOGY", "DISCLOSURE", "FORM"]):
            return True
    
    # Alternative check if all keywords appear anywhere in the text
    keywords = ["TECHNOLOGY", "DISCLOSURE", "FORM"]
    return all(keyword.lower() in text.lower() for keyword in keywords)

def process_pdfs(raw_dir, disclosure_dir):
    """Process PDFs and identify disclosure forms."""
    print("Starting disclosure form selection...")
    
    # Make sure destination directory exists
    os.makedirs(disclosure_dir, exist_ok=True)
    
    # Get all PDF files in raw directory
    pdf_files = glob.glob(os.path.join(raw_dir, "*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Counter for identified disclosure forms
    disclosure_count = 0
    
    # Process each PDF with progress bar
    for pdf_path in tqdm(pdf_files, desc="Selecting disclosure forms", unit="file"):
        # Extract text from first page
        first_page_text = extract_first_page_text(pdf_path)
        
        if not first_page_text:
            continue
            
        # Check if this is a disclosure form
        if is_disclosure_form(first_page_text):
            # Copy the file
            dest_path = os.path.join(disclosure_dir, os.path.basename(pdf_path))
            shutil.copy2(pdf_path, dest_path)
            disclosure_count += 1
    
    print(f"Processed {len(pdf_files)} files, identified {disclosure_count} disclosure forms")

if __name__ == "__main__":
    # Directories - use relative paths
    raw_dir = "data/raw"
    disclosure_dir = "data/disclosure"
    
    # Process PDFs
    process_pdfs(raw_dir, disclosure_dir)