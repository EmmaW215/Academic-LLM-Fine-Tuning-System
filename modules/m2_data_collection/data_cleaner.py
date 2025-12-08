# modules/m2_data_collection/data_cleaner.py
"""Data cleaning and deduplication."""

import re
from typing import List, Set
from langdetect import detect, LangDetectException
from datasketch import MinHash, MinHashLSH
from loguru import logger


class DataCleaner:
    """Cleans and deduplicates text data."""
    
    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
        self.lsh = MinHashLSH(threshold=similarity_threshold, num_perm=128)
        self.seen_hashes: Set[str] = set()
        
    def clean_text(self, text: str) -> str:
        """Apply all cleaning operations to text."""
        text = self._remove_html(text)
        text = self._remove_pii(text)
        text = self._remove_special_chars(text)
        text = self._normalize_whitespace(text)
        return text
    
    def _remove_html(self, text: str) -> str:
        """Remove HTML tags."""
        return re.sub(r'<[^>]+>', '', text)
    
    def _remove_pii(self, text: str) -> str:
        """Remove PII (emails, phone numbers, credit cards)."""
        # Email
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        # Phone numbers (various formats)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        # Credit card numbers
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', text)
        return text
    
    def _remove_special_chars(self, text: str) -> str:
        """Remove special characters but keep essential punctuation."""
        # Keep alphanumeric, common punctuation, and whitespace
        text = re.sub(r'[^\w\s.,!?;:\-\'\"()\[\]{}]', ' ', text)
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def detect_language(self, text: str) -> str:
        """Detect language of text."""
        try:
            return detect(text[:1000])  # Use first 1000 chars
        except LangDetectException:
            return "unknown"
    
    def is_english(self, text: str) -> bool:
        """Check if text is English."""
        return self.detect_language(text) == "en"
    
    def _get_minhash(self, text: str) -> MinHash:
        """Create MinHash from text."""
        m = MinHash(num_perm=128)
        words = text.lower().split()
        for word in words:
            m.update(word.encode('utf-8'))
        return m
    
    def is_duplicate(self, text: str, doc_id: str) -> bool:
        """Check if text is duplicate using MinHash LSH."""
        m = self._get_minhash(text)
        
        # Query for similar documents
        result = self.lsh.query(m)
        
        if result:
            return True
        
        # Add to LSH index
        self.lsh.insert(doc_id, m)
        return False
    
    def deduplicate_batch(self, documents: List[dict]) -> List[dict]:
        """Remove duplicate documents from a batch."""
        unique_docs = []
        
        for doc in documents:
            doc_id = doc.get("arxiv_id", str(len(unique_docs)))
            text = doc.get("full_text", doc.get("abstract", ""))
            
            if not self.is_duplicate(text, doc_id):
                unique_docs.append(doc)
        
        removed = len(documents) - len(unique_docs)
        if removed > 0:
            logger.info(f"Removed {removed} duplicate documents")
        
        return unique_docs
    
    def process_batch(self, documents: List[dict]) -> List[dict]:
        """Full processing pipeline for documents."""
        processed = []
        
        for doc in documents:
            # Clean text
            if "full_text" in doc:
                doc["full_text"] = self.clean_text(doc["full_text"])
            if "abstract" in doc:
                doc["abstract"] = self.clean_text(doc["abstract"])
            
            # Language filter
            text = doc.get("full_text", doc.get("abstract", ""))
            if not self.is_english(text):
                logger.debug(f"Skipping non-English: {doc.get('arxiv_id', 'unknown')}")
                continue
            
            processed.append(doc)
        
        # Deduplicate
        processed = self.deduplicate_batch(processed)
        
        logger.info(f"Processed {len(processed)} documents (from {len(documents)})")
        return processed

