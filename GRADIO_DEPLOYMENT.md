# 🚀 Gradio UI 部署指南

Gradio UI 本身就是一个完整的前端应用，可以直接部署使用。

## 📋 部署选项

### 选项 1: 直接运行（最简单）

```bash
cd /home/jovyan/work
export GRADIO_SERVER_PORT=7861
python gradio-ui.py
```

然后通过端口转发访问：
- 在 Cursor/VS Code 中会自动转发端口
- 或手动 SSH 隧道：`ssh -L 7861:localhost:7861 ...`

### 选项 2: 使用 Gradio 的公共链接（临时）

在 `gradio-ui.py` 中，`launch()` 已经设置了 `share=True`，这会生成一个公共 URL：

```python
interface.launch(
    server_port=server_port,
    share=True  # 生成公共 URL
)
```

运行后会显示类似：
```
Running on public URL: https://xxxxx.gradio.live
```

**注意：** 这个 URL 是临时的，应用关闭后就会失效。

### 选项 3: 部署到 HuggingFace Spaces（推荐，免费）

1. **创建 HuggingFace Space**
   - 访问 https://huggingface.co/spaces
   - 点击 "Create new Space"
   - 选择 "Gradio" SDK
   - 设置 Space 名称

2. **上传代码**
   ```bash
   # 安装 HuggingFace Hub
   pip install huggingface_hub
   
   # 登录
   huggingface-cli login
   
   # 创建 Space
   huggingface-cli repo create academic-llm-ui --type space --space-sdk gradio
   
   # 上传文件（需要调整代码以适配 Spaces）
   ```

3. **配置 requirements.txt**
   - 在 Space 中添加所有依赖

**限制：** 需要将后端 API 也部署，或者使用 Spaces 的 GPU（需要付费）

### 选项 4: 部署到云服务器（生产环境）

#### 使用 systemd 服务

创建服务文件 `/etc/systemd/system/gradio-ui.service`:

```ini
[Unit]
Description=Academic LLM Gradio UI
After=network.target

[Service]
Type=simple
User=jovyan
WorkingDirectory=/home/jovyan/work
Environment="GRADIO_SERVER_PORT=7861"
ExecStart=/usr/bin/python3 /home/jovyan/work/gradio-ui.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable gradio-ui
sudo systemctl start gradio-ui
```

#### 使用 nginx 反向代理

配置 nginx 将请求转发到 Gradio：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:7861;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

然后配置 SSL（Let's Encrypt）：
```bash
sudo certbot --nginx -d your-domain.com
```

### 选项 5: 使用 Docker（容器化）

创建 `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements-file.txt .
RUN pip install -r requirements-file.txt

COPY . .

EXPOSE 7861

CMD ["python", "gradio-ui.py"]
```

构建和运行：
```bash
docker build -t academic-llm-ui .
docker run -p 7861:7861 -e GRADIO_SERVER_PORT=7861 academic-llm-ui
```

## 🔧 配置说明

### 当前配置

查看 `gradio-ui.py` 的启动配置：

```python
interface.launch(
    server_port=server_port,  # 从环境变量获取，默认 7861
    share=True,               # 生成公共 URL
    server_name="0.0.0.0"     # 监听所有接口
)
```

### 环境变量

- `GRADIO_SERVER_PORT`: 服务器端口（默认 7860）
- `OPENAI_API_KEY`: OpenAI API 密钥（用于合成数据生成）

## 📊 Gradio UI vs Next.js 前端

| 特性 | Gradio UI | Next.js 前端 |
|------|-----------|--------------|
| **部署平台** | Python 服务器、HF Spaces | Vercel、Netlify |
| **开发速度** | 快速（内置组件） | 需要开发 |
| **功能完整性** | 完整（所有功能） | 部分（Chat + Search） |
| **定制性** | 有限 | 完全可定制 |
| **用户体验** | 良好 | 优秀 |
| **适合场景** | 原型、演示、内部工具 | 生产环境、公开应用 |

## 💡 推荐方案

### 场景 1: 快速演示和内部使用
**使用 Gradio UI**
- 直接运行即可
- 功能完整
- 适合团队内部使用

### 场景 2: 公开部署和生产环境
**使用 Next.js 前端 + Vercel**
- 更好的用户体验
- 全球 CDN
- 专业外观

### 场景 3: 两者结合
- Gradio UI 用于内部管理和开发
- Next.js 前端用于公开访问
- 两者共享同一个后端 API

## 🚀 快速启动

最简单的启动方式：

```bash
cd /home/jovyan/work
export GRADIO_SERVER_PORT=7861
python gradio-ui.py
```

访问：
- 本地：http://localhost:7861
- 公共 URL：运行后会显示（如果 share=True）

## 📝 注意事项

1. **安全性**
   - 如果部署到公网，考虑添加认证
   - 不要暴露敏感信息

2. **性能**
   - Gradio UI 会加载模型到内存
   - 确保服务器有足够的 GPU/CPU 资源

3. **持久化**
   - 使用 `share=True` 的 URL 是临时的
   - 生产环境建议使用固定域名

## 🔗 相关文档

- [Gradio 文档](https://www.gradio.app/docs/)
- [Gradio 部署指南](https://www.gradio.app/guides/sharing-your-app)
- [HuggingFace Spaces](https://huggingface.co/docs/hub/spaces)

