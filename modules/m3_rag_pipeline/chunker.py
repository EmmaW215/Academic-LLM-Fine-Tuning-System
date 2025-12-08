# modules/m3_rag_pipeline/chunker.py
"""Document chunking strategies."""

from typing import List, Optional, Dict
from dataclasses import dataclass
import re
from loguru import logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config


@dataclass
class Chunk:
    """A text chunk with metadata."""
    chunk_id: str
    doc_id: str
    text: str
    start_idx: int
    end_idx: int
    metadata: Dict
    token_count: int = 0


class DocumentChunker:
    """Splits documents into chunks for embedding."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.chunk_size = self.config.data.chunk_size
        self.chunk_overlap = self.config.data.chunk_overlap
        self.min_chunk_length = self.config.data.min_chunk_length
        
    def chunk_document(
        self, 
        doc_id: str,
        text: str,
        metadata: Optional[Dict] = None
    ) -> List[Chunk]:
        """Chunk a single document using sliding window."""
        metadata = metadata or {}
        chunks = []
        
        # Estimate tokens (rough approximation: 1 token ≈ 4 chars)
        char_chunk_size = self.chunk_size * 4
        char_overlap = self.chunk_overlap * 4
        
        # Split into sentences first for cleaner boundaries
        sentences = self._split_sentences(text)
        
        current_chunk = []
        current_length = 0
        chunk_start = 0
        chunk_idx = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            if current_length + sentence_len > char_chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text) >= self.min_chunk_length:
                    chunk = Chunk(
                        chunk_id=f"{doc_id}_chunk_{chunk_idx}",
                        doc_id=doc_id,
                        text=chunk_text,
                        start_idx=chunk_start,
                        end_idx=chunk_start + len(chunk_text),
                        metadata=metadata.copy(),
                        token_count=len(chunk_text) // 4
                    )
                    chunks.append(chunk)
                    chunk_idx += 1
                
                # Start new chunk with overlap
                overlap_chars = 0
                overlap_sentences = []
                for s in reversed(current_chunk):
                    if overlap_chars + len(s) < char_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_chars += len(s)
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_length = overlap_chars
                chunk_start = chunk_start + len(chunk_text) - overlap_chars
            
            current_chunk.append(sentence)
            current_length += sentence_len
        
        # Don't forget last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text) >= self.min_chunk_length:
                chunk = Chunk(
                    chunk_id=f"{doc_id}_chunk_{chunk_idx}",
                    doc_id=doc_id,
                    text=chunk_text,
                    start_idx=chunk_start,
                    end_idx=chunk_start + len(chunk_text),
                    metadata=metadata.copy(),
                    token_count=len(chunk_text) // 4
                )
                chunks.append(chunk)
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def chunk_by_sections(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict] = None
    ) -> List[Chunk]:
        """Chunk by detecting section headers."""
        metadata = metadata or {}
        chunks = []
        
        # Common section patterns in academic papers
        section_pattern = r'\n(?=(?:\d+\.?\s+)?(?:Abstract|Introduction|Related Work|Background|Method|Results|Discussion|Conclusion|References))'
        
        sections = re.split(section_pattern, text, flags=re.IGNORECASE)
        
        for idx, section in enumerate(sections):
            section = section.strip()
            if len(section) < self.min_chunk_length:
                continue
            
            # Extract section title if present
            lines = section.split('\n')
            section_title = lines[0][:100] if lines else f"Section {idx}"
            
            # If section is too long, sub-chunk it
            if len(section) > self.chunk_size * 4:
                sub_chunks = self.chunk_document(
                    doc_id=doc_id,
                    text=section,
                    metadata={**metadata, "section": section_title}
                )
                # Update chunk IDs
                for i, sc in enumerate(sub_chunks):
                    sc.chunk_id = f"{doc_id}_sec{idx}_chunk_{i}"
                chunks.extend(sub_chunks)
            else:
                chunk = Chunk(
                    chunk_id=f"{doc_id}_sec{idx}",
                    doc_id=doc_id,
                    text=section,
                    start_idx=0,
                    end_idx=len(section),
                    metadata={**metadata, "section": section_title},
                    token_count=len(section) // 4
                )
                chunks.append(chunk)
        
        return chunks
    
    def chunk_batch(
        self,
        documents: List[Dict],
        by_sections: bool = False
    ) -> List[Chunk]:
        """Chunk multiple documents."""
        all_chunks = []
        
        for doc in documents:
            doc_id = doc.get("arxiv_id", doc.get("id", "unknown"))
            text = doc.get("full_text", doc.get("text", ""))
            metadata = {
                "title": doc.get("title", ""),
                "authors": doc.get("authors", []),
                "arxiv_id": doc_id
            }
            
            if by_sections:
                chunks = self.chunk_by_sections(doc_id, text, metadata)
            else:
                chunks = self.chunk_document(doc_id, text, metadata)
            
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks

