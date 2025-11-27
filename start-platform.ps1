# 情绪检测平台 - 启动脚本
# Emotion Detection Platform - Start Script

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "启动情绪检测平台" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已安装依赖
if (-not (Test-Path "server/node_modules")) {
    Write-Host "未找到后端依赖，正在运行安装程序..." -ForegroundColor Yellow
    .\setup-platform.ps1
    Write-Host ""
}

if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "未找到前端依赖，正在运行安装程序..." -ForegroundColor Yellow
    .\setup-platform.ps1
    Write-Host ""
}

# 启动后端
Write-Host "[1/2] 启动后端 API 服务器..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd server; npm start" -WindowStyle Normal

Start-Sleep -Seconds 2

# 启动前端
Write-Host "[2/2] 启动前端 React 应用..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start" -WindowStyle Normal

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "平台启动成功！" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "后端 API：  http://localhost:3001" -ForegroundColor Cyan
Write-Host "前端界面：  http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "在各个终端窗口按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""