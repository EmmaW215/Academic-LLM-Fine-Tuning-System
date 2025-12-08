#!/bin/bash
# 创建代码压缩包，排除大文件和敏感信息

ARCHIVE_NAME="Academic-LLM-Fine-Tuning-System-$(date +%Y%m%d-%H%M%S).tar.gz"
EXCLUDE_PATTERNS=(
    "storage/models/**"
    "storage/data/raw/*.pdf"
    "storage/data/processed/*.json"
    "storage/data/synthetic/*.jsonl"
    "storage/indexes/faiss/*.faiss"
    "storage/indexes/faiss/*.pkl"
    "storage/indexes/sqlite/*.db"
    ".env"
    ".env.local"
    "__pycache__"
    "*.pyc"
    ".ipynb_checkpoints"
    ".gradio"
    "*.log"
    ".venv"
    "venv"
    ".git"
    "*.tmp"
    "*.bak"
    ".DS_Store"
)

echo "Creating archive: $ARCHIVE_NAME"
echo "Excluding large files and sensitive data..."

# 使用 tar 创建压缩包，排除指定模式
tar --exclude='storage/models' \
    --exclude='storage/data/raw/*.pdf' \
    --exclude='storage/data/processed/*.json' \
    --exclude='storage/data/synthetic/*.jsonl' \
    --exclude='storage/indexes/faiss/*.faiss' \
    --exclude='storage/indexes/faiss/*.pkl' \
    --exclude='storage/indexes/sqlite/*.db' \
    --exclude='.env' \
    --exclude='.env.local' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.ipynb_checkpoints' \
    --exclude='.gradio' \
    --exclude='*.log' \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='.git' \
    --exclude='*.tmp' \
    --exclude='*.bak' \
    --exclude='.DS_Store' \
    -czf "$ARCHIVE_NAME" \
    --exclude="$ARCHIVE_NAME" \
    .

if [ $? -eq 0 ]; then
    SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)
    echo ""
    echo "✅ Archive created successfully!"
    echo "   File: $ARCHIVE_NAME"
    echo "   Size: $SIZE"
    echo ""
    echo "📦 Contents included:"
    echo "   ✅ All source code"
    echo "   ✅ Configuration files"
    echo "   ✅ Documentation"
    echo "   ✅ Requirements"
    echo ""
    echo "🚫 Excluded:"
    echo "   ❌ Model files (storage/models)"
    echo "   ❌ Data files (storage/data)"
    echo "   ❌ Index files (storage/indexes)"
    echo "   ❌ .env files (sensitive)"
    echo "   ❌ Cache and temporary files"
else
    echo "❌ Failed to create archive"
    exit 1
fi
