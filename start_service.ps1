# PowerShell启动脚本
Write-Host "正在启动企业信用评估模型后端服务..." -ForegroundColor Green
Write-Host ""

# 设置工作目录
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

# 启动Flask服务
Write-Host "启动Flask应用，端口: 8000" -ForegroundColor Yellow
Write-Host "访问地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 CTRL+C 停止服务" -ForegroundColor Gray
Write-Host ""

try {
    $env:FLASK_APP = "backend/api/app.py"
    $env:FLASK_ENV = "development"
    $env:PYTHONPATH = "$projectRoot/backend"
    
    C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe backend/api/app.py
} catch {
    Write-Host "启动失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Read-Host "按回车键退出"
}
