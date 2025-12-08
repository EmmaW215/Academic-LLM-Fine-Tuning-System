# modules/m8_api_service/__init__.py
"""Module 8: FastAPI Service."""

from .main import create_app

__all__ = ["create_app"]


# modules/m8_api_service/schemas.py
"""Pydantic schemas for API."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class ModelType(str, Enum):
    BASE = "base"
    FINETUNED = "finetuned"


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    search_type: str = Field(default="hybrid", pattern="^(vector|keyword|hybrid)$")


class SearchResult(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    score: float
    metadata: Dict = {}


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    search_type: str
    total_results: int


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    model_type: ModelType = ModelType.FINETUNED
    use_rag: bool = True
    max_tokens: int = Field(default=512, ge=64, le=2048)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    message: str
    model_used: str
    sources: List[SearchResult] = []
    latency_ms: float


class EvaluateRequest(BaseModel):
    questions: List[str]
    expected_answers: Optional[List[str]] = None


class ComparisonResponse(BaseModel):
    question: str
    base_answer: str
    finetuned_answer: str
    base_score: float
    finetuned_score: float
    winner: str


class PipelineStatus(BaseModel):
    status: str
    papers_collected: int = 0
    chunks_indexed: int = 0
    qa_pairs_generated: int = 0
    model_trained: bool = False
    last_updated: Optional[str] = None


class DataCollectionRequest(BaseModel):
    category: str = Field(default="cs.CL", description="arXiv category")
    query: Optional[str] = Field(default=None, description="Search query")
    num_papers: int = Field(default=50, ge=10, le=100, description="Number of papers to collect")


class DataCollectionResponse(BaseModel):
    status: str
    papers_collected: int
    preview: str = ""


class IndexBuildResponse(BaseModel):
    status: str
    chunks_indexed: int
    documents_processed: int


class SyntheticDataRequest(BaseModel):
    num_papers: int = Field(default=50, ge=10, le=100)
    qa_per_paper: int = Field(default=5, ge=1, le=10)


class SyntheticDataResponse(BaseModel):
    status: str
    qa_pairs_generated: int
    filepath: str
    preview: str = ""


class FineTuningRequest(BaseModel):
    epochs: int = Field(default=3, ge=1, le=10)
    batch_size: int = Field(default=2, ge=1, le=8)
    learning_rate: float = Field(default=0.0002, ge=0.0001, le=0.001)


class FineTuningResponse(BaseModel):
    status: str
    train_loss: Optional[float] = None
    train_runtime: Optional[float] = None
    output_dir: Optional[str] = None
    message: str


# modules/m8_api_service/main.py
"""FastAPI application."""

import time
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.settings import get_config, INDEX_DIR
from .schemas import (
    SearchRequest, SearchResponse, SearchResult,
    ChatRequest, ChatResponse,
    ComparisonResponse, PipelineStatus, ModelType
)


# Global state
class AppState:
    def __init__(self):
        self.config = get_config()
        self.embedder = None
        self.faiss_indexer = None
        self.sqlite_fts = None
        self.hybrid_retriever = None
        self.base_model = None
        self.base_tokenizer = None
        self.ft_model = None
        self.ft_tokenizer = None
        self.llm_loader = None
        self.initialized = False


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Academic LLM API...")
    
    # Initialize components
    try:
        from modules.m3_rag_pipeline import EmbeddingGenerator, FAISSIndexer
        from modules.m4_hybrid_retrieval import SQLiteFTS, HybridRetriever
        from modules.m1_langchain_llama import LLMLoader
        
        # Load embedder
        state.embedder = EmbeddingGenerator()
        state.embedder.load_model()
        
        # Load FAISS index if exists
        faiss_path = INDEX_DIR / "faiss" / "academic_index.faiss"
        if faiss_path.exists():
            state.faiss_indexer = FAISSIndexer(state.embedder.get_dimension())
            state.faiss_indexer.load("academic_index")
            logger.info("Loaded FAISS index")
        
        # Load SQLite FTS
        state.sqlite_fts = SQLiteFTS()
        state.sqlite_fts.connect()
        
        # Setup hybrid retriever if both are available
        if state.faiss_indexer:
            state.hybrid_retriever = HybridRetriever(
                state.faiss_indexer,
                state.sqlite_fts,
                state.embedder
            )
        
        # Load LLM (lazy - only when needed)
        state.llm_loader = LLMLoader()
        
        state.initialized = True
        logger.info("API initialized successfully")
        
    except Exception as e:
        logger.error(f"Initialization error: {e}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    if state.sqlite_fts:
        state.sqlite_fts.close()


def create_app() -> FastAPI:
    """Create FastAPI application."""
    
    app = FastAPI(
        title="Academic LLM API",
        description="RAG-enhanced Academic Q&A with Fine-tuned LLaMA",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "initialized": state.initialized,
            "index_loaded": state.faiss_indexer is not None
        }
    
    # Search endpoint
    @app.post("/search", response_model=SearchResponse)
    async def search(request: SearchRequest):
        if not state.hybrid_retriever:
            raise HTTPException(503, "Search index not initialized")
        
        try:
            if request.search_type == "hybrid":
                results = state.hybrid_retriever.search(
                    request.query, 
                    top_k=request.top_k
                )
            elif request.search_type == "vector":
                query_emb = state.embedder.embed_text(request.query)
                results_raw = state.faiss_indexer.search(query_emb, request.top_k)
                results = [
                    SearchResult(
                        chunk_id=c.chunk_id,
                        doc_id=c.doc_id,
                        text=c.text,
                        score=s,
                        metadata=c.metadata
                    ) for c, s in results_raw
                ]
            else:  # keyword
                results_raw = state.sqlite_fts.search(request.query, request.top_k)
                results = [
                    SearchResult(
                        chunk_id=r["chunk_id"],
                        doc_id=r["doc_id"],
                        text=r["text"],
                        score=r["score"],
                        metadata={}
                    ) for r in results_raw
                ]
            
            # Convert to response format
            search_results = []
            for r in results:
                if hasattr(r, 'chunk_id'):
                    search_results.append(SearchResult(
                        chunk_id=r.chunk_id,
                        doc_id=r.doc_id,
                        text=r.text[:500],
                        score=r.score,
                        metadata=getattr(r, 'metadata', {})
                    ))
            
            return SearchResponse(
                query=request.query,
                results=search_results,
                search_type=request.search_type,
                total_results=len(search_results)
            )
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise HTTPException(500, str(e))
    
    # Chat endpoint
    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        start_time = time.time()
        
        try:
            # Load model if needed
            if request.model_type == ModelType.FINETUNED:
                if state.ft_model is None:
                    state.ft_model, state.ft_tokenizer = state.llm_loader.load_finetuned_model()
                model, tokenizer = state.ft_model, state.ft_tokenizer
                model_name = "finetuned"
            else:
                if state.base_model is None:
                    state.base_model, state.base_tokenizer = state.llm_loader.load_base_model()
                model, tokenizer = state.base_model, state.base_tokenizer
                model_name = "base"
            
            # Get context from RAG if enabled
            sources = []
            context = ""
            if request.use_rag and state.hybrid_retriever:
                results = state.hybrid_retriever.search(request.message, top_k=3)
                context = "\n\n".join([r.text for r in results[:3]])
                sources = [
                    SearchResult(
                        chunk_id=r.chunk_id,
                        doc_id=r.doc_id,
                        text=r.text[:200],
                        score=r.score,
                        metadata={}
                    ) for r in results[:3]
                ]
            
            # Format prompt
            if context:
                user_message = f"""Based on the following research context, answer the question.

