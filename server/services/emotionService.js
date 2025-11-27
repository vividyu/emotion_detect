/**
 * Emotion Service
 * 
 * 负责从 JSON 文件读取情绪数据
 * 
 * 未来数据库集成说明：
 * - 将此服务改为查询数据库 (e.g., Sequelize models)
 * - 保持相同的返回格式，这样路由层不需要修改
 * - 可以添加 EmotionModel (models/emotion.js) 来替代文件读取
 */

const fs = require('fs').promises;
const path = require('path');

class EmotionService {
  constructor(dataDir = null) {
    // 数据目录默认为项目根目录下的 results 文件夹
    this.dataDir = dataDir || path.join(__dirname, '../../results');
  }

  /**
   * 读取指定目录下的所有 JSON 文件
   * @returns {Promise<Array>} JSON 文件名数组
   */
  async getJsonFiles() {
    try {
      const files = await fs.readdir(this.dataDir);
      return files.filter(file => file.endsWith('.json'));
    } catch (error) {
      console.error('Error reading data directory:', error);
      throw new Error('Failed to read data directory');
    }
  }

  /**
   * 读取单个 JSON 文件
   * @param {string} filename - JSON 文件名
   * @returns {Promise<Object>} 解析后的 JSON 对象
   */
  async readJsonFile(filename) {
    try {
      const filePath = path.join(this.dataDir, filename);
      const content = await fs.readFile(filePath, 'utf-8');
      return JSON.parse(content);
    } catch (error) {
      console.error(`Error reading file ${filename}:`, error);
      return null;
    }
  }

  /**
   * 获取所有情绪记录（扁平化格式）
   * 每个 face 一条记录，包含 image 信息
   * @returns {Promise<Array>} 情绪记录数组
   */
  async getAllEmotions() {
    const jsonFiles = await this.getJsonFiles();
    const allRecords = [];

    for (const filename of jsonFiles) {
      const data = await this.readJsonFile(filename);
      if (!data || !data.faces) continue;

      // 从文件名提取信息（可选：添加时间戳）
      const imageName = data.image || filename.replace('.json', '');
      
      // 将每个 face 转换为独立记录
      data.faces.forEach(face => {
        allRecords.push({
          filename: filename,
          image: imageName,
          faceId: face.id,
          bbox: face.bbox,
          emotionClass: face.emotion_class,
          emotionName: face.emotion_name,
          valence: face.valence,
          arousal: face.arousal,
          // 可选：添加时间戳（如果文件名包含或使用文件修改时间）
          timestamp: this.extractTimestamp(filename) || Date.now()
        });
      });
    }

    // 按 filename 或 timestamp 排序
    allRecords.sort((a, b) => {
      if (a.timestamp && b.timestamp) {
        return a.timestamp - b.timestamp;
      }
      return a.filename.localeCompare(b.filename);
    });

    return allRecords;
  }

  /**
   * 获取指定图像的情绪数据
   * @param {string} imageName - 图像名称（不含 .json 扩展名）
   * @returns {Promise<Object|null>} 图像的情绪数据
   */
  async getEmotionByImage(imageName) {
    const filename = imageName.endsWith('.json') ? imageName : `${imageName}.json`;
    const data = await this.readJsonFile(filename);
    
    if (!data) {
      return null;
    }

    return {
      filename: filename,
      image: data.image || imageName,
      faces: data.faces.map(face => ({
        faceId: face.id,
        bbox: face.bbox,
        emotionClass: face.emotion_class,
        emotionName: face.emotion_name,
        valence: face.valence,
        arousal: face.arousal
      }))
    };
  }

  /**
   * 获取指定 faceId 的所有历史记录
   * （假设 faceId 在不同图像中是稳定的）
   * @param {number} faceId - 面部 ID
   * @returns {Promise<Array>} 该 face 的所有记录
   */
  async getEmotionsByFaceId(faceId) {
    const allEmotions = await this.getAllEmotions();
    return allEmotions.filter(record => record.faceId === parseInt(faceId));
  }

  /**
   * 获取情绪统计信息
   * @returns {Promise<Object>} 统计信息
   */
  async getEmotionStats() {
    const allEmotions = await this.getAllEmotions();
    
    const emotionCounts = {};
    let totalValence = 0;
    let totalArousal = 0;

    allEmotions.forEach(record => {
      // 统计每种情绪的数量
      emotionCounts[record.emotionName] = (emotionCounts[record.emotionName] || 0) + 1;
      totalValence += record.valence;
      totalArousal += record.arousal;
    });

    return {
      totalRecords: allEmotions.length,
      emotionDistribution: emotionCounts,
      averageValence: totalValence / allEmotions.length,
      averageArousal: totalArousal / allEmotions.length
    };
  }

  /**
   * 从文件名提取时间戳（可根据实际文件名格式调整）
   * @param {string} filename - 文件名
   * @returns {number|null} 时间戳或 null
   */
  extractTimestamp(filename) {
    // 示例：如果文件名包含时间戳，可以在这里解析
    // 例如：emotion_1638316800000.json
    const match = filename.match(/(\d{13})/);
    if (match) {
      return parseInt(match[1]);
    }
    return null;
  }
}

module.exports = EmotionService;
