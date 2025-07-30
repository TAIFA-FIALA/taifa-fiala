#!/usr/bin/env python3
"""
Manual PDF Ingestion Test Script
Test the PDF processing pipeline by manually processing PDFs from the inbox.
"""

import sys
import os
from pathlib import Path
import asyncio

# Add the data processors source to Python path
sys.path.append(str(Path(__file__).parent / "data_processors" / "src"))

try:
    from taifa_etl.services.file_ingestion.processors.pdf_processor import PDFProcessor
    print("✅ Successfully imported PDFProcessor")
except ImportError as e:
    print(f"❌ Failed to import PDFProcessor: {e}")
    print("Trying alternative import...")
    
    # Alternative: use the backend PDF processor if available
    sys.path.append(str(Path(__file__).parent / "backend"))
    try:
        # We'll create a simple PDF processor inline
        print("Creating simple PDF processor...")
    except Exception as e2:
        print(f"❌ Alternative import failed: {e2}")
        sys.exit(1)

async def process_pdf_from_inbox():
    """Process PDFs from the inbox folder"""
    
    inbox_path = Path(__file__).parent / "data_ingestion" / "inbox" / "pdfs"
    processing_path = Path(__file__).parent / "data_ingestion" / "processing"
    completed_path = Path(__file__).parent / "data_ingestion" / "completed"
    failed_path = Path(__file__).parent / "data_ingestion" / "failed"
    
    print(f"📁 Checking inbox: {inbox_path}")
    
    # Check for PDFs and HTML files in inbox
    pdf_files = list(inbox_path.glob("*.pdf"))
    html_files = list(inbox_path.glob("*.html"))
    all_files = pdf_files + html_files
    
    if not all_files:
        print("📭 No PDFs or HTML files found in inbox")
        print(f"💡 Drop a PDF or HTML file into: {inbox_path}")
        return
    
    print(f"📄 Found {len(all_files)} file(s) to process:")
    for file in all_files:
        file_type = "PDF" if file.suffix.lower() == ".pdf" else "HTML"
        print(f"  - {file.name} ({file.stat().st_size / 1024:.1f} KB) [{file_type}]")
    
    # Process each file
    for file in all_files:
        print(f"\n🔄 Processing: {file.name}")
        
        try:
            # Move to processing folder
            processing_file = processing_path / file.name
            file.rename(processing_file)
            print(f"📦 Moved to processing: {processing_file}")
            
            # Extract text based on file type
            text_content = ""
            
            if processing_file.suffix.lower() == ".pdf":
                # PDF text extraction using PyPDF2
                import PyPDF2
                
                with open(processing_file, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    print(f"📖 PDF has {len(pdf_reader.pages)} pages")
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        text_content += f"\n--- Page {page_num + 1} ---\n{page_text}"
                        
            elif processing_file.suffix.lower() == ".html":
                # HTML text extraction
                from bs4 import BeautifulSoup
                
                try:
                    with open(processing_file, 'r', encoding='utf-8') as html_file:
                        soup = BeautifulSoup(html_file.read(), 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Get text content
                        text_content = soup.get_text()
                        
                        # Clean up whitespace
                        lines = (line.strip() for line in text_content.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text_content = '\n'.join(chunk for chunk in chunks if chunk)
                        
                        print(f"🌐 HTML processed successfully")
                        
                except ImportError:
                    print("⚠️ BeautifulSoup not available, using basic HTML processing")
                    with open(processing_file, 'r', encoding='utf-8') as html_file:
                        import re
                        html_content = html_file.read()
                        # Basic HTML tag removal
                        text_content = re.sub('<[^<]+?>', '', html_content)
                        text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            print(f"📝 Extracted {len(text_content)} characters of text")
            
            # Basic analysis
            lines = text_content.split('\n')
            non_empty_lines = [line.strip() for line in lines if line.strip()]
            
            print(f"📊 Analysis:")
            print(f"  - Total lines: {len(lines)}")
            print(f"  - Non-empty lines: {len(non_empty_lines)}")
            
            # Look for funding-related keywords
            funding_keywords = ['funding', 'grant', 'investment', 'million', 'startup', 'venture', 'capital', 'fund']
            keyword_counts = {}
            
            text_lower = text_content.lower()
            for keyword in funding_keywords:
                count = text_lower.count(keyword)
                if count > 0:
                    keyword_counts[keyword] = count
            
            if keyword_counts:
                print(f"💰 Funding keywords found:")
                for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  - '{keyword}': {count} times")
            else:
                print("⚠️ No obvious funding keywords found")
            
            # Show first few lines of content
            print(f"\n📄 Content preview (first 500 chars):")
            print("-" * 50)
            print(text_content[:500] + "..." if len(text_content) > 500 else text_content)
            print("-" * 50)
            
            # Move to completed
            completed_file = completed_path / file.name
            processing_file.rename(completed_file)
            print(f"✅ Processing completed: {completed_file}")
            
        except Exception as e:
            print(f"❌ Error processing {file.name}: {e}")
            
            # Move to failed folder
            try:
                failed_file = failed_path / file.name
                if processing_file.exists():
                    processing_file.rename(failed_file)
                else:
                    file.rename(failed_file)
                print(f"💥 Moved to failed: {failed_file}")
            except Exception as move_error:
                print(f"❌ Error moving failed file: {move_error}")

def main():
    print("🚀 Manual PDF Ingestion Test")
    print("=" * 50)
    
    try:
        asyncio.run(process_pdf_from_inbox())
    except KeyboardInterrupt:
        print("\n⏹️ Processing interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n✨ Test completed!")

if __name__ == "__main__":
    main()