Context:
{context}

Question: {request.message}"""
            else:
                user_message = request.message
            
            prompt = state.llm_loader.format_prompt(user_message)
            
            # Generate
            response = state.llm_loader.generate(
                prompt,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            latency = (time.time() - start_time) * 1000
            
            return ChatResponse(
                message=response,
                model_used=model_name,
                sources=sources,
                latency_ms=latency
            )
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise HTTPException(500, str(e))
    
    # Compare models endpoint
    @app.post("/compare")
    async def compare_models(question: str):
        try:
            # Ensure both models loaded
            if state.base_model is None:
                state.base_model, state.base_tokenizer = state.llm_loader.load_base_model()
            
            # Load fresh base for comparison
            from modules.m1_langchain_llama import LLMLoader
            base_loader = LLMLoader()
            base_model, base_tok = base_loader.load_base_model()
            
            # Get fine-tuned response
            ft_loader = LLMLoader()
            ft_model, ft_tok = ft_loader.load_finetuned_model()
            
            prompt = state.llm_loader.format_prompt(question)
            
            base_response = base_loader.generate(prompt)
            ft_response = ft_loader.generate(prompt)
            
            return {
                "question": question,
                "base_response": base_response,
                "finetuned_response": ft_response
            }
            
        except Exception as e:
            logger.error(f"Compare error: {e}")
            raise HTTPException(500, str(e))
    
    # Pipeline status
    @app.get("/status", response_model=PipelineStatus)
    async def get_status():
        from config.settings import DATA_DIR
        import os
        
        # Count papers
        papers_file = DATA_DIR / "processed" / "papers_metadata.json"
        papers_count = 0
        if papers_file.exists():
            try:
                import json
                with open(papers_file) as f:
                    papers = json.load(f)
                    papers_count = len(papers) if isinstance(papers, list) else 0
            except:
                pass
        
        # Count QA pairs
        qa_file = DATA_DIR / "synthetic" / "synthetic_qa.jsonl"
        qa_count = 0
        if qa_file.exists():
            try:
                with open(qa_file) as f:
                    qa_count = sum(1 for _ in f)
            except:
                pass
        
        return PipelineStatus(
            status="ready" if state.initialized else "initializing",
            papers_collected=papers_count,
            chunks_indexed=state.faiss_indexer.index.ntotal if state.faiss_indexer else 0,
            qa_pairs_generated=qa_count,
            model_trained=Path(state.config.training.output_dir).exists()
        )
    
    # Data collection endpoint
    @app.post("/collect", response_model=DataCollectionResponse)
    async def collect_papers(request: DataCollectionRequest, background_tasks: BackgroundTasks):
        """Collect papers from arXiv."""
        try:
            from modules.m2_data_collection import ArxivScraper
            
            scraper = ArxivScraper()
            
            # Run in background
            def collect_task():
                papers = scraper.search_papers(
                    category=request.category,
                    query=request.query,
                    max_results=request.num_papers
                )
                scraper.download_pdfs(papers)
                scraper.save_metadata()
                return len(papers)
            
            background_tasks.add_task(collect_task)
            
            return DataCollectionResponse(
                status="✅ Paper collection started in background. This may take a few minutes.",
                papers_collected=0,
                preview="Collection in progress..."
            )
        except Exception as e:
            logger.error(f"Collection error: {e}")
            raise HTTPException(500, str(e))
    
    # Index building endpoint
    @app.post("/build-index", response_model=IndexBuildResponse)
    async def build_index(background_tasks: BackgroundTasks):
        """Build RAG index from collected papers."""
        try:
            from modules.m2_data_collection import ArxivScraper, PDFExtractor
            from modules.m3_rag_pipeline import DocumentChunker, EmbeddingGenerator, FAISSIndexer
            from modules.m4_hybrid_retrieval import SQLiteFTS
            
            def build_task():
                # Load papers
                scraper = ArxivScraper()
                papers = scraper.load_metadata()
                
                # Extract text
                extractor = PDFExtractor()
                pdf_paths = [p.local_pdf_path for p in papers if p.local_pdf_path]
                metadata_list = [{"title": p.title, "arxiv_id": p.arxiv_id} for p in papers if p.local_pdf_path]
                documents = extractor.extract_batch(pdf_paths, metadata_list)
                
                # Chunk
                chunker = DocumentChunker()
                all_chunks = []
                for doc in documents:
                    chunks = chunker.chunk_document(
                        doc.arxiv_id,
                        doc.full_text,
                        {"title": doc.title}
                    )
                    all_chunks.extend(chunks)
                
                # Generate embeddings
                embedder = EmbeddingGenerator()
                embedder.load_model()
                embeddings = embedder.embed_chunks(all_chunks)
                
                # Build FAISS index
                indexer = FAISSIndexer(embedder.get_dimension())
                indexer.create_index()
                indexer.add_vectors(embeddings, all_chunks)
                indexer.save("academic_index")
                
                # Build SQLite FTS
                fts = SQLiteFTS()
                fts.connect()
                if not fts.check_integrity():
                    fts.clear_all_data()
                else:
                    fts.create_tables()
                fts.add_chunks_batch(all_chunks)
                fts.close()
                
                return len(all_chunks), len(documents)
            
            background_tasks.add_task(build_task)
            
            return IndexBuildResponse(
                status="✅ Index building started in background. This may take several minutes.",
                chunks_indexed=0,
                documents_processed=0
            )
        except Exception as e:
            logger.error(f"Index building error: {e}")
            raise HTTPException(500, str(e))
    
    # Synthetic data generation endpoint
    @app.post("/generate-synthetic", response_model=SyntheticDataResponse)
    async def generate_synthetic(request: SyntheticDataRequest, background_tasks: BackgroundTasks):
        """Generate synthetic Q&A data."""
        try:
            from modules.m5_synthetic_data import QAGenerator, DatasetBuilder
            from modules.m2_data_collection import ArxivScraper
            
            def generate_task():
                scraper = ArxivScraper()
                papers = scraper.load_metadata()[:request.num_papers]
                
                papers_dict = [
                    {
                        "arxiv_id": p.arxiv_id,
                        "title": p.title,
                        "abstract": p.abstract,
                        "full_text": p.abstract
                    }
                    for p in papers
                ]
                
                generator = QAGenerator()
                qa_pairs = generator.generate_batch(
                    papers_dict,
                    qa_per_paper=request.qa_per_paper
                )
                
                builder = DatasetBuilder()
                dataset = builder.build_instruct_dataset(qa_pairs)
                filepath = builder.save_jsonl(dataset)
                
                return len(qa_pairs), filepath
            
            background_tasks.add_task(generate_task)
            
            return SyntheticDataResponse(
                status="✅ Synthetic data generation started in background. This may take a while.",
                qa_pairs_generated=0,
                filepath="",
                preview="Generation in progress..."
            )
        except Exception as e:
            logger.error(f"Synthetic generation error: {e}")
            error_msg = str(e)
            if "API key" in error_msg.lower():
                error_msg += "\n\n💡 Please set OPENAI_API_KEY environment variable."
            raise HTTPException(500, error_msg)
    
    # Fine-tuning endpoint
    @app.post("/finetune", response_model=FineTuningResponse)
    async def finetune(request: FineTuningRequest, background_tasks: BackgroundTasks):
        """Start fine-tuning process."""
        try:
            from modules.m6_fine_tuning import QLoRATrainer
            
            def train_task():
                trainer = QLoRATrainer()
                trainer.setup()
                dataset = trainer.load_dataset()
                results = trainer.train(
                    dataset,
                    epochs=request.epochs,
                    batch_size=request.batch_size
                )
                return results
            
            background_tasks.add_task(train_task)
            
            return FineTuningResponse(
                status="✅ Fine-tuning started in background. This will take a long time (hours).",
                message="Training in progress. Check status endpoint for updates."
            )
        except Exception as e:
            logger.error(f"Fine-tuning error: {e}")
            error_msg = str(e)
            if "dataset" in error_msg.lower() or "empty" in error_msg.lower():
                error_msg += "\n\n💡 Please generate synthetic data first."
            raise HTTPException(500, error_msg)
    
    return app


# Run with: uvicorn modules.m8_api_service.main:app --host 0.0.0.0 --port 8000
app = create_app()


if __name__ == "__main__":
    import uvicorn
    config = get_config()
    uvicorn.run(app, host=config.api.host, port=config.api.port)
