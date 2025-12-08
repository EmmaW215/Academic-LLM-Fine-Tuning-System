#!/bin/bash
echo "=========================================="
echo "重启 Gradio UI"
echo "=========================================="
echo ""
echo "步骤 1: 正在停止当前运行的 Gradio UI..."
pkill -9 -f "gradio-ui.py" 2>/dev/null
sleep 2

echo "步骤 2: 检查是否已停止..."
if ps aux | grep "gradio-ui.py" | grep -v grep > /dev/null; then
    echo "⚠️  仍有进程在运行，强制停止..."
    pkill -9 -f "gradio-ui.py"
    sleep 2
else
    echo "✅ 已成功停止"
fi

echo ""
echo "步骤 3: 正在启动 Gradio UI（端口 7861）..."
cd /home/jovyan/work
nohup GRADIO_SERVER_PORT=7861 python gradio-ui.py > gradio.log 2>&1 &

echo "步骤 4: 等待服务启动..."
sleep 8

echo ""
echo "步骤 5: 验证启动状态..."
if curl -s http://localhost:7861 > /dev/null 2>&1; then
    echo "✅ Gradio UI 已成功启动！"
    echo ""
    echo "访问地址:"
    echo "  - JupyterLab 代理: /proxy/7861/"
    echo "  - 本地访问: http://localhost:7861"
    echo ""
    echo "查看日志: tail -f /home/jovyan/work/gradio.log"
else
    echo "⚠️  Gradio UI 可能还在启动中，请稍候..."
    echo "   您可以运行以下命令检查:"
    echo "   curl -s http://localhost:7861 -o /dev/null -w '%{http_code}\n'"
    echo "   或查看日志: tail -f /home/jovyan/work/gradio.log"
fi
echo ""
echo "=========================================="
