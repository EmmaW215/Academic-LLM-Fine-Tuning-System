#!/bin/bash
# 创建只包含代码的压缩包（排除大数据文件）

echo "正在创建代码压缩包..."
cd /home/jovyan/work

tar -czf ../academic-llm-code.tar.gz \
    --exclude='storage/data/raw' \
    --exclude='storage/data/processed' \
    --exclude='storage/data/synthetic' \
    --exclude='storage/indexes' \
    --exclude='storage/models' \
    --exclude='__pycache__' \
    --exclude='.ipynb_checkpoints' \
    --exclude='.venv' \
    --exclude='.gradio' \
    --exclude='*.log' \
    --exclude='*.pyc' \
    config/ modules/ *.py *.md *.txt *.sh requirements-file.txt .gitignore

echo "✅ 压缩包已创建: /home/jovyan/academic-llm-code.tar.gz"
echo "   大小: $(du -h ../academic-llm-code.tar.gz | cut -f1)"
