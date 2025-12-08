# 如何重启 Gradio UI - 逐步指南

## 方法 1：使用终端命令（推荐）

### 步骤 1：停止当前运行的 Gradio UI

在终端中运行以下命令：

```bash
pkill -f "gradio-ui.py"
```

或者更强制的方式：

```bash
pkill -9 -f "gradio-ui.py"
```

**验证是否已停止：**
```bash
ps aux | grep "gradio-ui.py" | grep -v grep
```
如果没有输出，说明已成功停止。

### 步骤 2：等待几秒

```bash
sleep 3
```

### 步骤 3：重新启动 Gradio UI

```bash
cd /home/jovyan/work
GRADIO_SERVER_PORT=7861 python gradio-ui.py
```

**或者让它在后台运行：**
```bash
cd /home/jovyan/work
nohup GRADIO_SERVER_PORT=7861 python gradio-ui.py > gradio.log 2>&1 &
```

### 步骤 4：验证是否成功启动

等待 5-10 秒后，运行：

```bash
curl -s http://localhost:7861 -o /dev/null -w "HTTP状态码: %{http_code}\n"
```

如果返回 `200`，说明启动成功。

---

## 方法 2：在 JupyterLab 中操作

### 步骤 1：打开终端

在 JupyterLab 中，点击菜单栏的 **File** → **New** → **Terminal**

### 步骤 2：停止 Gradio

在终端中输入：
```bash
pkill -f "gradio-ui.py"
```

### 步骤 3：启动 Gradio

```bash
cd /home/jovyan/work
GRADIO_SERVER_PORT=7861 python gradio-ui.py &
```

注意：末尾的 `&` 让它在后台运行。

### 步骤 4：检查状态

```bash
ps aux | grep "gradio-ui.py" | grep -v grep
```

---

## 方法 3：一键重启脚本

创建一个重启脚本：

```bash
cat > /home/jovyan/work/restart_gradio.sh << 'EOF'
#!/bin/bash
echo "正在停止 Gradio UI..."
pkill -9 -f "gradio-ui.py"
sleep 2
echo "正在启动 Gradio UI..."
cd /home/jovyan/work
GRADIO_SERVER_PORT=7861 python gradio-ui.py > gradio.log 2>&1 &
sleep 5
if curl -s http://localhost:7861 > /dev/null; then
    echo "✅ Gradio UI 已成功启动（端口 7861）"
else
    echo "⚠️  Gradio UI 可能还在启动中，请稍候..."
fi
EOF

chmod +x /home/jovyan/work/restart_gradio.sh
```

然后每次只需要运行：
```bash
/home/jovyan/work/restart_gradio.sh
```

---

## 访问 Gradio UI

启动成功后，在浏览器中访问：

**JupyterLab 代理方式：**
```
https://your-jupyter-url/proxy/7861/
```

**或者直接访问（如果允许）：**
```
http://localhost:7861
```

---

## 常见问题

### Q: 如何查看 Gradio 日志？

```bash
tail -f /home/jovyan/work/gradio.log
```

### Q: 如何检查端口是否被占用？

```bash
lsof -i :7861
```

### Q: 如何强制停止所有 Python 进程？

```bash
pkill -9 python
```
⚠️ 注意：这会停止所有 Python 进程，请谨慎使用。

### Q: 如何查看 Gradio 是否正在运行？

```bash
ps aux | grep gradio-ui.py | grep -v grep
```

---

## 快速参考

| 操作 | 命令 |
|------|------|
| 停止 Gradio | `pkill -f "gradio-ui.py"` |
| 启动 Gradio | `cd /home/jovyan/work && GRADIO_SERVER_PORT=7861 python gradio-ui.py &` |
| 检查状态 | `curl -s http://localhost:7861 -o /dev/null -w "%{http_code}\n"` |
| 查看进程 | `ps aux | grep gradio-ui.py` |
| 查看日志 | `tail -f gradio.log` |

