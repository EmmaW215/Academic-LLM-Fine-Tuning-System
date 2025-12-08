# Academic LLM Fine-Tuning System

A comprehensive system for building a custom academic Q&A assistant using RAG (Retrieval Augmented Generation) and QLoRA fine-tuning.

<img width="1289" height="850" alt="image" src="https://github.com/user-attachments/assets/f6bfbdcb-8731-4b34-b418-d8cfbbefc415" />

## 🚀 Features

- **Data Collection**: Automated arXiv paper scraping and PDF processing
- **RAG Pipeline**: Hybrid retrieval combining vector search (FAISS) and keyword search (SQLite FTS5)
- **Synthetic Data Generation**: GPT-4 powered Q&A pair generation for fine-tuning
- **QLoRA Fine-Tuning**: Efficient fine-tuning of LLaMA 3.1 8B model with 4-bit quantization
- **Gradio UI**: Interactive web interface for testing and comparing models
- **FastAPI Backend**: RESTful API for integration with external applications

## 📋 Requirements

- Python 3.10+
- CUDA-capable GPU (recommended)
- OpenAI API key (for synthetic data generation)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/EmmaW215/Academic-LLM-Fine-Tuning-System.git
cd Academic-LLM-Fine-Tuning-System
```

2. Install dependencies:
```bash
pip install -r requirements-file.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## 🎯 Quick Start

### Option 1: Gradio UI (Recommended for beginners)

```bash
export GRADIO_SERVER_PORT=7861
python gradio-ui.py
```

Then access the UI at `http://localhost:7861`

### Option 2: Pipeline Runner

```bash
python pipeline-runner.py
```

### Option 3: FastAPI Server

```bash
uvicorn module8-api:app --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
├── config/              # Configuration files
├── modules/             # Core modules
│   ├── m1_langchain_llama/    # LLM loading and chain building
│   ├── m2_data_collection/    # arXiv scraping
│   ├── m3_rag_pipeline/       # RAG indexing
│   ├── m4_hybrid_retrieval/  # Hybrid search (FAISS + SQLite)
│   ├── m5_synthetic_data/    # Q&A generation
│   ├── m6_fine_tuning/       # QLoRA training
│   └── m8_api_service/       # FastAPI endpoints
├── storage/            # Data, indexes, and models
├── gradio-ui.py        # Main Gradio interface
├── module8-api.py       # FastAPI application
└── pipeline-runner.py   # Full pipeline execution
```

## 🔧 Configuration

Edit `config/settings.py` to customize:
- Model selection (base model, embedding model)
- Training parameters (LoRA rank, learning rate, etc.)
- RAG settings (top-k retrieval, similarity thresholds)
- Data collection (arXiv categories, number of papers)

## 📚 Documentation

- [Setup Guide](SETUP_OPENAI.md) - Setting up OpenAI API
- [Deployment Guide](deployment-guide.md) - Production deployment
- [Restart Guide](RESTART_GRADIO.md) - Troubleshooting Gradio UI

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/)
- Fine-tuning powered by [Unsloth](https://github.com/unslothai/unsloth)
- UI built with [Gradio](https://www.gradio.app/)

<img width="1092" height="1211" alt="image" src="https://github.com/user-attachments/assets/f8516e71-9e89-4dc3-8a06-7c3c71a022a5" />

<img width="1092" height="1211" alt="image" src="https://github.com/user-attachments/assets/7f457901-4ce6-401c-bca8-cc5086d42137" />

<img width="1092" height="1204" alt="image" src="https://github.com/user-attachments/assets/9ebf58d8-3233-4ac7-8de5-97ec60d27f7e" />

<img width="1020" height="779" alt="image" src="https://github.com/user-attachments/assets/72e128d7-b087-4dc4-bb0a-98bd2b0e8bc7" />





