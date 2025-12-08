# 🔄 Vercel 重新连接和部署指南

## 📋 当前状态

- ✅ GitHub 代码已是最新
- ⚠️ 需要重新连接 Vercel 项目
- ⚠️ 需要重新部署

## 🎯 步骤 1: 重新连接 Vercel 项目

### 方法 A: 通过 Vercel 网站（推荐）

1. **访问 Vercel 项目**
   - 打开：https://vercel.com/emma-wangs-projects/academic-llm-fine-tuning-system
   - 或访问：https://vercel.com/dashboard

2. **检查项目设置**
   - 点击项目名称进入项目页面
   - 点击 "Settings" 标签
   - 检查 "Git Repository" 部分
   - 确保连接到：`EmmaW215/Academic-LLM-Fine-Tuning-System`

3. **如果未连接或需要重新连接**
   - 点击 "Connect Git Repository"
   - 选择 GitHub
   - 选择仓库：`Academic-LLM-Fine-Tuning-System`
   - 点击 "Import"

### 方法 B: 删除并重新创建项目

如果项目设置有问题，可以删除并重新创建：

1. **删除现有项目**
   - 在项目设置页面
   - 滚动到底部
   - 点击 "Delete Project"
   - 确认删除

2. **重新创建项目**
   - 点击 "Add New..." → "Project"
   - 选择仓库：`EmmaW215/Academic-LLM-Fine-Tuning-System`
   - 点击 "Import"

## 🎯 步骤 2: 配置项目设置

### 重要配置项

1. **Root Directory** ⚠️ **必须设置！**
   - 点击 "Edit" 按钮
   - 输入：`frontend`
   - 点击 "Continue"

2. **Framework Preset**
   - 应该自动检测为 "Next.js"
   - 如果没有，手动选择 "Next.js"

3. **Build Command**
   - 留空（让 Vercel 自动检测）
   - 或使用：`npm run build`

4. **Output Directory**
   - 留空（Next.js 默认）
   - 或使用：`.next`

5. **Install Command**
   - 留空（让 Vercel 自动检测）
   - 或使用：`npm install`

## 🎯 步骤 3: 配置环境变量

1. **在项目设置中，找到 "Environment Variables"**

2. **添加环境变量：**
   ```
   Key: NEXT_PUBLIC_API_URL
   Value: https://your-backend-api-url.com
   ```
   
   **获取后端 API URL 的方法：**
   
   **选项 1: 使用 Cloudflare Tunnel（推荐，免费）**
   ```bash
   # 在 GPU 服务器上安装 cloudflared
   curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
   chmod +x /usr/local/bin/cloudflared
   
   # 运行 tunnel（在后台）
   nohup cloudflared tunnel --url http://localhost:8000 > /tmp/cloudflare.log 2>&1 &
   
   # 查看生成的 URL
   tail -f /tmp/cloudflare.log
   # 会显示类似: https://random-name.trycloudflare.com
   ```
   
   **选项 2: 使用 ngrok（开发测试）**
   ```bash
   ngrok http 8000
   # 会显示 HTTPS URL
   ```

3. **选择环境：** Production, Preview, Development（全选）

4. **点击 "Save"**

## 🎯 步骤 4: 触发重新部署

### 方法 A: 手动触发

1. 在 Vercel 项目页面
2. 点击 "Deployments" 标签
3. 找到最新的部署
4. 点击右侧的 "..." 菜单
5. 选择 "Redeploy"

### 方法 B: 通过 Git 推送触发

```bash
cd /home/jovyan/work

# 创建一个小的更改来触发部署
echo "# Trigger redeploy" >> frontend/.vercel-trigger
git add frontend/.vercel-trigger
git commit -m "Trigger Vercel redeploy"
git push origin main
```

### 方法 C: 使用 Vercel CLI

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录
vercel login

# 链接项目
cd frontend
vercel link

# 部署
vercel --prod
```

## 🎯 步骤 5: 启动后端 API

在 GPU 服务器上启动后端 API：

```bash
cd /home/jovyan/work

# 方法 1: 使用启动脚本（推荐）
./start_backend_api.sh

# 方法 2: 直接运行
python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000

# 方法 3: 后台运行
nohup python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
```

## 🔍 验证部署

1. **检查 Vercel 部署状态**
   - 访问：https://vercel.com/emma-wangs-projects/academic-llm-fine-tuning-system
   - 查看 "Deployments" 标签
   - 确保最新部署状态为 "Ready"（绿色）

2. **访问部署的网站**
   - 点击部署的 URL
   - 或使用项目域名

3. **测试功能**
   - 检查 "System Status" 卡片
   - 测试各个标签页的功能
   - 查看浏览器控制台是否有错误

## 🔧 故障排除

### 问题 1: 构建失败

**检查：**
- Root Directory 是否正确设置为 `frontend`
- 查看构建日志中的错误信息

**解决：**
- 确保 `frontend/package.json` 存在
- 检查 `frontend/next.config.js` 配置

### 问题 2: API 连接失败

**检查：**
- 环境变量 `NEXT_PUBLIC_API_URL` 是否正确设置
- 后端 API 是否正在运行
- 后端 URL 是否可以通过浏览器访问

**解决：**
```bash
# 测试后端 API
curl https://your-api-url/health

# 应该返回 JSON 响应
```

### 问题 3: 项目未连接到 GitHub

**解决：**
1. 在 Vercel 项目设置中
2. 点击 "Connect Git Repository"
3. 重新连接 GitHub 仓库

## 📝 快速检查清单

- [ ] Vercel 项目已连接到 GitHub 仓库
- [ ] Root Directory 设置为 `frontend`
- [ ] 环境变量 `NEXT_PUBLIC_API_URL` 已设置
- [ ] 后端 API 正在运行
- [ ] 后端 API 可以通过 HTTPS 访问
- [ ] 最新部署状态为 "Ready"
- [ ] 前端可以访问并显示正常

## 🎉 完成！

完成以上步骤后，您的前端应该已经成功部署到 Vercel！

**访问您的应用：**
- Vercel URL: https://academic-llm-fine-tuning-system.vercel.app（或您的自定义域名）

