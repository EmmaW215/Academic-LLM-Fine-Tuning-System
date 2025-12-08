# modules/m4_hybrid_retrieval/sqlite_fts.py
"""SQLite FTS5 for keyword search."""

import sqlite3
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import INDEX_DIR


class SQLiteFTS:
    """SQLite FTS5 full-text search engine."""
    
    def __init__(self, db_name: str = "academic_search.db"):
        self.db_path = INDEX_DIR / "sqlite" / db_name
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        
    def connect(self):
        """Connect to database."""
        # Close existing connection if any
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
        
        # Connect with timeout to handle locked databases
        self.conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        self.conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        self.conn.execute("PRAGMA journal_mode=WAL")
        
    def create_tables(self):
        """Create FTS5 tables."""
        if self.conn is None:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                title TEXT,
                authors TEXT,
                arxiv_id TEXT,
                abstract TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                doc_id TEXT,
                text TEXT,
                section TEXT,
                FOREIGN KEY (doc_id) REFERENCES documents(doc_id)
            )
        """)
        
        # FTS5 virtual table for full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                chunk_id,
                doc_id,
                text,
                section,
                content='chunks',
                content_rowid='rowid'
            )
        """)
        
        # Triggers to keep FTS in sync
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
                INSERT INTO chunks_fts(rowid, chunk_id, doc_id, text, section)
                VALUES (new.rowid, new.chunk_id, new.doc_id, new.text, new.section);
            END
        """)
        
        self.conn.commit()
        logger.info("Created SQLite FTS tables")
        
    def add_document(self, doc: Dict):
        """Add a document to the database."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO documents (doc_id, title, authors, arxiv_id, abstract)
            VALUES (?, ?, ?, ?, ?)
        """, (
            doc.get("doc_id", doc.get("arxiv_id")),
            doc.get("title", ""),
            ",".join(doc.get("authors", [])),
            doc.get("arxiv_id", ""),
            doc.get("abstract", "")
        ))
        
        self.conn.commit()
        
    def add_chunk(self, chunk):
        """Add a chunk to the database."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO chunks (chunk_id, doc_id, text, section)
            VALUES (?, ?, ?, ?)
        """, (
            chunk.chunk_id,
            chunk.doc_id,
            chunk.text,
            chunk.metadata.get("section", "")
        ))
        
        self.conn.commit()
        
    def add_chunks_batch(self, chunks: List):
        """Add multiple chunks."""
        cursor = self.conn.cursor()
        
        data = [
            (c.chunk_id, c.doc_id, c.text, c.metadata.get("section", ""))
            for c in chunks
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO chunks (chunk_id, doc_id, text, section)
            VALUES (?, ?, ?, ?)
        """, data)
        
        self.conn.commit()
        logger.info(f"Added {len(chunks)} chunks to SQLite")
        
    def _sanitize_fts5_query(self, query: str) -> str:
        """Sanitize query string for FTS5 syntax.
        
        FTS5 special characters that need handling:
        - ? : parameter placeholder (causes syntax error)
        - " : quote (needs escaping)
        - ' : single quote (needs escaping)
        - : : colon (special operator)
        - * : wildcard (can be used but needs careful handling)
        - AND, OR, NOT : logical operators (should be preserved)
        
        Returns a sanitized query that will match any of the words in the original query.
        """
        import re
        
        # Remove trailing question marks and other punctuation that cause issues
        # But preserve the core search terms
        query = query.strip()
        
        # Remove trailing question marks, exclamation marks
        query = re.sub(r'[?!]+$', '', query)
        
        # Remove or escape special FTS5 characters that cause syntax errors
        # Replace ? with space (since ? is parameter placeholder in SQL)
        query = query.replace('?', ' ')
        
        # Escape quotes by removing them (or could double them)
        query = query.replace('"', ' ').replace("'", ' ')
        
        # Remove colons that aren't part of words (but keep word-internal colons)
        query = re.sub(r'(?<!\w):(?!\w)', ' ', query)
        
        # Clean up multiple spaces
        query = re.sub(r'\s+', ' ', query).strip()
        
        # If query is empty after cleaning, return a wildcard search
        if not query:
            return '*'
        
        # Split into words and filter out empty strings and very short words
        words = [w for w in query.split() if len(w) > 1]
        
        if not words:
            return '*'
        
        # Join words with AND for more precise matching
        # This allows flexible matching: any document containing these words
        # Escape any remaining special characters in words
        sanitized_words = []
        for word in words:
            # Escape quotes in words
            escaped_word = word.replace('"', '""')
            sanitized_words.append(escaped_word)
        
        # Use AND to require all words (more precise) or just join with space (OR-like)
        # For better recall, we'll use space (which acts like OR in FTS5)
        return ' '.join(sanitized_words)
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search using FTS5."""
        # Ensure connection is open
        if self.conn is None:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Sanitize query to handle special characters
        sanitized_query = self._sanitize_fts5_query(query)
        
        try:
            # FTS5 search with BM25 ranking
            cursor.execute("""
                SELECT chunk_id, doc_id, text, bm25(chunks_fts) as score
                FROM chunks_fts
                WHERE chunks_fts MATCH ?
                ORDER BY score
                LIMIT ?
            """, (sanitized_query, top_k))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "chunk_id": row["chunk_id"],
                    "doc_id": row["doc_id"],
                    "text": row["text"],
                    "score": -row["score"]  # BM25 returns negative scores, lower is better
                })
            
            return results
        except sqlite3.DatabaseError as e:
            error_msg = str(e)
            if "malformed" in error_msg.lower() or "corrupt" in error_msg.lower():
                logger.error(f"Database corruption detected: {e}")
                raise sqlite3.DatabaseError(
                    "Database disk image is malformed. "
                    "Please rebuild the RAG index by running 'Build RAG Index' again in the Data Collection tab."
                )
            raise
    
    def check_integrity(self) -> bool:
        """Check database integrity."""
        if self.conn is None:
            self.connect()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            return "ok" in result.lower()
        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            return False
    
    def clear_all_data(self):
        """Clear all data from database (useful when rebuilding index)."""
        if self.conn is None:
            self.connect()
        
        cursor = self.conn.cursor()
        try:
            # Drop and recreate tables
            cursor.execute("DROP TABLE IF EXISTS chunks_fts")
            cursor.execute("DROP TABLE IF EXISTS chunks")
            cursor.execute("DROP TABLE IF EXISTS documents")
            self.conn.commit()
            # Recreate tables
            self.create_tables()
            logger.info("Cleared all data from SQLite database")
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            self.conn.rollback()
            raise
    
    def close(self):
        """Close database connection."""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            self.conn = None

