@echo off
chcp 65001 >nul
title 企业信用评估模型 - 后端服务

echo ========================================
echo 企业信用评估模型 - 后端服务启动
echo ========================================
echo.

cd /d "%~dp0"

echo 当前目录: %CD%
echo.
echo 正在启动后端服务...
echo 服务地址: http://localhost:8000
echo 健康检查: http://localhost:8000/api/health
echo.
echo 按 CTRL+C 可以停止服务
echo ========================================
echo.

set PYTHONPATH=%CD%\backend
C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe backend/api/app.py

if errorlevel 1 (
    echo.
    echo 服务启动失败！
    echo.
    pause
)
