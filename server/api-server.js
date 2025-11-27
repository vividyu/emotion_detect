/**
 * Emotion Visualization API Server
 * 
 * 独立的 API 服务器，用于提供情绪数据接口
 * 支持 CORS，方便前端调用
 */

const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();

// 中间件配置
app.use(cors()); // 启用 CORS
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 静态文件服务（可选，如果需要提供图片）
app.use('/images', express.static(path.join(__dirname, '../data/images')));

// API 路由
const emotionRoutes = require('./routes/emotions');
app.use('/api/emotions', emotionRoutes);

// 健康检查端点
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    message: 'Emotion API Server is running',
    timestamp: new Date().toISOString()
  });
});

// 根路径
app.get('/', (req, res) => {
  res.json({
    message: 'Emotion Detection API',
    version: '1.0.0',
    endpoints: {
      health: '/api/health',
      emotions: '/api/emotions',
      emotionsByImage: '/api/emotions/image/:imageName',
      emotionsByFace: '/api/emotions/face/:faceId',
      stats: '/api/emotions/stats'
    }
  });
});

// 错误处理
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(err.status || 500).json({
    success: false,
    error: err.message || 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// 404 处理
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found'
  });
});

// 启动服务器
const PORT = 3001; // 默认端口
app.listen(PORT, () => {
  console.log(`🚀 Emotion API Server running on port ${PORT}`);
  console.log(`📊 API Documentation: http://localhost:${PORT}/`);
  console.log(`💚 Health check: http://localhost:${PORT}/api/health`);
});

module.exports = app;
