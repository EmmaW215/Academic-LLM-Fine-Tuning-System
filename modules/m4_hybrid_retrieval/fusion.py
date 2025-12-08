# modules/m4_hybrid_retrieval/fusion.py
"""Score fusion strategies for hybrid retrieval."""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from loguru import logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config


@dataclass
class SearchResult:
    """Unified search result."""
    chunk_id: str
    doc_id: str
    text: str
    score: float
    metadata: Dict
    source: str  # "vector" or "keyword"


class RRFFusion:
    """Reciprocal Rank Fusion for combining search results."""
    
    def __init__(self, k: int = 60):
        self.k = k  # RRF constant
        
    def fuse(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult]
    ) -> List[SearchResult]:
        """Fuse results using RRF."""
        scores = {}
        results_map = {}
        
        # Score vector results
        for rank, result in enumerate(vector_results):
            rrf_score = 1.0 / (self.k + rank + 1)
            chunk_id = result.chunk_id
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            results_map[chunk_id] = result
        
        # Score keyword results
        for rank, result in enumerate(keyword_results):
            rrf_score = 1.0 / (self.k + rank + 1)
            chunk_id = result.chunk_id
            scores[chunk_id] = scores.get(chunk_id, 0) + rrf_score
            if chunk_id not in results_map:
                results_map[chunk_id] = result
        
        # Sort by combined score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        fused_results = []
        for chunk_id in sorted_ids:
            result = results_map[chunk_id]
            result.score = scores[chunk_id]
            result.source = "hybrid"
            fused_results.append(result)
        
        return fused_results


class HybridRetriever:
    """Combines vector and keyword search."""
    
    def __init__(self, faiss_indexer, sqlite_fts, embedder, config=None):
        self.config = config or get_config()
        self.faiss_indexer = faiss_indexer
        self.sqlite_fts = sqlite_fts
        self.embedder = embedder
        self.fusion = RRFFusion()
        
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        vector_weight: Optional[float] = None,
        keyword_weight: Optional[float] = None
    ) -> List[SearchResult]:
        """Perform hybrid search."""
        top_k = top_k or self.config.rag.top_k_retrieval
        vector_weight = vector_weight or self.config.rag.vector_weight
        keyword_weight = keyword_weight or self.config.rag.keyword_weight
        
        # Vector search
        query_embedding = self.embedder.embed_text(query)
        vector_results_raw = self.faiss_indexer.search(query_embedding, top_k * 2)
        
        vector_results = [
            SearchResult(
                chunk_id=chunk.chunk_id,
                doc_id=chunk.doc_id,
                text=chunk.text,
                score=score,
                metadata=chunk.metadata,
                source="vector"
            )
            for chunk, score in vector_results_raw
        ]
        
        # Keyword search
        keyword_results_raw = self.sqlite_fts.search(query, top_k * 2)
        
        keyword_results = [
            SearchResult(
                chunk_id=r["chunk_id"],
                doc_id=r["doc_id"],
                text=r["text"],
                score=r["score"],
                metadata={},
                source="keyword"
            )
            for r in keyword_results_raw
        ]
        
        # Fuse results
        if self.config.rag.use_rrf:
            fused = self.fusion.fuse(vector_results, keyword_results)
        else:
            # Weighted score fusion
            fused = self._weighted_fusion(
                vector_results, keyword_results,
                vector_weight, keyword_weight
            )
        
        return fused[:top_k]
    
    def _weighted_fusion(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult],
        vector_weight: float,
        keyword_weight: float
    ) -> List[SearchResult]:
        """Simple weighted score fusion."""
        scores = {}
        results_map = {}
        
        # Normalize and weight vector scores
        if vector_results:
            max_v = max(r.score for r in vector_results)
            for r in vector_results:
                norm_score = (r.score / max_v) * vector_weight
                scores[r.chunk_id] = scores.get(r.chunk_id, 0) + norm_score
                results_map[r.chunk_id] = r
        
        # Normalize and weight keyword scores
        if keyword_results:
            max_k = max(r.score for r in keyword_results)
            for r in keyword_results:
                norm_score = (r.score / max_k) * keyword_weight
                scores[r.chunk_id] = scores.get(r.chunk_id, 0) + norm_score
                if r.chunk_id not in results_map:
                    results_map[r.chunk_id] = r
        
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        return [results_map[cid] for cid in sorted_ids]

