#!/bin/bash
# 设置 HTTPS Tunnel 的脚本

echo "=========================================="
echo "设置 HTTPS Tunnel 获取后端 API URL"
echo "=========================================="
echo ""

# 检查后端 API 是否运行
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  后端 API 未运行，正在启动..."
    echo ""
    echo "请在另一个终端运行："
    echo "  cd /home/jovyan/work"
    echo "  python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000"
    echo ""
    echo "或者后台运行："
    echo "  nohup python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &"
    echo ""
    read -p "后端 API 已启动？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "请先启动后端 API，然后重新运行此脚本"
        exit 1
    fi
fi

# 检查 cloudflared
if command -v cloudflared &> /dev/null; then
    echo "✅ cloudflared 已安装"
    METHOD="cloudflared"
elif command -v ngrok &> /dev/null; then
    echo "✅ ngrok 已安装"
    METHOD="ngrok"
else
    echo "❌ 未找到 cloudflared 或 ngrok"
    echo ""
    echo "正在安装 cloudflared（推荐，免费）..."
    
    # 下载 cloudflared
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        ARCH="amd64"
    elif [ "$ARCH" = "aarch64" ]; then
        ARCH="arm64"
    else
        ARCH="amd64"
    fi
    
    DOWNLOAD_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH}"
    
    echo "下载 cloudflared..."
    curl -L "$DOWNLOAD_URL" -o /tmp/cloudflared
    chmod +x /tmp/cloudflared
    sudo mv /tmp/cloudflared /usr/local/bin/cloudflared 2>/dev/null || mv /tmp/cloudflared ~/.local/bin/cloudflared
    
    if command -v cloudflared &> /dev/null; then
        echo "✅ cloudflared 安装成功"
        METHOD="cloudflared"
    else
        echo "❌ 安装失败，请手动安装"
        echo "运行: curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared"
        echo "然后: chmod +x /usr/local/bin/cloudflared"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "启动 HTTPS Tunnel..."
echo "=========================================="
echo ""

if [ "$METHOD" = "cloudflared" ]; then
    echo "使用 Cloudflare Tunnel..."
    echo ""
    echo "正在启动 tunnel（后台运行）..."
    nohup cloudflared tunnel --url http://localhost:8000 > /tmp/cloudflare.log 2>&1 &
    TUNNEL_PID=$!
    
    echo "等待 tunnel 启动..."
    sleep 5
    
    # 从日志中提取 URL
    if [ -f /tmp/cloudflare.log ]; then
        URL=$(grep -o 'https://[^ ]*\.trycloudflare\.com' /tmp/cloudflare.log | head -1)
        if [ -n "$URL" ]; then
            echo ""
            echo "=========================================="
            echo "✅ HTTPS URL 已获取！"
            echo "=========================================="
            echo ""
            echo "您的后端 API HTTPS URL:"
            echo "  $URL"
            echo ""
            echo "测试连接:"
            echo "  curl $URL/health"
            echo ""
            echo "=========================================="
            echo "下一步：在 Vercel 配置环境变量"
            echo "=========================================="
            echo ""
            echo "1. 访问: https://vercel.com/emma-wangs-projects/academic-llm-fine-tuning-system"
            echo "2. 点击 'Settings' 标签"
            echo "3. 找到 'Environment Variables' 部分"
            echo "4. 点击 'Add New'"
            echo "5. 输入:"
            echo "   Key: NEXT_PUBLIC_API_URL"
            echo "   Value: $URL"
            echo "6. 选择所有环境（Production, Preview, Development）"
            echo "7. 点击 'Save'"
            echo ""
            echo "Tunnel 进程 ID: $TUNNEL_PID"
            echo "日志文件: /tmp/cloudflare.log"
            echo "停止 tunnel: kill $TUNNEL_PID"
            echo ""
        else
            echo "⚠️  无法从日志中提取 URL，请查看日志："
            echo "  tail -f /tmp/cloudflare.log"
        fi
    fi
elif [ "$METHOD" = "ngrok" ]; then
    echo "使用 ngrok..."
    echo ""
    echo "启动 ngrok（前台运行，按 Ctrl+C 停止）..."
    echo ""
    ngrok http 8000
fi
