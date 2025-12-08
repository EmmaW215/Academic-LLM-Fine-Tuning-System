#!/usr/bin/env bash
# 获取 HTTPS URL 的简化脚本

echo "=========================================="
echo "获取后端 API 的 HTTPS URL"
echo "=========================================="
echo ""

# 检查后端 API 是否运行
echo "检查后端 API..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端 API 正在运行"
else
    echo "⚠️  后端 API 未运行"
    echo ""
    echo "请先启动后端 API（在另一个终端）:"
    echo "  cd /home/jovyan/work"
    echo "  python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000"
    echo ""
    echo "或者后台运行:"
    echo "  nohup python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &"
    echo ""
    read -p "后端 API 已启动？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "请先启动后端 API，然后重新运行此脚本"
        exit 1
    fi
fi

echo ""
echo "检查 cloudflared..."

# 检查 cloudflared
if command -v cloudflared &> /dev/null; then
    echo "✅ cloudflared 已安装"
else
    echo "正在安装 cloudflared..."
    
    # 检测架构
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
    curl -L "$DOWNLOAD_URL" -o /tmp/cloudflared 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "❌ 下载失败，请手动安装"
        exit 1
    fi
    
    chmod +x /tmp/cloudflared
    
    # 尝试安装到系统路径
    if [ -w /usr/local/bin ]; then
        mv /tmp/cloudflared /usr/local/bin/cloudflared
    elif [ -w ~/.local/bin ]; then
        mkdir -p ~/.local/bin
        mv /tmp/cloudflared ~/.local/bin/cloudflared
        export PATH="$HOME/.local/bin:$PATH"
    else
        echo "⚠️  无法安装到系统路径，使用临时路径"
        export PATH="/tmp:$PATH"
    fi
    
    if command -v cloudflared &> /dev/null; then
        echo "✅ cloudflared 安装成功"
    else
        echo "❌ 安装失败"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "启动 HTTPS Tunnel..."
echo "=========================================="
echo ""

# 停止可能存在的旧进程
pkill -f "cloudflared tunnel" 2>/dev/null
sleep 1

# 启动 tunnel
echo "正在启动 tunnel（后台运行）..."
nohup cloudflared tunnel --url http://localhost:8000 > /tmp/cloudflare.log 2>&1 &
TUNNEL_PID=$!

echo "等待 tunnel 启动（5秒）..."
sleep 5

# 从日志中提取 URL
if [ -f /tmp/cloudflare.log ]; then
    URL=$(grep -o 'https://[^ ]*\.trycloudflare\.com' /tmp/cloudflare.log 2>/dev/null | head -1)
    
    if [ -z "$URL" ]; then
        # 尝试其他格式
        URL=$(grep -o 'https://[^ ]*trycloudflare[^ ]*' /tmp/cloudflare.log 2>/dev/null | head -1)
    fi
    
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
        echo "3. 找到 'Environment Variables'"
        echo "4. 点击 'Add New'"
        echo "5. 输入:"
        echo "   Key: NEXT_PUBLIC_API_URL"
        echo "   Value: $URL"
        echo "6. 选择所有环境（Production, Preview, Development）"
        echo "7. 点击 'Save'"
        echo ""
        echo "Tunnel 进程 ID: $TUNNEL_PID"
        echo "查看日志: tail -f /tmp/cloudflare.log"
        echo "停止 tunnel: kill $TUNNEL_PID"
        echo ""
    else
        echo "⚠️  无法从日志中提取 URL"
        echo ""
        echo "请查看日志:"
        echo "  tail -20 /tmp/cloudflare.log"
        echo ""
        echo "或者手动运行:"
        echo "  cloudflared tunnel --url http://localhost:8000"
        echo ""
    fi
else
    echo "❌ 日志文件不存在"
    echo "Tunnel 可能启动失败"
fi
