# modules/m3_rag_pipeline/faiss_indexer.py
"""FAISS index management for vector search."""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config, INDEX_DIR
from .chunker import Chunk


class FAISSIndexer:
    """Manages FAISS index for vector similarity search."""
    
    def __init__(self, embedding_dim: int, config=None):
        self.config = config or get_config()
        self.embedding_dim = embedding_dim
        self.index = None
        self.chunks: List[Chunk] = []
        self.id_to_chunk: Dict[str, Chunk] = {}
        self.index_dir = INDEX_DIR / "faiss"
        
    def create_index(self, index_type: Optional[str] = None):
        """Create a new FAISS index."""
        index_type = index_type or self.config.rag.faiss_index_type
        
        if index_type == "IndexFlatIP":
            # Inner product (for normalized vectors = cosine similarity)
            self.index = faiss.IndexFlatIP(self.embedding_dim)
        elif index_type == "IndexFlatL2":
            # L2 distance
            self.index = faiss.IndexFlatL2(self.embedding_dim)
        elif index_type == "IndexIVFFlat":
            # IVF index for larger datasets
            quantizer = faiss.IndexFlatIP(self.embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, 100)
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        logger.info(f"Created FAISS index: {index_type}")
        
    def add_vectors(
        self,
        embeddings: np.ndarray,
        chunks: List[Chunk],
        normalize: bool = True
    ):
        """Add vectors to the index."""
        if self.index is None:
            self.create_index()
        
        # Normalize for cosine similarity
        if normalize:
            faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Store chunk mappings
        for chunk in chunks:
            self.chunks.append(chunk)
            self.id_to_chunk[chunk.chunk_id] = chunk
        
        logger.info(f"Added {len(chunks)} vectors to index (total: {self.index.ntotal})")
        
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: Optional[int] = None,
        normalize: bool = True
    ) -> List[Tuple[Chunk, float]]:
        """Search for similar chunks."""
        if self.index is None or self.index.ntotal == 0:
            raise ValueError("Index is empty. Add vectors first.")
        
        top_k = top_k or self.config.rag.top_k_retrieval
        
        # Ensure 2D array
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Normalize query
        if normalize:
            faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Map results to chunks
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.chunks):
                chunk = self.chunks[idx]
                results.append((chunk, float(score)))
        
        return results
    
    def save(self, name: str = "academic_index"):
        """Save index and chunks to disk."""
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = self.index_dir / f"{name}.faiss"
        faiss.write_index(self.index, str(index_path))
        
        # Save chunks
        chunks_path = self.index_dir / f"{name}_chunks.pkl"
        with open(chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
        
        logger.info(f"Saved index to {self.index_dir}")
        
    def load(self, name: str = "academic_index"):
        """Load index and chunks from disk."""
        # Load FAISS index
        index_path = self.index_dir / f"{name}.faiss"
        self.index = faiss.read_index(str(index_path))
        
        # Load chunks
        chunks_path = self.index_dir / f"{name}_chunks.pkl"
        with open(chunks_path, 'rb') as f:
            self.chunks = pickle.load(f)
        
        # Rebuild mapping
        self.id_to_chunk = {chunk.chunk_id: chunk for chunk in self.chunks}
        
        logger.info(f"Loaded index with {self.index.ntotal} vectors")
        
    def get_stats(self) -> Dict:
        """Get index statistics."""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "embedding_dim": self.embedding_dim,
            "num_chunks": len(self.chunks),
            "index_type": type(self.index).__name__ if self.index else None
        }

