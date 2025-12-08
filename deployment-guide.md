# 🚀 Deployment Guide - Academic LLM System

## Step 1: Connect to GPU Server via Cursor

### SSH Config (already set up)
```
Host gpu-server
    HostName 64.247.206.5
    User jovyan
    Port 32137
    StrictHostKeyChecking no
```

### Connect in Cursor
1. Press `Cmd+Shift+P` → "Remote-SSH: Connect to Host"
2. Select `gpu-server`
3. Open folder: `/home/jovyan/`

---

## Step 2: Clone & Setup Project

```bash
# Navigate to workspace
cd /home/jovyan

# Create project directory
mkdir -p academic_llm_system
cd academic_llm_system

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install PyTorch with CUDA (cu124 for your setup)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Install core requirements
pip install transformers>=4.40.0 accelerate>=0.27.0 bitsandbytes>=0.43.0
pip install peft>=0.10.0 datasets>=2.18.0 sentence-transformers>=2.5.0
pip install langchain>=0.1.0 langchain-community langchain-huggingface
pip install faiss-cpu arxiv PyMuPDF trafilatura langdetect datasketch
pip install fastapi uvicorn gradio pydantic sqlalchemy
pip install openai tqdm loguru python-dotenv trl

# Install Unsloth for efficient fine-tuning
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# Verify GPU
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

---

## Step 3: Create Project Structure

```bash
# Create directories
mkdir -p config modules storage/data/{raw,processed,synthetic}
mkdir -p storage/indexes/{faiss,sqlite} storage/models/{base,finetuned}
mkdir -p modules/{m1_langchain_llama,m2_data_collection,m3_rag_pipeline}
mkdir -p modules/{m4_hybrid_retrieval,m5_synthetic_data,m6_fine_tuning}
mkdir -p modules/{m7_evaluation,m8_api_service}
mkdir -p ui scripts tests
```

Copy all the code artifacts I created into their respective files.

---

## Step 4: Set Environment Variables

```bash
# Create .env file
cat > .env << 'EOF'
OPENAI_API_KEY=your_openai_api_key_here
HF_TOKEN=your_huggingface_token_here
EOF
```

---

## Step 5: Run the Pipeline

### Option A: Full Pipeline (Automated)
```bash
# Activate environment
source venv/bin/activate

# Run complete pipeline
python scripts/run_pipeline.py --step all --papers 50 --epochs 2
```

### Option B: Step-by-Step
```bash
# Step 1: Collect papers
python scripts/run_pipeline.py --step collect --papers 50 --category cs.CL

# Step 2: Build RAG index
python scripts/run_pipeline.py --step index

# Step 3: Generate synthetic Q&A data
python scripts/run_pipeline.py --step synthetic --qa-per-paper 5

# Step 4: Fine-tune model
python scripts/run_pipeline.py --step train --epochs 2

# Step 5: Evaluate
python scripts/run_pipeline.py --step eval
```

### Option C: Gradio Web Interface
```bash
# Launch Gradio UI (accessible via port forwarding)
python ui/gradio_app.py
```

---

## Step 6: Port Forwarding for Web Access

### In Cursor/VSCode
The Remote-SSH extension auto-forwards ports. When Gradio starts on 7860, you'll see a notification.

### Manual SSH Tunnel
```bash
# From your local machine
ssh -L 7860:localhost:7860 -L 8000:localhost:8000 jovyan@64.247.206.5 -p 32137
```

Then access:
- **Gradio UI**: http://localhost:7860
- **FastAPI**: http://localhost:8000

---

## Step 7: Run FastAPI Service

```bash
# Start API server
cd academic_llm_system
source venv/bin/activate
uvicorn modules.m8_api_service.main:app --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/search -H "Content-Type: application/json" \
  -d '{"query": "attention mechanism", "top_k": 5}'
```

---

## Quick Verification Test

```python
# Run quick_test.py to verify setup
python scripts/quick_test.py
```

Expected output:
```
==================================================
GPU & Environment Verification
==================================================

1. GPU Available: True
   GPU Name: NVIDIA GeForce RTX ... (16GB)
   GPU Memory: 16.0 GB

2. Checking package imports...
   ✅ transformers
   ✅ peft
   ✅ bitsandbytes
   ...

3. Testing embedding model...
   ✅ Embedding model works! Dim: 384
```

---

## Estimated Resource Usage

| Component | GPU Memory | Time |
|-----------|------------|------|
| Embedding Model | ~500 MB | 30s load |
| Base LLaMA 3 8B (4-bit) | ~6 GB | 2-3 min load |
| Fine-tuning (QLoRA) | ~10-12 GB | 15-30 min |
| Inference | ~6-8 GB | ~1s/response |

Your 16GB GPU should handle everything comfortably!

---

## Troubleshooting

### CUDA Out of Memory
```python
# Reduce batch size in config/settings.py
per_device_train_batch_size: int = 1  # Reduce from 2
gradient_accumulation_steps: int = 8  # Increase to compensate
```

### Model Loading Fails
```bash
# Clear HuggingFace cache
rm -rf ~/.cache/huggingface/hub
```

### Port Already in Use
```bash
# Find and kill process
lsof -i :7860
kill -9 <PID>
```
