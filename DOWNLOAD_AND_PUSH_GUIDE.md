# 如何下载项目到本地或推送到 GitHub

## 方法 1: 下载到本地

### 选项 A: 使用 JupyterLab 文件浏览器（最简单）

1. **在 JupyterLab 中**：
   - 左侧文件浏览器，右键点击 `/home/jovyan/work` 文件夹
   - 选择 **"Download"** 或 **"Download Folder"**
   - 浏览器会自动下载为 ZIP 文件

2. **注意事项**：
   - 项目大小约 213MB，包含数据文件
   - 如果只想下载代码，可以排除 `storage/` 目录

### 选项 B: 创建压缩包后下载

在终端中运行：

```bash
cd /home/jovyan/work

# 只压缩代码文件（排除大数据文件）
tar -czf academic-llm-project-code.tar.gz \
    --exclude='storage/data/raw/*.pdf' \
    --exclude='storage/data/processed/*.json' \
    --exclude='storage/indexes/**/*' \
    --exclude='storage/models/**/*' \
    --exclude='__pycache__' \
    --exclude='.ipynb_checkpoints' \
    --exclude='.venv' \
    --exclude='*.log' \
    config/ modules/ *.py *.md *.txt *.sh requirements-file.txt

# 或者压缩整个项目（包括数据，约 213MB）
tar -czf academic-llm-project-full.tar.gz \
    --exclude='__pycache__' \
    --exclude='.ipynb_checkpoints' \
    --exclude='.venv' \
    --exclude='*.log' \
    .
```

然后在 JupyterLab 文件浏览器中下载 `.tar.gz` 文件。

### 选项 C: 使用 SCP（从本地终端）

如果您有 SSH 访问权限，在**本地终端**运行：

```bash
# 下载整个项目
scp -r user@server:/home/jovyan/work ./academic-llm-project

# 或只下载代码（排除大数据）
scp -r --exclude='storage/data' --exclude='storage/indexes' \
    user@server:/home/jovyan/work ./academic-llm-project-code
```

### 选项 D: 使用 rsync（推荐，支持断点续传）

在**本地终端**运行：

```bash
# 同步整个项目
rsync -avz --progress user@server:/home/jovyan/work/ ./academic-llm-project/

# 只同步代码（排除大数据）
rsync -avz --progress \
    --exclude='storage/data/raw' \
    --exclude='storage/indexes' \
    --exclude='storage/models' \
    --exclude='__pycache__' \
    user@server:/home/jovyan/work/ ./academic-llm-project-code/
```

---

## 方法 2: 推送到 GitHub

### 步骤 1: 初始化 Git 仓库

```bash
cd /home/jovyan/work

# 初始化 git
git init

# 检查 .gitignore 是否存在
ls -la .gitignore
```

### 步骤 2: 配置 Git（如果还没配置）

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 步骤 3: 添加文件并提交

```bash
# 添加所有文件（.gitignore 会自动排除不需要的文件）
git add .

# 查看将要提交的文件
git status

# 提交
git commit -m "Initial commit: Academic LLM Fine-Tuning System"
```

### 步骤 4: 在 GitHub 创建仓库

1. 访问 https://github.com/new
2. 创建新仓库（例如：`academic-llm-finetuning`）
3. **不要**初始化 README、.gitignore 或 license（我们已经有了）

### 步骤 5: 推送到 GitHub

```bash
# 添加远程仓库（替换 YOUR_USERNAME 和 REPO_NAME）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 或者使用 SSH（如果配置了 SSH key）
git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 步骤 6: 如果需要认证

如果提示输入用户名和密码：
- **用户名**: 您的 GitHub 用户名
- **密码**: 使用 Personal Access Token（不是 GitHub 密码）
  - 创建 Token: https://github.com/settings/tokens
  - 权限：至少需要 `repo` 权限

---

## 推荐的文件排除列表

如果只想推送代码（不包含数据），确保 `.gitignore` 包含：

```
storage/data/raw/*.pdf
storage/data/processed/*.json
storage/data/synthetic/*.jsonl
storage/indexes/**/*
storage/models/**/*
*.log
__pycache__/
.ipynb_checkpoints/
.venv/
.env
```

---

## 快速命令参考

### 创建代码压缩包（排除数据）
```bash
cd /home/jovyan/work
tar -czf ../academic-llm-code.tar.gz \
    --exclude='storage/data' \
    --exclude='storage/indexes' \
    --exclude='storage/models' \
    --exclude='__pycache__' \
    --exclude='.ipynb_checkpoints' \
    --exclude='.venv' \
    --exclude='*.log' \
    .
```

### Git 快速推送
```bash
cd /home/jovyan/work
git add .
git commit -m "Update project"
git push origin main
```

---

## 注意事项

1. **数据文件很大**（约 200MB+），建议：
   - 推送到 GitHub 时排除 `storage/` 目录
   - 或使用 Git LFS（Large File Storage）

2. **敏感信息**：
   - 确保 `.env` 文件在 `.gitignore` 中
   - 不要提交 API keys

3. **项目大小**：
   - 代码部分：约 1-2MB
   - 包含数据：约 213MB

