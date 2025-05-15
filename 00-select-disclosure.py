import PyPDF2
import os
import shutil
import re
import glob

def extract_first_page_text(pdf_path):
    """
    Extract text from the first page of a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Text extracted from the first page
    """
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            # Create a PDF reader object
            reader = PyPDF2.PdfReader(file)
            
            # Check if the PDF has pages
            if len(reader.pages) > 0:
                # Extract the first page
                first_page = reader.pages[0]
                
                # Extract text from the first page
                text = first_page.extract_text()
                
                return text
            else:
                return ""
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {str(e)}")
        return ""

def is_disclosure_form(text):
    """
    Check if the text contains the keywords indicating a disclosure form.
    
    Args:
        text (str): Text extracted from the first page
        
    Returns:
        bool: True if this is likely a disclosure form, False otherwise
    """
    # Check if all three keywords are in the same line
    lines = text.splitlines()
    for line in lines:
        if all(keyword.lower() in line.lower() for keyword in ["TECHNOLOGY", "DISCLOSURE", "FORM"]):
            return True
    
    # Alternative approach: check if all three keywords appear in the text
    # This is a more lenient check if the above fails
    keywords = ["TECHNOLOGY", "DISCLOSURE", "FORM"]
    if all(keyword.lower() in text.lower() for keyword in keywords):
        return True
    
    return False

def process_pdfs(raw_dir, disclosure_dir):
    """
    Process all PDFs in raw_dir, identify disclosure forms, and copy them to disclosure_dir.
    
    Args:
        raw_dir (str): Directory containing raw PDFs
        disclosure_dir (str): Directory to copy disclosure forms to
    """
    # Make sure destination directory exists
    os.makedirs(disclosure_dir, exist_ok=True)
    
    # Get all PDF files in raw directory
    pdf_files = glob.glob(os.path.join(raw_dir, "*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files in {raw_dir}")
    
    # Counter for identified disclosure forms
    disclosure_count = 0
    
    # Process each PDF
    for pdf_path in pdf_files:
        # Extract text from first page
        first_page_text = extract_first_page_text(pdf_path)
        
        # Check if this is a disclosure form
        if is_disclosure_form(first_page_text):
            # Get the base filename
            filename = os.path.basename(pdf_path)
            
            # Path to copy to
            dest_path = os.path.join(disclosure_dir, filename)
            
            # Copy the file
            shutil.copy2(pdf_path, dest_path)
            
            print(f"Copied disclosure form: {filename}")
            disclosure_count += 1
    
    print(f"\nTotal disclosure forms identified and copied: {disclosure_count}")

if __name__ == "__main__":
    # Directories
    raw_dir = "/home/shaoerzhuo/InnovationIntelligence/data-preprocessing/pdf-extraction/data/raw"
    disclosure_dir = "/home/shaoerzhuo/InnovationIntelligence/data-preprocessing/pdf-extraction/data/disclosure"
    
    # Process PDFs
    process_pdfs(raw_dir, disclosure_dir)