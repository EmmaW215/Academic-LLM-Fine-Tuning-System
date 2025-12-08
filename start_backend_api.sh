#!/bin/bash
# 启动后端 API 服务器

cd /home/jovyan/work

# 检查 uvicorn 是否可用
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "安装 uvicorn..."
    pip install uvicorn fastapi
fi

# 启动 API 服务器
echo "启动后端 API 服务器..."
echo "访问地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000

