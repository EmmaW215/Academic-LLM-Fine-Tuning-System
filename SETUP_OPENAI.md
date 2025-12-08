# 设置 OpenAI API Key

## 问题原因

Synthetic Data Generation 需要 OpenAI API key 来使用 GPT-4 生成 Q&A 训练数据。

当前状态：
- ❌ OpenAI API Key 未设置
- ✅ 已收集 50 篇论文数据
- ❌ 因此无法生成训练数据

## 解决方案

### 方法 1：使用环境变量（推荐）

在终端中运行：
```bash
export OPENAI_API_KEY='your-api-key-here'
```

然后重启 Gradio UI。

### 方法 2：创建 .env 文件

1. 在项目根目录创建 `.env` 文件：
```bash
echo "OPENAI_API_KEY=your-api-key-here" > /home/jovyan/work/.env
```

2. 重启 Gradio UI（代码会自动读取 .env 文件）

### 获取 API Key

1. 访问 https://platform.openai.com/api-keys
2. 登录您的 OpenAI 账户
3. 创建新的 API key
4. 复制 key 并按照上述方法设置

## 验证设置

设置后，在 Gradio UI 中：
1. 切换到 "Synthetic Data" 标签页
2. 点击 "Generate Q&A Data"
3. 应该能看到生成进度和结果

## 注意事项

- API key 使用会产生费用（GPT-4 按 token 计费）
- 建议先用少量论文测试（如 10 篇，每篇 3 个 Q&A）
- 生成 50 篇论文 × 5 Q&A 可能需要一些时间和费用
