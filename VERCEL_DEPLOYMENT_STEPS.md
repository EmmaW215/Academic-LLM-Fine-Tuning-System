# 🚀 Vercel 部署步骤指南

## 📋 快速步骤概览

1. ✅ **准备代码** - 前端代码已创建在 `frontend/` 目录
2. 📤 **推送到 GitHub** - 将代码推送到您的仓库
3. 🌐 **在 Vercel 部署** - 连接 GitHub 并部署
4. ⚙️ **配置环境变量** - 设置后端 API URL
5. ✅ **测试部署** - 验证一切正常工作

---

## 🎯 步骤 1: 推送到 GitHub

```bash
cd /home/jovyan/work

# 添加前端文件
git add frontend/

# 提交
git commit -m "Add Next.js frontend for Vercel deployment"

# 推送到 GitHub（需要先设置认证）
git push origin main
```

**如果还没有推送过，请参考 `PUSH_TO_GITHUB.md` 设置 GitHub 认证。**

---

## 🎯 步骤 2: 在 Vercel 创建账户和项目

### 2.1 注册/登录 Vercel

1. 访问 https://vercel.com
2. 点击 "Sign Up" 或 "Log In"
3. **推荐使用 GitHub 账户登录**（最简单）

### 2.2 导入项目

1. 登录后，点击 **"Add New..."** → **"Project"**
2. 在 "Import Git Repository" 中：
   - 选择您的仓库：`EmmaW215/Academic-LLM-Fine-Tuning-System`
   - 点击 **"Import"**

### 2.3 配置项目设置

在项目配置页面：

#### 重要设置：

1. **Root Directory** ⚠️ **必须设置！**
   - 点击 "Edit" 按钮（在 Framework Preset 旁边）
   - 输入：`frontend`
   - 点击 "Continue"

2. **Framework Preset**
   - 应该自动检测为 "Next.js"
   - 如果没有，手动选择 "Next.js"

3. **Build Command**
   - 默认：`npm run build` ✅

4. **Output Directory**
   - 默认：`.next` ✅

5. **Install Command**
   - 默认：`npm install` ✅

---

## 🎯 步骤 3: 配置环境变量

### 3.1 获取后端 API URL

您需要确保后端 API 可以通过 HTTPS 访问。有几个选项：

#### 选项 A: 使用 Cloudflare Tunnel（推荐，免费）

在 GPU 服务器上运行：

```bash
# 安装 cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# 运行 tunnel（在后台）
nohup cloudflared tunnel --url http://localhost:8000 > /tmp/cloudflare.log 2>&1 &

# 查看生成的 URL
tail -f /tmp/cloudflare.log
# 会显示类似: https://random-name.trycloudflare.com
```

#### 选项 B: 使用 ngrok（开发测试）

```bash
# 安装 ngrok
# 然后运行
ngrok http 8000
# 会显示 HTTPS URL
```

#### 选项 C: 配置 SSL（生产环境）

使用 nginx + Let's Encrypt 配置 HTTPS。

### 3.2 在 Vercel 添加环境变量

1. 在项目设置页面，找到 **"Environment Variables"** 部分
2. 点击 **"Add"** 按钮
3. 添加以下变量：

   **Key:** `NEXT_PUBLIC_API_URL`
   
   **Value:** 您的后端 API URL（例如：`https://your-tunnel.trycloudflare.com`）

4. 选择环境：**Production, Preview, Development**（全选）
5. 点击 **"Save"**

---

## 🎯 步骤 4: 部署

1. 点击页面底部的 **"Deploy"** 按钮
2. 等待构建完成（通常 1-3 分钟）
3. 构建成功后，您会看到一个 URL，例如：
   ```
   https://academic-llm-fine-tuning-system.vercel.app
   ```

---

## 🎯 步骤 5: 配置后端 CORS

确保后端允许 Vercel 域名访问。

### 5.1 更新后端 CORS 配置

编辑 `module8-api.py`，找到 CORS 配置部分（大约第 184 行）：

```python
# 更新为：
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app-name.vercel.app",  # 您的 Vercel URL
        "https://*.vercel.app",  # 允许所有 Vercel 子域名
        "http://localhost:3000",  # 本地开发
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5.2 重启后端服务

```bash
# 在 GPU 服务器上
pkill -f "uvicorn.*module8-api"
cd /home/jovyan/work
uvicorn module8-api:app --host 0.0.0.0 --port 8000 &
```

---

## 🎯 步骤 6: 测试部署

1. **访问您的 Vercel URL**
   - 例如：`https://academic-llm-fine-tuning-system.vercel.app`

