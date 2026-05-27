#!/bin/bash

# 个人作品集部署脚本
# 使用前请先在 GitHub 上创建仓库

echo "🚀 开始部署个人作品集..."

# 检查是否已经是 git 仓库
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    git branch -M main
else
    echo "✅ Git 仓库已存在"
fi

# 添加所有文件
echo "📝 添加文件..."
git add .

# 提交
read -p "请输入提交信息 (默认: Update portfolio): " commit_msg
commit_msg=${commit_msg:-"Update portfolio"}
git commit -m "$commit_msg"

# 检查是否已配置 remote
if ! git remote get-url origin > /dev/null 2>&1; then
    echo ""
    echo "🔗 请提供你的 GitHub 仓库地址"
    read -p "例如: https://github.com/你的用户名/你的仓库名.git: " repo_url
    git remote add origin "$repo_url"
else
    echo "✅ Remote origin 已配置"
fi

# 推送
echo "🚀 推送到 GitHub..."
git push -u origin main

echo ""
echo "✅ 代码已成功推送到 GitHub!"
echo ""
echo "📋 下一步操作:"
echo "1. 访问你的 GitHub 仓库"
echo "2. 进入 Settings -> Pages"
echo "3. 选择 main 分支并保存"
echo "4. 等待几分钟，访问 https://你的用户名.github.io/你的仓库名/"
echo ""
echo "📚 详细部署说明请查看 DEPLOY.md 文件"
