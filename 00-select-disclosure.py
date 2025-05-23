import os
import shutil
import signal
import argparse
from pathlib import Path
from tqdm import tqdm

# Handle broken pipe errors in Python
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def find_pdf_files(directory):
    """Find all PDF files in a directory and its subdirectories."""
    pdf_files = []
    # Use Path.rglob for recursive glob pattern matching
    for file_path in Path(directory).rglob("*.pdf"):
        pdf_files.append(str(file_path))
    return pdf_files

def process_pdfs(raw_dir, disclosure_dir, supplementary_dir):
    """Process PDFs and separate them into invention disclosures and supplementary documents."""
    print(f"Starting document classification from {raw_dir}...")
    
    # Make sure destination directories exist
    os.makedirs(disclosure_dir, exist_ok=True)
    os.makedirs(supplementary_dir, exist_ok=True)
    
    # Get all PDF files in raw directory and subdirectories
    pdf_files = find_pdf_files(raw_dir)
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Counters for classified documents
    invention_count = 0
    supplementary_count = 0
    
    # Process each PDF with progress bar
    for pdf_path in tqdm(pdf_files, desc="Classifying documents", unit="file"):
        # Get the relative path from raw_dir to maintain directory structure
        rel_path = os.path.relpath(pdf_path, raw_dir)
        
        # Determine if it's an invention disclosure based on filename
        is_invention = "InventionDisclosure" in os.path.basename(pdf_path)
        
        # Choose destination directory
        dest_dir = disclosure_dir if is_invention else supplementary_dir
        
        # Create destination path maintaining the same directory structure
        dest_path = os.path.join(dest_dir, rel_path)
        
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        # Copy the file
        shutil.copy2(pdf_path, dest_path)
        
        # Update counters
        if is_invention:
            invention_count += 1
        else:
            supplementary_count += 1
    
    print(f"Processed {len(pdf_files)} files:")
    print(f"- {invention_count} invention disclosures")
    print(f"- {supplementary_count} supplementary documents")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Classify PDF files into invention disclosures and supplementary documents")
    parser.add_argument("--raw-dir", default="data/raw", help="Directory containing raw PDF files")
    parser.add_argument("--disclosure-dir", default="data/invention_disclosure", 
                       help="Directory to save invention disclosure forms")
    parser.add_argument("--supplementary-dir", default="data/supplementary", 
                       help="Directory to save supplementary documents")
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Process PDFs
    process_pdfs(args.raw_dir, args.disclosure_dir, args.supplementary_dir)