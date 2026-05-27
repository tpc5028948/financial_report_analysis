@echo off
echo 🚀 开始部署个人作品集...

REM 检查是否已经是 git 仓库
if not exist ".git" (
    echo 📦 初始化 Git 仓库...
    git init
    git branch -M main
) else (
    echo ✅ Git 仓库已存在
)

REM 添加所有文件
echo 📝 添加文件...
git add .

REM 提交
set /p commit_msg=请输入提交信息 (默认: Update portfolio): 
if "%commit_msg%"=="" set commit_msg=Update portfolio
git commit -m "%commit_msg%"

REM 检查是否已配置 remote
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo.
    echo 🔗 请提供你的 GitHub 仓库地址
    set /p repo_url=例如: https://github.com/你的用户名/你的仓库名.git: 
    git remote add origin "%repo_url%"
) else (
    echo ✅ Remote origin 已配置
)

REM 推送
echo 🚀 推送到 GitHub...
git push -u origin main

echo.
echo ✅ 代码已成功推送到 GitHub!
echo.
echo 📋 下一步操作:
echo 1. 访问你的 GitHub 仓库
echo 2. 进入 Settings -^> Pages
echo 3. 选择 main 分支并保存
echo 4. 等待几分钟，访问 https://你的用户名.github.io/你的仓库名/
echo.
echo 📚 详细部署说明请查看 DEPLOY.md 文件
pause
