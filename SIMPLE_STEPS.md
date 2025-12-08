# 🚀 简单步骤指南

## 步骤 1: 启动后端 API

在终端运行：

```bash
cd /home/jovyan/work
nohup python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
```

等待 3-5 秒，然后验证：

```bash
curl http://localhost:8000/health
```

应该返回：`{"status":"healthy",...}`

## 步骤 2: 获取 HTTPS URL

运行脚本：

```bash
bash get_https_url.sh
```

脚本会自动：
- ✅ 检查后端 API
- ✅ 安装 cloudflared（如果需要）
- ✅ 启动 HTTPS tunnel
- ✅ 显示您的 HTTPS URL

**重要：** 复制显示的 URL（类似 `https://xxxxx.trycloudflare.com`）

## 步骤 3: 在 Vercel 配置环境变量

### 详细步骤：

1. **打开浏览器，访问：**
   ```
   https://vercel.com/emma-wangs-projects/academic-llm-fine-tuning-system
   ```

2. **点击 "Settings" 标签**
   - 在页面顶部导航栏

3. **在左侧菜单找到 "Environment Variables"**
   - 在 Settings 页面左侧

4. **点击 "Add New" 按钮**
   - 在环境变量列表上方

5. **填写环境变量：**
   - **Key（键）:** `NEXT_PUBLIC_API_URL`
   - **Value（值）:** 粘贴您在步骤 2 中获取的 URL
     - 例如：`https://xxxxx.trycloudflare.com`

6. **选择环境：**
   - ✅ Production
   - ✅ Preview
   - ✅ Development
   - （建议全选）

7. **点击 "Save" 按钮**

## 步骤 4: 重新部署

1. **点击 "Deployments" 标签**
   - 在页面顶部导航栏

2. **找到最新的部署**
   - 在部署列表中

3. **点击部署右侧的 "..." 菜单**
   - 三个点的图标

4. **选择 "Redeploy"**
   - 从下拉菜单中

5. **确认重新部署**
   - 等待部署完成（通常 1-2 分钟）

## ✅ 验证

部署完成后：

1. **访问您的 Vercel 网站**
   - 点击部署的 URL

2. **检查 "System Status" 卡片**
   - 应该显示 "API Status: Healthy"

3. **测试功能**
   - 尝试使用各个标签页的功能

## 🔧 如果遇到问题

### 后端 API 无法启动

```bash
# 检查是否已运行
ps aux | grep uvicorn

# 查看日志
tail -f /tmp/api.log

# 手动启动（前台，可以看到输出）
python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000
```

### 脚本无法运行

```bash
# 使用 bash 直接运行
bash get_https_url.sh

# 或者手动安装 cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /tmp/cloudflared
chmod +x /tmp/cloudflared
/tmp/cloudflared tunnel --url http://localhost:8000
```

### Vercel 环境变量未生效

- 确保已重新部署（环境变量更改需要重新部署）
- 检查环境变量名称：`NEXT_PUBLIC_API_URL`（注意大小写）
- 确保选择了正确的环境

## 📝 快速命令参考

```bash
# 启动后端 API（后台）
nohup python3 -m uvicorn module8-api:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &

# 获取 HTTPS URL
bash get_https_url.sh

# 查看后端日志
tail -f /tmp/api.log

# 查看 tunnel 日志
tail -f /tmp/cloudflare.log

# 停止后端 API
pkill -f "uvicorn.*module8-api"

# 停止 tunnel
pkill -f "cloudflared tunnel"
```

