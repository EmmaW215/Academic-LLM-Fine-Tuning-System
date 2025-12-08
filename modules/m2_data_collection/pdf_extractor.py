# modules/m2_data_collection/pdf_extractor.py
"""PDF text extraction using PyMuPDF."""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
from tqdm import tqdm
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import DATA_DIR


@dataclass
class ExtractedDocument:
    """Extracted document with text and metadata."""
    arxiv_id: str
    title: str
    full_text: str
    pages: List[str]
    num_pages: int
    source_path: str


class PDFExtractor:
    """Extracts text from PDF files."""
    
    def __init__(self):
        self.raw_dir = DATA_DIR / "raw"
        self.processed_dir = DATA_DIR / "processed"
        self.documents: List[ExtractedDocument] = []
        
    def extract_single(self, pdf_path: str, metadata: Optional[Dict] = None) -> ExtractedDocument:
        """Extract text from a single PDF."""
        pdf_path = Path(pdf_path)
        
        try:
            doc = fitz.open(pdf_path)
            pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                # Clean up text
                text = self._clean_page_text(text)
                pages.append(text)
            
            full_text = "\n\n".join(pages)
            arxiv_id = pdf_path.stem.replace("_", "/")
            
            extracted = ExtractedDocument(
                arxiv_id=arxiv_id,
                title=metadata.get("title", arxiv_id) if metadata else arxiv_id,
                full_text=full_text,
                pages=pages,
                num_pages=len(pages),
                source_path=str(pdf_path)
            )
            
            doc.close()
            return extracted
            
        except Exception as e:
            logger.error(f"Failed to extract {pdf_path}: {e}")
            raise
    
    def _clean_page_text(self, text: str) -> str:
        """Clean extracted page text."""
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_batch(
        self, 
        pdf_paths: List[str], 
        metadata_list: Optional[List[Dict]] = None
    ) -> List[ExtractedDocument]:
        """Extract text from multiple PDFs."""
        self.documents = []
        
        for i, pdf_path in enumerate(tqdm(pdf_paths, desc="Extracting PDFs")):
            try:
                metadata = metadata_list[i] if metadata_list else None
                doc = self.extract_single(pdf_path, metadata)
                self.documents.append(doc)
            except Exception as e:
                logger.warning(f"Skipping {pdf_path}: {e}")
        
        logger.info(f"Extracted {len(self.documents)} documents")
        return self.documents
    
    def save_extracted(self, output_dir: Optional[Path] = None):
        """Save extracted documents to JSON files."""
        output_dir = output_dir or (self.processed_dir / "extracted")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for doc in self.documents:
            filename = doc.arxiv_id.replace("/", "_") + ".json"
            filepath = output_dir / filename
            
            data = {
                "arxiv_id": doc.arxiv_id,
                "title": doc.title,
                "full_text": doc.full_text,
                "num_pages": doc.num_pages,
                "source_path": doc.source_path
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(self.documents)} documents to {output_dir}")

