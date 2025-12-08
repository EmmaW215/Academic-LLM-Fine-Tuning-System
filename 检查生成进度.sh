#!/bin/bash
echo "检查 Synthetic Data Generation 进度..."
echo ""

FILE="/home/jovyan/work/storage/data/synthetic/synthetic_qa.jsonl"
if [ -f "$FILE" ]; then
    CURRENT=$(wc -l < "$FILE")
    SIZE=$(du -h "$FILE" | cut -f1)
    echo "当前状态:"
    echo "  - 记录数: $CURRENT 条"
    echo "  - 文件大小: $SIZE"
    echo ""
    
    # 等待30秒后再次检查
    echo "等待 30 秒后再次检查..."
    sleep 30
    NEW=$(wc -l < "$FILE")
    
    if [ "$NEW" -gt "$CURRENT" ]; then
        echo "✅ 进度正常！新增了 $((NEW - CURRENT)) 条记录"
    else
        echo "⚠️  进度可能已停止（30秒内无新增）"
        echo "   建议："
        echo "   1. 检查浏览器控制台是否有错误"
        echo "   2. 刷新页面重试"
        echo "   3. 或减少论文数量（如 3-5 篇）"
    fi
else
    echo "文件不存在"
fi
