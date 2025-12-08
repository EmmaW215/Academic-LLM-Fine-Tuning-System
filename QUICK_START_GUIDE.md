# 🚀 快速启动指南

## 📋 当前状态

- ✅ GitHub 代码已是最新
- ⚠️ 后端 API 需要启动
- ⚠️ Vercel 项目需要重新连接

## 🎯 步骤 1: 启动后端 API

### 方法 A: 使用启动脚本（推荐）

```bash
cd /home/jovyan/work
./start_backend_api.sh
```

### 方法 B: 直接运行

```bash
cd /home/jovyan/work
python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000
```

### 方法 C: 后台运行

```bash
cd /home/jovyan/work
nohup python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
```

**验证后端运行：**
```bash
curl http://localhost:8000/health
# 应该返回: {"status":"healthy",...}
```

## 🎯 步骤 2: 获取后端 API 的 HTTPS URL

### 选项 1: Cloudflare Tunnel（推荐，免费）

```bash
# 安装
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# 运行（后台）
nohup cloudflared tunnel --url http://localhost:8000 > /tmp/cloudflare.log 2>&1 &

# 查看 URL
tail -f /tmp/cloudflare.log
# 会显示: https://xxxxx.trycloudflare.com
```

### 选项 2: ngrok（开发测试）

```bash
ngrok http 8000
# 会显示 HTTPS URL
```

## 🎯 步骤 3: 重新连接 Vercel 项目

### 访问 Vercel 项目

打开：https://vercel.com/emma-wangs-projects/academic-llm-fine-tuning-system

### 检查项目设置

1. **点击 "Settings" 标签**

2. **检查 "Git Repository"**
   - 应该显示：`EmmaW215/Academic-LLM-Fine-Tuning-System`
   - 如果未连接，点击 "Connect Git Repository"

3. **检查 "General" → "Root Directory"**
   - 必须设置为：`frontend`
   - 如果不对，点击 "Edit" 修改

### 配置环境变量

1. **在 Settings → Environment Variables**

2. **添加变量：**
   ```
   Key: NEXT_PUBLIC_API_URL
   Value: https://your-cloudflare-url.trycloudflare.com
   ```
   （使用步骤 2 中获取的 URL）

3. **选择环境：** Production, Preview, Development（全选）

4. **点击 "Save"**

## 🎯 步骤 4: 触发重新部署

### 方法 A: 手动触发（推荐）

1. 在 Vercel 项目页面
2. 点击 "Deployments" 标签
3. 找到最新的部署（或任意部署）
4. 点击右侧的 "..." 菜单
5. 选择 "Redeploy"
6. 确认重新部署

### 方法 B: 通过 Git 推送触发

```bash
cd /home/jovyan/work
# 创建一个小的更改
echo "" >> frontend/README.md
git add frontend/README.md
git commit -m "Trigger Vercel redeploy"
git push origin main
```

Vercel 会自动检测到更改并重新部署。

## ✅ 验证部署

1. **等待部署完成**
   - 在 Vercel "Deployments" 页面
   - 查看最新部署状态
   - 应该显示 "Ready"（绿色）

2. **访问部署的网站**
   - 点击部署的 URL
   - 或使用：https://academic-llm-fine-tuning-system.vercel.app

3. **测试功能**
   - 检查 "System Status" 卡片
   - 应该显示 "API Status: Healthy"
   - 测试各个功能标签页

## 🔧 故障排除

### 后端 API 无法启动

```bash
# 检查 uvicorn 是否安装
python3 -c "import uvicorn; print('OK')"

# 如果未安装
pip install uvicorn fastapi

# 检查端口是否被占用
lsof -i :8000
```

### Vercel 构建失败

1. 检查 Root Directory = `frontend`
2. 查看构建日志中的错误
3. 确保 `frontend/package.json` 存在

### API 连接失败

1. 检查环境变量 `NEXT_PUBLIC_API_URL` 是否正确
2. 测试后端 API：`curl https://your-api-url/health`
3. 检查后端 API 是否正在运行

## 📝 快速命令参考

```bash
# 启动后端 API
cd /home/jovyan/work
python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000

# 后台运行
nohup python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &

# 查看日志
tail -f /tmp/api.log

# 停止后端（如果在前台运行）
# 按 Ctrl+C

# 停止后台进程
pkill -f "uvicorn.*module8-api"
```

## 🎉 完成！

完成以上步骤后：
- ✅ 后端 API 在 GPU 服务器上运行
- ✅ Vercel 前端已部署
- ✅ 两者通过 HTTPS 连接
- ✅ 所有功能正常工作

