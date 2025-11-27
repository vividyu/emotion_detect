/**
 * Emotion Routes
 * 
 * REST API 端点用于情绪数据访问
 */

const express = require('express');
const router = express.Router();
const EmotionService = require('../services/emotionService');

// 初始化服务（可以通过环境变量配置数据目录）
const emotionService = new EmotionService(process.env.DATA_DIR);

/**
 * GET /api/emotions
 * 获取所有情绪记录
 * 返回扁平化的记录数组，每个 face 一条记录
 */
router.get('/', async (req, res) => {
  try {
    const emotions = await emotionService.getAllEmotions();
    res.json({
      success: true,
      count: emotions.length,
      data: emotions
    });
  } catch (error) {
    console.error('Error fetching emotions:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch emotions',
      message: error.message
    });
  }
});

/**
 * GET /api/emotions/stats
 * 获取情绪统计信息
 */
router.get('/stats', async (req, res) => {
  try {
    const stats = await emotionService.getEmotionStats();
    res.json({
      success: true,
      data: stats
    });
  } catch (error) {
    console.error('Error fetching emotion stats:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch statistics',
      message: error.message
    });
  }
});

/**
 * GET /api/emotions/image/:imageName
 * 获取指定图像的情绪数据
 * @param imageName - 图像名称（可以带或不带 .json 扩展名）
 */
router.get('/image/:imageName', async (req, res) => {
  try {
    const { imageName } = req.params;
    const data = await emotionService.getEmotionByImage(imageName);
    
    if (!data) {
      return res.status(404).json({
        success: false,
        error: 'Image not found',
        message: `No data found for image: ${imageName}`
      });
    }

    res.json({
      success: true,
      data: data
    });
  } catch (error) {
    console.error('Error fetching emotion by image:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch emotion data',
      message: error.message
    });
  }
});

/**
 * GET /api/emotions/face/:faceId
 * 获取指定 faceId 的所有历史记录
 * @param faceId - 面部 ID
 */
router.get('/face/:faceId', async (req, res) => {
  try {
    const { faceId } = req.params;
    const records = await emotionService.getEmotionsByFaceId(faceId);
    
    res.json({
      success: true,
      count: records.length,
      data: records
    });
  } catch (error) {
    console.error('Error fetching emotions by face ID:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch emotion records',
      message: error.message
    });
  }
});

module.exports = router;
