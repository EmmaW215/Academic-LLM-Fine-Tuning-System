# 🔧 Vercel 环境变量配置详细指南

## 📋 步骤 1: 获取后端 API 的 HTTPS URL

### 方法 A: 使用自动脚本（推荐）

```bash
cd /home/jovyan/work
./setup_https_tunnel.sh
```

脚本会自动：
1. 检查后端 API 是否运行
2. 安装 cloudflared（如果未安装）
3. 启动 HTTPS tunnel
4. 显示您的 HTTPS URL

### 方法 B: 手动设置 Cloudflare Tunnel

```bash
# 1. 确保后端 API 正在运行
cd /home/jovyan/work
python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000

# 2. 在另一个终端，安装 cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared
chmod +x /tmp/cloudflared
sudo mv /tmp/cloudflared /usr/local/bin/cloudflared

# 3. 启动 tunnel
cloudflared tunnel --url http://localhost:8000

# 4. 会显示类似这样的 URL:
# https://xxxxx.trycloudflare.com
```

### 方法 C: 使用 ngrok

```bash
# 1. 安装 ngrok（如果未安装）
# 访问: https://ngrok.com/download

# 2. 启动 ngrok
ngrok http 8000

# 3. 会显示 HTTPS URL
```

## 📋 步骤 2: 在 Vercel 配置环境变量

### 详细步骤（带截图说明）

#### 步骤 1: 访问 Vercel 项目

1. 打开浏览器
2. 访问：https://vercel.com/emma-wangs-projects/academic-llm-fine-tuning-system
3. 如果未登录，先登录您的 Vercel 账户

#### 步骤 2: 进入设置页面

1. 在项目页面，点击顶部的 **"Settings"** 标签
   - 位置：在 "Overview", "Deployments", "Analytics" 等标签旁边

#### 步骤 3: 找到环境变量部分

1. 在左侧菜单中，找到 **"Environment Variables"**
   - 位置：在 Settings 下的子菜单中
   - 或者在页面中滚动找到 "Environment Variables" 部分

#### 步骤 4: 添加新环境变量

1. 点击 **"Add New"** 或 **"Add"** 按钮
   - 通常在环境变量列表的顶部或右侧

2. 填写环境变量信息：
   ```
   Key（键）: NEXT_PUBLIC_API_URL
   Value（值）: https://xxxxx.trycloudflare.com
   ```
   - 将 `https://xxxxx.trycloudflare.com` 替换为您在步骤 1 中获取的实际 URL

3. 选择环境：
   - ✅ Production（生产环境）
   - ✅ Preview（预览环境）
   - ✅ Development（开发环境）
   - 建议全选，这样所有环境都能使用

4. 点击 **"Save"** 或 **"Add"** 按钮

#### 步骤 5: 验证环境变量

1. 确认环境变量已添加：
   - 在环境变量列表中应该能看到 `NEXT_PUBLIC_API_URL`
   - 值应该是您的 HTTPS URL

2. 注意：环境变量的值在保存后会被隐藏（显示为 `••••••`），这是正常的安全措施

## 📋 步骤 3: 触发重新部署

### 方法 A: 手动重新部署（推荐）

1. 在 Vercel 项目页面
2. 点击 **"Deployments"** 标签
3. 找到最新的部署（或任意部署）
4. 点击部署右侧的 **"..."** 菜单（三个点）
5. 选择 **"Redeploy"**
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

## ✅ 验证配置

### 1. 检查后端 API 可访问性

```bash
# 使用您获取的 HTTPS URL
curl https://your-url.trycloudflare.com/health

# 应该返回:
# {"status":"healthy","initialized":true,"index_loaded":true}
```

### 2. 检查 Vercel 部署

1. 在 Vercel "Deployments" 页面
2. 查看最新部署状态
3. 应该显示 "Ready"（绿色）

### 3. 测试前端应用

1. 访问您的 Vercel 部署 URL
2. 打开浏览器开发者工具（F12）
3. 查看 "Console" 标签
4. 检查是否有 API 连接错误

4. 在应用中：
   - 查看 "System Status" 卡片
   - 应该显示 "API Status: Healthy"
   - 测试各个功能

## 🔧 故障排除

### 问题 1: 环境变量未生效

**解决：**
- 确保已重新部署（环境变量更改需要重新部署才能生效）
- 检查环境变量名称是否正确：`NEXT_PUBLIC_API_URL`（注意大小写）
- 确保选择了正确的环境（Production/Preview/Development）

### 问题 2: API 连接失败

**检查：**
1. 后端 API 是否正在运行
2. HTTPS URL 是否正确
3. 测试 URL：`curl https://your-url/health`

**解决：**
- 确保 tunnel 正在运行
- 检查防火墙设置
- 重新启动 tunnel

### 问题 3: Vercel 构建失败

**检查：**
- 查看构建日志中的错误
- 确保 Root Directory 设置为 `frontend`

## 📝 快速参考

### 环境变量配置摘要

```
Key: NEXT_PUBLIC_API_URL
Value: https://your-cloudflare-url.trycloudflare.com
环境: Production, Preview, Development（全选）
```

### 常用命令

```bash
# 启动后端 API
cd /home/jovyan/work
python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000

# 启动 HTTPS tunnel
cloudflared tunnel --url http://localhost:8000

# 查看 tunnel 日志
tail -f /tmp/cloudflare.log

# 测试 API
curl https://your-url.trycloudflare.com/health
```

## 🎉 完成！

完成以上步骤后：
- ✅ 后端 API 有 HTTPS URL
- ✅ Vercel 环境变量已配置
- ✅ 前端可以访问后端 API
- ✅ 所有功能正常工作

