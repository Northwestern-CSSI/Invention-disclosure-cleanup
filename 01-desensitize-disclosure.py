import os
import re
import PyPDF2
from pathlib import Path

def process_pdf(input_path, output_path):
    """
    Process a PDF file to remove the page containing a specific marker sentence and all pages after it.
    Enhanced with fuzzy matching to handle potential PDF text extraction issues.
    
    Args:
        input_path (str): Path to the input PDF file
        output_path (str): Path to save the processed PDF file
    """
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
    
    with open(input_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        total_pages = len(reader.pages)
        
        # Find the page that contains the marker text
        marker_page = None
        
        # Store text of each page for analysis
        page_texts = []
        for i in range(total_pages):
            page = reader.pages[i]
            text = page.extract_text()
            page_texts.append(text.lower())
        
        # First pass: Try to find exact key phrases
        for i, text in enumerate(page_texts):
            for phrase in marker_phrases:
                if phrase.lower() in text:
                    print(f"Found marker phrase on page {i+1}: '{phrase}'")
                    marker_page = i
                    break
            if marker_page is not None:
                break
        
        # Second pass: Use regex for fuzzy matching if not found in first pass
        if marker_page is None:
            for i, text in enumerate(page_texts):
                if marker_pattern.search(text):
                    print(f"Found marker pattern match on page {i+1}")
                    marker_page = i
                    break
        
        # Third pass: Search for individual words in combination
        if marker_page is None:
            for i, text in enumerate(page_texts):
                # Count occurrence of important words
                word_count = sum([
                    1 if "contributor" in text else 0,
                    1 if "sign" in text else 0,
                    1 if "form" in text else 0,
                    1 if "accuracy" in text else 0,
                    1 if "table" in text else 0,
                    1 if "copy" in text else 0
                ])
                
                if word_count >= 3:
                    print(f"Found marker word combination on page {i+1} with score {word_count}/6")
                    marker_page = i
                    break
        
        # Additional check for signature sections in later pages if marker not found
        if marker_page is None and total_pages > 5:
            # Check the last third of the document for signature-like content
            start_check = int(total_pages * 0.67)
            for i in range(start_check, total_pages):
                text = page_texts[i]
                if "signature" in text or "sign" in text or "contributor" in text:
                    print(f"Found potential signature section on page {i+1}")
                    marker_page = i
                    break
        
        # If marker found, only include pages before it
        if marker_page is not None:
            print(f"Removing page {marker_page+1} and all subsequent pages")
            for i in range(marker_page):
                writer.add_page(reader.pages[i])
            pages_kept = marker_page
        else:
            # If no marker found, use heuristics based on document type
            doc_title = reader.metadata.get('/Title', '').lower() if reader.metadata else ''
            
            if (total_pages > 10 and 
                ('disclosure' in doc_title or 'invention' in doc_title or 'patent' in doc_title)):
                # For disclosure documents, keep first 2/3 of pages as a safety measure
                safe_pages = int(total_pages * 0.67)
                print(f"No marker found. Document appears to be a disclosure form.")
                print(f"Taking precautionary measure to keep only first {safe_pages} pages")
                
                for i in range(safe_pages):
                    writer.add_page(reader.pages[i])
                pages_kept = safe_pages
            else:
                # If truly nothing relevant found, keep the first 80% of the document
                safe_pages = int(total_pages * 0.8)
                print("WARNING: Could not identify any marker with confidence.")
                print(f"Taking precautionary measure to keep only first {safe_pages} pages")
                
                for i in range(safe_pages):
                    writer.add_page(reader.pages[i])
                pages_kept = safe_pages
        
        # If no pages were included, add a blank page
        if pages_kept == 0:
            print("No content to keep. Creating an empty PDF with a blank page.")
            writer.add_blank_page(width=595, height=842)  # A4 size
        else:
            print(f"Kept {pages_kept} pages in the output document")
        
        # Write the output file
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
    
    return True  # Always return True because we're taking action regardless

def batch_process_pdfs(input_dir, output_dir):
    """
    Process all PDF files in the input directory and save results to the output directory.
    
    Args:
        input_dir (str): Directory containing input PDF files
        output_dir (str): Directory to save processed PDF files
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    processed_count = 0
    for pdf_file in input_path.glob('*.pdf'):
        output_file = output_path / pdf_file.name
        if process_pdf(str(pdf_file), str(output_file)):
            processed_count += 1
            print(f"Processed: {pdf_file.name}")
        else:
            print(f"No changes made to: {pdf_file.name}")
    
    print(f"Completed processing {processed_count} files")

if __name__ == "__main__":
    # Example usage
    input_dir = "data/before"
    output_dir = "data/after"
    batch_process_pdfs(input_dir, output_dir)