# 情绪检测平台 - 快速安装脚本
# Emotion Detection Platform - Quick Start Script

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "情绪检测平台安装" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# 检查Node.js
Write-Host "[1/4] 检查 Node.js 安装..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✓ 已找到 Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ 未找到 Node.js，请从 https://nodejs.org/ 下载安装" -ForegroundColor Red
    exit 1
}

# 检查Python
Write-Host "[2/4] 检查 Python 安装..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ 已找到 Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ 未找到 Python，请从 https://www.python.org/ 下载安装 Python 3.10+" -ForegroundColor Red
    exit 1
}

# 安装后端依赖
Write-Host "[3/4] 安装后端依赖..." -ForegroundColor Yellow
Set-Location -Path "server"
if (-not (Test-Path "node_modules")) {
    npm install
    Write-Host "✓ 后端依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "✓ 后端依赖已安装" -ForegroundColor Green
}
Set-Location -Path ".."

# 安装前端依赖
Write-Host "[4/4] 安装前端依赖..." -ForegroundColor Yellow
Set-Location -Path "frontend"
if (-not (Test-Path "node_modules")) {
    npm install
    Write-Host "✓ 前端依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "✓ 前端依赖已安装" -ForegroundColor Green
}
Set-Location -Path ".."

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "安装完成！" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "启动平台：" -ForegroundColor Yellow
Write-Host "  1. 启动后端：  cd server;  npm start" -ForegroundColor White
Write-Host "  2. 启动前端： cd frontend; npm start" -ForegroundColor White
Write-Host ""
Write-Host "或使用启动脚本： .\start-platform.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "后端 API：  http://localhost:3001" -ForegroundColor Cyan
Write-Host "前端界面：  http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "更多详情请查看 FULL_STACK_README.md" -ForegroundColor Gray
