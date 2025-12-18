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


<img width="1562" height="1190" alt="image" src="https://github.com/user-attachments/assets/d9f10e90-319a-4b1a-9d54-ba2a97ecaa9a" />

<img width="1562" height="1190" alt="image" src="https://github.com/user-attachments/assets/0d6d4590-ef07-4730-9ae6-9e03bcdfd907" />

<img width="1562" height="1190" alt="image" src="https://github.com/user-attachments/assets/740ce92f-6e1f-47ae-8f28-2831c2c885cc" />

<img width="1562" height="778" alt="image" src="https://github.com/user-attachments/assets/671f9164-5a53-43e2-bb4e-603a008174be" />

<img width="1562" height="1194" alt="image" src="https://github.com/user-attachments/assets/ad704d2b-d4c7-474a-a7cd-ea9bfb7dbe8f" />

<img width="751" height="1131" alt="image" src="https://github.com/user-attachments/assets/71dbc42f-029d-443b-b4e5-a97fae7c545f" />

<img width="751" height="1078" alt="image" src="https://github.com/user-attachments/assets/d8b04aa9-d61d-42b9-9ba3-e2bd461eb1f3" />



