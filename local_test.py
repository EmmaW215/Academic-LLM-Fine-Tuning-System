#!/usr/bin/env python3
"""
Local Test Script - Test data collection WITHOUT GPU
This tests the parts that can run on your Mac
"""

import arxiv
from pathlib import Path
from loguru import logger
import fitz  # PyMuPDF
from tqdm import tqdm

# Setup directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "storage" / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

for d in [RAW_DIR, PROCESSED_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def test_arxiv_search(category: str = "cs.CL", max_results: int = 5):
    """Test searching arXiv for papers."""
    logger.info(f"🔍 Searching arXiv for {category} papers...")
    
    client = arxiv.Client()
    search = arxiv.Search(
        query=f"cat:{category}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    papers = []
    for result in client.results(search):
        paper = {
            "arxiv_id": result.entry_id.split("/")[-1],
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "abstract": result.summary,
            "published": result.published.isoformat(),
            "pdf_url": result.pdf_url
        }
        papers.append(paper)
        logger.info(f"  📄 Found: {paper['title'][:60]}...")
    
    logger.success(f"✅ Found {len(papers)} papers!")
    return papers


def test_download_pdf(paper: dict, save_dir: Path = RAW_DIR):
    """Test downloading a single PDF."""
    import requests
    
    arxiv_id = paper["arxiv_id"].replace("/", "_")
    pdf_path = save_dir / f"{arxiv_id}.pdf"
    
    if pdf_path.exists():
        logger.info(f"  📁 Already exists: {pdf_path.name}")
        return pdf_path
    
    logger.info(f"  📥 Downloading: {paper['title'][:50]}...")
    
    response = requests.get(paper["pdf_url"], timeout=30)
    if response.status_code == 200:
        pdf_path.write_bytes(response.content)
        logger.success(f"  ✅ Saved: {pdf_path.name}")
        return pdf_path
    else:
        logger.error(f"  ❌ Failed to download: {response.status_code}")
        return None


def test_extract_text(pdf_path: Path):
    """Test extracting text from PDF using PyMuPDF."""
    logger.info(f"  📖 Extracting text from: {pdf_path.name}")
    
    try:
        doc = fitz.open(pdf_path)
        text_parts = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            text_parts.append(text)
        
        full_text = "\n".join(text_parts)
        doc.close()
        
        # Clean text
        full_text = " ".join(full_text.split())  # Normalize whitespace
        
        logger.success(f"  ✅ Extracted {len(full_text)} characters from {len(text_parts)} pages")
        return full_text[:500] + "..."  # Return preview
        
    except Exception as e:
        logger.error(f"  ❌ Extraction failed: {e}")
        return None


def main():
    """Run all local tests."""
    print("=" * 60)
    print("🧪 LOCAL TEST - Academic LLM System")
    print("   Testing components that work WITHOUT GPU")
    print("=" * 60)
    print()
    
    # Test 1: arXiv Search
    print("\n📚 TEST 1: arXiv Paper Search")
    print("-" * 40)
    papers = test_arxiv_search(category="cs.CL", max_results=3)
    
    if not papers:
        print("❌ No papers found, stopping tests")
        return
    
    # Test 2: Download PDF
    print("\n📥 TEST 2: PDF Download")
    print("-" * 40)
    pdf_path = test_download_pdf(papers[0])
    
    if not pdf_path:
        print("❌ Download failed, stopping tests")
        return
    
    # Test 3: Extract Text
    print("\n📖 TEST 3: Text Extraction")
    print("-" * 40)
    text_preview = test_extract_text(pdf_path)
    
    if text_preview:
        print(f"\n📝 Text Preview:\n{text_preview[:300]}...")
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 LOCAL TESTS COMPLETE!")
    print("=" * 60)
    print("""
✅ What works locally (tested above):
   - arXiv paper search
   - PDF download
   - Text extraction from PDFs

❌ What REQUIRES GPU (not tested):
   - LLaMA 3 model loading
   - QLoRA fine-tuning  
   - Model inference/chat
   - Embedding generation (possible but slow)

➡️  Next step: Connect to GPU server to run full pipeline!
""")


if __name__ == "__main__":
    main()

