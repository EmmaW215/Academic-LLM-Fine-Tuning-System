# modules/m4_hybrid_retrieval/__init__.py
"""Module 4: Hybrid Retrieval System."""

from .sqlite_fts import SQLiteFTS
from .fusion import HybridRetriever, RRFFusion, SearchResult

__all__ = ["SQLiteFTS", "HybridRetriever", "RRFFusion", "SearchResult"]

