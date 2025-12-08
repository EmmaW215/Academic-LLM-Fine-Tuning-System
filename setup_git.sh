#!/bin/bash
# 设置 Git 并准备推送到 GitHub

cd /home/jovyan/work

echo "=== 设置 Git 仓库 ==="
echo ""

# 检查是否已初始化
if [ -d .git ]; then
    echo "⚠️  Git 仓库已存在"
    read -p "是否重新初始化？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .git
        git init
    fi
else
    git init
    echo "✅ Git 仓库已初始化"
fi

echo ""
echo "=== 检查 .gitignore ==="
if [ -f .gitignore ]; then
    echo "✅ .gitignore 文件存在"
else
    echo "⚠️  .gitignore 文件不存在，将创建..."
    # .gitignore 应该已经存在
fi

echo ""
echo "=== 添加文件 ==="
git add .

echo ""
echo "=== 文件状态 ==="
git status --short | head -20
echo "..."

echo ""
echo "=== 下一步 ==="
echo "1. 检查文件列表: git status"
echo "2. 提交更改: git commit -m 'Initial commit'"
echo "3. 添加远程仓库: git remote add origin https://github.com/USERNAME/REPO.git"
echo "4. 推送到 GitHub: git push -u origin main"