2. **检查系统状态**
   - 页面顶部的 "System Status" 卡片应该显示：
     - ✅ API Status: Healthy
     - ✅ Initialized: Yes
     - ✅ Index Loaded: Yes

3. **测试功能**
   - 切换到 "💬 Chat & Compare" 标签
   - 输入一个问题，测试聊天功能
   - 切换到 "🔍 RAG Search" 标签
   - 输入搜索查询，测试搜索功能

---

## 🔧 故障排除

### 问题 1: 构建失败

**症状：** Vercel 构建日志显示错误

**检查：**
- Root Directory 是否设置为 `frontend`
- `frontend/package.json` 是否存在
- 查看构建日志中的具体错误

**解决：**
- 确保 Root Directory = `frontend`
- 检查 `frontend/package.json` 语法是否正确

### 问题 2: API 连接失败

**症状：** 前端显示 "API Status: Unhealthy"

**检查：**
- 环境变量 `NEXT_PUBLIC_API_URL` 是否正确设置
- 后端服务是否正在运行
- 后端 URL 是否可以通过浏览器访问

**解决：**
```bash
# 测试后端 API
curl https://your-api-url/health

# 应该返回 JSON 响应
```

### 问题 3: CORS 错误

**症状：** 浏览器控制台显示 CORS 错误

**错误信息：**
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```

**解决：**
- 更新后端 CORS 配置（见步骤 5）
- 重启后端服务
- 清除浏览器缓存

### 问题 4: 环境变量未生效

**症状：** 前端仍在使用旧的 API URL

**解决：**
- 在 Vercel 项目设置中，重新部署项目
- 或者手动触发重新部署：
  - 项目页面 → "Deployments" → 点击最新部署 → "Redeploy"

---

## 📝 更新部署

每次您更新前端代码并推送到 GitHub，Vercel 会自动重新部署：

```bash
cd /home/jovyan/work/frontend
# 修改代码...
git add .
git commit -m "Update frontend"
git push origin main
```

Vercel 会自动检测到更改并重新部署。

---

## 🔒 生产环境建议

### 1. 添加 API Key 认证（可选但推荐）

**后端：**
```python
# 在 module8-api.py 中添加
API_KEY = os.getenv("API_KEY", "")

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path.startswith("/health"):
        return await call_next(request)
    
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        return JSONResponse({"detail": "Invalid API Key"}, status_code=401)
    
    return await call_next(request)
```

**前端：**
在 Vercel 环境变量中添加：
- `NEXT_PUBLIC_API_KEY` = your_secret_key

在 `lib/api.ts` 中添加到请求头：
```typescript
headers: {
  'Content-Type': 'application/json',
  'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || '',
}
```

### 2. 使用自定义域名

1. 在 Vercel 项目设置 → "Domains"
2. 添加您的域名
3. 按照说明配置 DNS 记录

### 3. 监控和日志

- Vercel 提供内置的分析和日志
- 在项目设置中查看 "Analytics" 和 "Logs"

---

## ✅ 部署检查清单

部署前确认：
- [ ] 代码已推送到 GitHub
- [ ] Vercel 账户已创建
- [ ] 项目已导入到 Vercel
- [ ] Root Directory 设置为 `frontend`
- [ ] 环境变量 `NEXT_PUBLIC_API_URL` 已设置
- [ ] 后端 API 可通过 HTTPS 访问
- [ ] 后端 CORS 配置已更新
- [ ] 构建成功
- [ ] 前端可以连接到后端
- [ ] 所有功能测试通过

---

## 📚 相关文档

- **详细部署指南：** `frontend/VERCEL_DEPLOYMENT.md`
- **前端 README：** `frontend/README.md`
- **Vercel 文档：** https://vercel.com/docs
- **Next.js 部署：** https://nextjs.org/docs/deployment

---

## 🎉 完成！

完成以上步骤后，您的前端应该已经成功部署到 Vercel！

**您的应用现在可以通过以下方式访问：**
- Vercel URL: `https://your-app.vercel.app`
- 自定义域名（如果配置了）

**下一步：**
- 分享您的应用 URL
- 监控使用情况
- 根据反馈进行改进

祝您部署顺利！🚀

