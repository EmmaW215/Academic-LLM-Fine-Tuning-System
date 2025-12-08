# modules/m3_rag_pipeline/embedder.py
"""Embedding generation using sentence-transformers."""

import numpy as np
from typing import List, Union, Optional
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from loguru import logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config


class EmbeddingGenerator:
    """Generates embeddings for text chunks."""
    
    def __init__(self, model_name: Optional[str] = None, config=None):
        self.config = config or get_config()
        self.model_name = model_name or self.config.model.embedding_model
        self.model = None
        self.embedding_dim = None
        
    def load_model(self):
        """Load the embedding model."""
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.embedding_dim}")
        
    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text."""
        if self.model is None:
            self.load_model()
        return self.model.encode(text, convert_to_numpy=True)
    
    def embed_batch(
        self, 
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """Embed multiple texts."""
        if self.model is None:
            self.load_model()
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def embed_chunks(
        self,
        chunks: List,  # List[Chunk]
        batch_size: int = 32
    ) -> np.ndarray:
        """Embed chunk objects."""
        texts = [chunk.text for chunk in chunks]
        return self.embed_batch(texts, batch_size)
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        if self.embedding_dim is None:
            self.load_model()
        return self.embedding_dim

