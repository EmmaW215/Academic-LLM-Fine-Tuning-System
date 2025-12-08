# 🚀 Vercel 部署指南

本指南将帮助您将 Academic LLM 前端部署到 Vercel。

## 📋 前置要求

1. ✅ GitHub 账户
2. ✅ Vercel 账户（免费注册：https://vercel.com）
3. ✅ 后端 API 已运行并可访问（GPU 服务器上的 FastAPI）

## 🎯 步骤 1: 准备代码

### 1.1 确保前端代码已提交到 GitHub

```bash
cd /home/jovyan/work/frontend
git add .
git commit -m "Add Next.js frontend"
git push origin main
```

或者，如果前端代码在项目根目录：

```bash
cd /home/jovyan/work
git add frontend/
git commit -m "Add Next.js frontend"
git push origin main
```

## 🎯 步骤 2: 在 Vercel 创建项目

### 2.1 登录 Vercel

1. 访问 https://vercel.com
2. 点击 "Sign Up" 或 "Log In"
3. 使用 GitHub 账户登录（推荐）

### 2.2 导入项目

1. 点击 "Add New..." → "Project"
2. 选择您的 GitHub 仓库：`EmmaW215/Academic-LLM-Fine-Tuning-System`
3. 点击 "Import"

### 2.3 配置项目

在项目设置页面：

1. **Root Directory**: 设置为 `frontend`
   - 点击 "Edit" 按钮
   - 输入 `frontend`
   - 点击 "Continue"

2. **Framework Preset**: 选择 "Next.js"（应该自动检测）

3. **Build Command**: `npm run build`（默认）

4. **Output Directory**: `.next`（默认）

5. **Install Command**: `npm install`（默认）

## 🎯 步骤 3: 配置环境变量

在 Vercel 项目设置中添加环境变量：

1. 在项目设置页面，点击 "Environment Variables"
2. 添加以下变量：

```
NEXT_PUBLIC_API_URL = https://your-gpu-server.com
```

**重要提示：**
- 如果您的 GPU 服务器没有 HTTPS，您需要：
  - 使用 Cloudflare Tunnel（免费）
  - 或使用 ngrok（开发测试）
  - 或配置 nginx + Let's Encrypt SSL

### 3.1 使用 Cloudflare Tunnel（推荐，免费）

在 GPU 服务器上：

```bash
# 安装 cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# 运行 tunnel
cloudflared tunnel --url http://localhost:8000
```

这会生成一个 HTTPS URL，例如：`https://random-name.trycloudflare.com`

在 Vercel 环境变量中使用这个 URL。

## 🎯 步骤 4: 部署

1. 点击 "Deploy" 按钮
2. 等待构建完成（通常 1-3 分钟）
3. 部署成功后，您会看到一个 URL，例如：`https://academic-llm-frontend.vercel.app`

## 🎯 步骤 5: 配置后端 CORS

确保后端允许 Vercel 域名访问：

在 `module8-api.py` 中，更新 CORS 配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "https://*.vercel.app",  # 允许所有 Vercel 子域名
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

然后重启后端服务。

## 🎯 步骤 6: 测试部署

1. 访问您的 Vercel URL
2. 检查 "System Status" 卡片是否显示 "Healthy"
3. 测试 Chat 功能
4. 测试 Search 功能

## 🔧 故障排除

### 问题 1: 构建失败

**检查：**
- Root Directory 是否正确设置为 `frontend`
- package.json 是否存在
- 所有依赖是否已安装

**解决：**
- 查看 Vercel 构建日志
- 确保 `frontend/package.json` 存在且有效

### 问题 2: API 连接失败

**检查：**
- 环境变量 `NEXT_PUBLIC_API_URL` 是否正确设置
- 后端服务是否正在运行
- CORS 配置是否正确

**解决：**
- 在 Vercel 项目设置中检查环境变量
- 测试后端 API：`curl https://your-api-url/health`
- 检查浏览器控制台的错误信息

### 问题 3: CORS 错误

**错误信息：**
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```

**解决：**
- 更新后端 CORS 配置，添加 Vercel 域名
- 重启后端服务

## 📝 更新部署

每次您推送代码到 GitHub，Vercel 会自动重新部署：

```bash
git add .
git commit -m "Update frontend"
git push origin main
```

Vercel 会自动检测更改并重新部署。

## 🔒 生产环境建议

1. **添加 API Key 认证**（可选但推荐）
   - 在后端添加 API Key 验证
   - 在前端环境变量中添加 `NEXT_PUBLIC_API_KEY`
   - 在 API 请求中发送 API Key

2. **使用自定义域名**
   - 在 Vercel 项目设置中添加自定义域名
   - 配置 DNS 记录

3. **启用 HTTPS**
   - 确保后端使用 HTTPS（使用 Cloudflare Tunnel 或 SSL 证书）

## 📚 更多资源

- [Vercel 文档](https://vercel.com/docs)
- [Next.js 部署](https://nextjs.org/docs/deployment)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

## ✅ 检查清单

部署前确认：
- [ ] 代码已推送到 GitHub
- [ ] Vercel 项目已创建
- [ ] Root Directory 设置为 `frontend`
- [ ] 环境变量 `NEXT_PUBLIC_API_URL` 已设置
- [ ] 后端 API 可访问
- [ ] 后端 CORS 配置正确
- [ ] 构建成功
- [ ] 前端可以连接到后端

完成以上步骤后，您的前端应该已经成功部署到 Vercel！🎉

