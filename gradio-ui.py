# ui/gradio_app.py
"""Gradio Web Interface for Academic LLM System."""

import gradio as gr
from pathlib import Path
import json
import time
from typing import Optional, List, Tuple
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import get_config, DATA_DIR, MODEL_DIR


class AcademicLLMInterface:
    """Gradio interface for the Academic LLM System."""
    
    def __init__(self):
        self.config = get_config()
        self.scraper = None
        self.extractor = None
        self.chunker = None
        self.embedder = None
        self.indexer = None
        self.hybrid_retriever = None
        self.qa_generator = None
        self.trainer = None
        self.base_loader = None
        self.ft_loader = None
        self.initialized = False
        
    def initialize_modules(self, progress=gr.Progress()):
        """Initialize all modules."""
        progress(0, desc="Initializing modules...")
        
        try:
            from modules.m2_data_collection import ArxivScraper, PDFExtractor
            from modules.m3_rag_pipeline import DocumentChunker, EmbeddingGenerator, FAISSIndexer
            from modules.m4_hybrid_retrieval import SQLiteFTS, HybridRetriever
            from modules.m1_langchain_llama import LLMLoader
            
            progress(0.2, desc="Loading scrapers...")
            self.scraper = ArxivScraper()
            self.extractor = PDFExtractor()
            
            progress(0.4, desc="Loading embedding model...")
            self.embedder = EmbeddingGenerator()
            self.embedder.load_model()
            
            progress(0.6, desc="Setting up indexers...")
            self.chunker = DocumentChunker()
            self.indexer = FAISSIndexer(self.embedder.get_dimension())
            
            self.sqlite_fts = SQLiteFTS()
            self.sqlite_fts.connect()
            self.sqlite_fts.create_tables()
            
            progress(0.8, desc="Loading LLM...")
            self.base_loader = LLMLoader()
            
            progress(1.0, desc="Done!")
            self.initialized = True
            
            return "✅ All modules initialized successfully!"
            
        except Exception as e:
            logger.error(f"Init error: {e}")
            return f"❌ Error: {str(e)}"
    
    # === Tab 1: Data Collection ===
    def collect_papers(
        self, 
        category: str, 
        query: str, 
        num_papers: int,
        progress=gr.Progress()
    ) -> Tuple[str, str]:
        """Collect papers from arXiv."""
        if not self.scraper:
            return "❌ Please initialize modules first!", ""
        
        try:
            progress(0.2, desc="Searching arXiv...")
            papers = self.scraper.search_papers(
                category=category,
                query=query if query else None,
                max_results=int(num_papers)
            )
            
            progress(0.5, desc="Downloading PDFs...")
            self.scraper.download_pdfs(papers)
            
            progress(0.8, desc="Saving metadata...")
            self.scraper.save_metadata()
            
            # Format preview
            preview = "## Collected Papers\n\n"
            for i, p in enumerate(papers[:10], 1):
                preview += f"**{i}. {p.title}**\n"
                preview += f"   - arXiv: {p.arxiv_id}\n"
                preview += f"   - Authors: {', '.join(p.authors[:3])}...\n\n"
            
            if len(papers) > 10:
                preview += f"... and {len(papers) - 10} more papers"
            
            progress(1.0, desc="Complete!")
            return f"✅ Collected {len(papers)} papers!", preview
            
        except Exception as e:
            logger.error(f"Collection error: {e}")
            return f"❌ Error: {str(e)}", ""
    
    def process_and_index(self, progress=gr.Progress()) -> str:
        """Extract text and build index."""
        if not self.scraper or not self.indexer:
            return "❌ Please initialize modules first!"
        
        try:
            progress(0.1, desc="Loading metadata...")
            papers = self.scraper.load_metadata()
            
            progress(0.2, desc="Extracting text from PDFs...")
            pdf_paths = [p.local_pdf_path for p in papers if p.local_pdf_path]
            metadata_list = [{"title": p.title, "arxiv_id": p.arxiv_id} for p in papers if p.local_pdf_path]
            
            documents = self.extractor.extract_batch(pdf_paths, metadata_list)
            
            progress(0.4, desc="Chunking documents...")
            all_chunks = []
            for doc in documents:
                chunks = self.chunker.chunk_document(
                    doc.arxiv_id,
                    doc.full_text,
                    {"title": doc.title}
                )
                all_chunks.extend(chunks)
            
            progress(0.6, desc="Generating embeddings...")
            embeddings = self.embedder.embed_chunks(all_chunks)
            
            progress(0.8, desc="Building FAISS index...")
            self.indexer.create_index()
            self.indexer.add_vectors(embeddings, all_chunks)
            self.indexer.save("academic_index")
            
            progress(0.9, desc="Adding to SQLite FTS...")
            self.sqlite_fts.add_chunks_batch(all_chunks)
            
            # Setup hybrid retriever
            from modules.m4_hybrid_retrieval import HybridRetriever
            self.hybrid_retriever = HybridRetriever(
                self.indexer, self.sqlite_fts, self.embedder
            )
            
            progress(1.0, desc="Complete!")
            return f"✅ Indexed {len(all_chunks)} chunks from {len(documents)} documents!"
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return f"❌ Error: {str(e)}"
    
    # === Tab 2: RAG Search ===
    def search_documents(
        self, 
        query: str, 
        search_type: str, 
        top_k: int
    ) -> str:
        """Search indexed documents."""
        if not self.hybrid_retriever:
            return "❌ Please build index first!"
        
        try:
            results = self.hybrid_retriever.search(query, top_k=int(top_k))
            
            output = f"## Search Results for: '{query}'\n\n"
            output += f"Search type: {search_type}\n\n"
            
            for i, r in enumerate(results, 1):
                output += f"### Result {i} (Score: {r.score:.4f})\n"
                output += f"**Document:** {r.doc_id}\n"
                output += f"**Text:** {r.text[:400]}...\n\n"
                output += "---\n\n"
            
            return output
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # === Tab 3: Synthetic Data ===
    def generate_synthetic_data(
        self, 
        num_papers: int, 
        qa_per_paper: int,
        progress=gr.Progress()
    ) -> Tuple[str, str]:
        """Generate synthetic Q&A data."""
        try:
            from modules.m5_synthetic_data import QAGenerator, DatasetBuilder
            
            progress(0.1, desc="Loading papers...")
            papers = self.scraper.load_metadata()[:int(num_papers)]
            
            # Convert to dict format
            papers_dict = [
                {
                    "arxiv_id": p.arxiv_id,
                    "title": p.title,
                    "abstract": p.abstract,
                    "full_text": p.abstract  # Use abstract for speed
                }
                for p in papers
            ]
            
            progress(0.2, desc="Generating Q&A pairs...")
            generator = QAGenerator()
            qa_pairs = generator.generate_batch(
                papers_dict,
                qa_per_paper=int(qa_per_paper)
            )
            
            progress(0.8, desc="Building dataset...")
            builder = DatasetBuilder()
            dataset = builder.build_instruct_dataset(qa_pairs)
            filepath = builder.save_jsonl(dataset)
            
            # Preview
            preview = "## Sample Q&A Pairs\n\n"
            for i, qa in enumerate(qa_pairs[:5], 1):
                preview += f"**Q{i}:** {qa['question']}\n\n"
                preview += f"**A{i}:** {qa['answer'][:200]}...\n\n"
                preview += "---\n\n"
            
            progress(1.0, desc="Complete!")
            return f"✅ Generated {len(qa_pairs)} Q&A pairs!\nSaved to: {filepath}", preview
            
        except ValueError as e:
            # API key or configuration errors
            error_msg = str(e)
            if "API key" in error_msg.lower():
                error_msg += "\n\n💡 提示：请设置 OPENAI_API_KEY 环境变量或创建 .env 文件"
            logger.error(f"Generation error: {e}")
            return f"❌ Error: {error_msg}", ""
        except Exception as e:
            logger.error(f"Generation error: {e}")
            error_msg = str(e)
            # Add helpful context for common errors
            if "api" in error_msg.lower() or "key" in error_msg.lower():
                error_msg += "\n\n💡 提示：请检查 OpenAI API key 是否正确设置"
            return f"❌ Error: {error_msg}", ""
    
    # === Tab 4: Fine-Tuning ===
    def run_finetuning(
        self, 
        epochs: int, 
        batch_size: int, 
        learning_rate: float,
        progress=gr.Progress()
    ) -> str:
        """Run QLoRA fine-tuning."""
        try:
            from modules.m6_fine_tuning import QLoRATrainer
            
            progress(0.1, desc="Setting up trainer...")
            trainer = QLoRATrainer()
            
            progress(0.2, desc="Loading model...")
            trainer.setup()
            
            progress(0.3, desc="Loading dataset...")
            dataset = trainer.load_dataset()
            
            progress(0.4, desc="Fine-tuning (this may take a while)...")
            results = trainer.train(
                dataset,
                epochs=int(epochs),
                batch_size=int(batch_size)
            )
            
            progress(1.0, desc="Complete!")
            return f"""✅ Fine-tuning complete!

**Results:**
- Training Loss: {results['train_loss']:.4f}
- Runtime: {results['train_runtime']:.1f}s
- Model saved to: {results['output_dir']}
"""
            
        except Exception as e:
            logger.error(f"Fine-tuning error: {e}")
            return f"❌ Error: {str(e)}"
    
    # === Tab 5: Chat & Compare ===
    def chat_with_model(
        self, 
        message: str, 
        model_type: str,
        use_rag: bool,
        history: List
    ) -> Tuple[List, str]:
        """Chat with the model."""
        # Ensure history is a list (handle None or invalid formats)
        if history is None:
            history = []
        elif not isinstance(history, list):
            history = []
        
        # Gradio 6.0+ uses dict format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
        # Clean and normalize history format
        cleaned_history = []
        for item in history:
            if isinstance(item, dict) and 'role' in item and 'content' in item:
                # Already in dict format
                cleaned_history.append(item)
            elif isinstance(item, tuple) and len(item) == 2:
                # Convert tuple format to dict format
                user_msg, bot_msg = item
                if user_msg:
                    cleaned_history.append({"role": "user", "content": str(user_msg)})
                if bot_msg:
                    cleaned_history.append({"role": "assistant", "content": str(bot_msg)})
            elif isinstance(item, list) and len(item) == 2:
                # List format, convert to dict
                user_msg, bot_msg = item
                if user_msg:
                    cleaned_history.append({"role": "user", "content": str(user_msg)})
                if bot_msg:
                    cleaned_history.append({"role": "assistant", "content": str(bot_msg)})
        
        history = cleaned_history
        
        if not self.base_loader:
            # Gradio 6.0+ uses dict format: [{"role": "user", "content": "..."}, ...]
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": "❌ Please initialize modules first!"})
            return history, ""
        
        if not message or not message.strip():
            return history, ""
        
        try:
            # Load appropriate model
            if model_type == "Fine-tuned" and not self.ft_loader:
                from modules.m1_langchain_llama import LLMLoader
                self.ft_loader = LLMLoader()
                self.ft_loader.load_finetuned_model()
            
            loader = self.ft_loader if model_type == "Fine-tuned" else self.base_loader
            
            # Ensure model is loaded
            if loader.model is None:
                loader.load_base_model() if model_type == "Base" else loader.load_finetuned_model()
            
            # Get RAG context
            context = ""
            if use_rag and self.hybrid_retriever:
                results = self.hybrid_retriever.search(message, top_k=3)
                context = "\n\n".join([f"[{r.doc_id}]: {r.text[:300]}" for r in results])
            
            # Build prompt
            if context:
                full_message = f"Context:\n{context}\n\nQuestion: {message}"
            else:
                full_message = message
            
            prompt = loader.format_prompt(full_message)
            response = loader.generate(prompt)
            
            # Add messages in dict format for Gradio 6.0+
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})
            return history, ""
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": f"❌ Error: {str(e)}"})
            return history, ""
    
    def compare_models(self, question: str) -> str:
        """Compare base and fine-tuned model responses."""
        try:
            from modules.m1_langchain_llama import LLMLoader
            
            # Base model response
            if self.base_loader.model is None:
                self.base_loader.load_base_model()
            
            base_prompt = self.base_loader.format_prompt(question)
            base_response = self.base_loader.generate(base_prompt)
            
            # Fine-tuned response
            if not self.ft_loader:
                self.ft_loader = LLMLoader()
                self.ft_loader.load_finetuned_model()
            
            ft_prompt = self.ft_loader.format_prompt(question)
            ft_response = self.ft_loader.generate(ft_prompt)
            
            return f"""## Model Comparison

### Question
{question}

---

### 🔵 Base Model Response
{base_response}

---

### 🟢 Fine-tuned Model Response
{ft_response}

---

### Analysis
Compare the responses above. The fine-tuned model should show:
- Better domain knowledge
- More accurate terminology
- More relevant answers to academic questions
"""
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        
        with gr.Blocks(
            title="Academic LLM Fine-Tuning System"
        ) as interface:
            
            gr.Markdown("""
            # 🎓 Academic LLM Fine-Tuning System
            
            Build a custom academic Q&A assistant using RAG and QLoRA fine-tuning.
            
            **Pipeline:** Data Collection → RAG Index → Synthetic Data → Fine-Tuning → Evaluation
            """)
            
            # Initialize button
            with gr.Row():
                init_btn = gr.Button("🚀 Initialize System", variant="primary", scale=2)
                init_status = gr.Textbox(label="Status", scale=3)
            
            init_btn.click(self.initialize_modules, outputs=init_status)
            
            with gr.Tabs():
                # Tab 1: Data Collection
                with gr.TabItem("📚 Data Collection"):
                    gr.Markdown("### Collect papers from arXiv")
                    
                    with gr.Row():
                        category = gr.Textbox(value="cs.CL", label="arXiv Category")
                        query = gr.Textbox(label="Search Query (optional)", placeholder="e.g., transformer attention")
                        num_papers = gr.Slider(10, 100, value=50, step=10, label="Number of Papers")
                    
                    collect_btn = gr.Button("📥 Collect Papers", variant="primary")
                    collect_status = gr.Textbox(label="Collection Status")
                    papers_preview = gr.Markdown(label="Collected Papers")
                    
                    collect_btn.click(
                        self.collect_papers,
                        inputs=[category, query, num_papers],
                        outputs=[collect_status, papers_preview]
                    )
                    
                    gr.Markdown("---")
                    process_btn = gr.Button("⚙️ Process & Build Index", variant="secondary")
                    process_status = gr.Textbox(label="Processing Status")
                    
                    process_btn.click(self.process_and_index, outputs=process_status)
                
                # Tab 2: RAG Search
                with gr.TabItem("🔍 RAG Search"):
                    gr.Markdown("### Search your indexed papers")
                    
                    with gr.Row():
                        search_query = gr.Textbox(label="Search Query", placeholder="What is attention mechanism?")
                        search_type = gr.Radio(["hybrid", "vector", "keyword"], value="hybrid", label="Search Type")
                        top_k = gr.Slider(1, 10, value=5, step=1, label="Top K Results")
                    
                    search_btn = gr.Button("🔎 Search", variant="primary")
                    search_results = gr.Markdown(label="Results")
                    
                    search_btn.click(
                        self.search_documents,
                        inputs=[search_query, search_type, top_k],
                        outputs=search_results
                    )
                
                # Tab 3: Synthetic Data
                with gr.TabItem("🧪 Synthetic Data"):
                    gr.Markdown("### Generate Q&A training data using GPT-4")
                    
                    with gr.Row():
                        syn_papers = gr.Slider(10, 100, value=50, step=10, label="Papers to Process")
                        qa_per_paper = gr.Slider(1, 10, value=5, step=1, label="Q&A per Paper")
                    
                    generate_btn = gr.Button("🔄 Generate Q&A Data", variant="primary")
                    generate_status = gr.Textbox(label="Generation Status")
                    qa_preview = gr.Markdown(label="Sample Q&A")
                    
                    generate_btn.click(
                        self.generate_synthetic_data,
                        inputs=[syn_papers, qa_per_paper],
                        outputs=[generate_status, qa_preview]
                    )
                
                # Tab 4: Fine-Tuning
                with gr.TabItem("🔧 Fine-Tuning"):
                    gr.Markdown("### QLoRA Fine-tune LLaMA 3")
                    
                    with gr.Row():
                        epochs = gr.Slider(1, 5, value=2, step=1, label="Epochs")
                        batch_size = gr.Slider(1, 8, value=2, step=1, label="Batch Size")
                        lr = gr.Number(value=2e-4, label="Learning Rate")
                    
                    train_btn = gr.Button("🚀 Start Fine-Tuning", variant="primary")
                    train_status = gr.Textbox(label="Training Status", lines=8)
                    
                    train_btn.click(
                        self.run_finetuning,
                        inputs=[epochs, batch_size, lr],
                        outputs=train_status
                    )
                
                # Tab 5: Chat & Compare
                with gr.TabItem("💬 Chat & Compare"):
                    gr.Markdown("### Test your models")
                    
                    with gr.Row():
                        with gr.Column():
                            chatbot = gr.Chatbot(height=400, label="Chat", value=[])  # Gradio 6.0.2 supports dict format directly via value parameter
                            with gr.Row():
                                chat_input = gr.Textbox(label="Message", placeholder="Ask a question...")
                                model_select = gr.Radio(["Base", "Fine-tuned"], value="Fine-tuned", label="Model")
                            use_rag = gr.Checkbox(value=True, label="Use RAG Context")
                            chat_btn = gr.Button("Send", variant="primary")
                        
                        with gr.Column():
                            compare_input = gr.Textbox(label="Comparison Question", lines=2)
                            compare_btn = gr.Button("Compare Models", variant="secondary")
                            compare_output = gr.Markdown(label="Comparison Results")
                    
                    chat_btn.click(
                        self.chat_with_model,
                        inputs=[chat_input, model_select, use_rag, chatbot],
                        outputs=[chatbot, chat_input]
                    )
                    
                    compare_btn.click(
                        self.compare_models,
                        inputs=compare_input,
                        outputs=compare_output
                    )
        
        return interface


def launch_app():
    """Launch the Gradio app."""
    import os

    # Allow overriding port via environment variable, default 7860
    port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))

    app = AcademicLLMInterface()
    interface = app.create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=True
    )


if __name__ == "__main__":
    launch_app()
