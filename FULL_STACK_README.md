# Emotion Detection Visualization Platform

完整的情绪检测可视化平台，包含Python情绪检测引擎、Node.js API服务器和React可视化前端。

## 项目架构

```
emotion_detect/
├── predict_image.py          # Python情绪检测主程序（支持图片和视频）
├── models/                   # EmoNet模型包装
│   └── emotion_model.py
├── utils/                    # 工具函数
│   └── face_utils.py
├── server/                   # Node.js API服务器
│   ├── api-server.js        # Express服务器主文件
│   ├── routes/              # API路由
│   │   └── emotions.js
│   ├── services/            # 服务层（JSON文件读取）
│   │   └── emotionService.js
│   ├── package.json         # 后端依赖配置
│   └── .env                 # 后端环境变量
└── frontend/                # React可视化前端
    ├── src/
    │   ├── App.js           # 主应用组件
    │   ├── App.css          # 主应用样式
    │   ├── components/      # React组件
    │   │   ├── EmotionChart.jsx      # 时序图表（Chart.js）
    │   │   ├── EmotionTable.jsx      # 数据表格
    │   │   ├── EmotionTable.css
    │   │   ├── EmotionStats.jsx      # 统计面板
    │   │   └── EmotionStats.css
    │   ├── index.js         # React入口
    │   └── index.css
    ├── public/
    │   ├── index.html       # HTML模板
    │   └── manifest.json    # PWA配置
    ├── package.json         # 前端依赖配置
    └── .env                 # 前端环境变量
```

## 功能特性

### Python情绪检测引擎
- ✅ 图片情绪检测（支持JPEG/PNG/TIFF）
- ✅ 视频情绪检测（支持MP4/AVI等格式）
- ✅ EmoNet模型集成（8种情绪分类）
- ✅ 人脸检测与追踪
- ✅ Valence（情绪效价）和Arousal（唤醒度）输出
- ✅ JSON结果输出
- ✅ 可视化视频输出（标注人脸和情绪）

### Node.js API服务器
- ✅ RESTful API设计
- ✅ 文件系统JSON读取（无需数据库）
- ✅ CORS支持
- ✅ 服务层模式（便于未来迁移到数据库）
- ✅ 静态文件服务（图片访问）

### React可视化前端
- ✅ Chart.js时序图表（Valence/Arousal趋势）
- ✅ 可排序数据表格（支持分页）
- ✅ 统计面板（总数、平均值、分布图）
- ✅ 情绪过滤器
- ✅ 响应式设计
- ✅ 现代渐变UI

---

## 快速开始

### 1. Python环境设置

#### 安装依赖
```powershell
# 创建虚拟环境（推荐）
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装Python依赖
pip install -r requirements.txt
```

#### 运行情绪检测
```powershell
# 处理图片
python predict_image.py --image data/images/test.jpg

# 处理视频
python predict_image.py --video data/videos/test.mp4

# 使用指定的EmoNet模型
python predict_image.py --image data/images/test.jpg --model emonet/pretrained/emonet_8.pth
```

输出结果保存在 `results/` 目录：
- `{filename}_result.json` - 检测结果JSON文件
- `{filename}_output.mp4` - 可视化视频（仅视频模式）

---

### 2. 后端API服务器设置

#### 安装依赖
```powershell
cd server
npm install
```

#### 配置环境变量
编辑 `server/.env`:
```env
API_PORT=3001
DATA_DIR=results
CORS_ORIGIN=http://localhost:3000
```

#### 启动服务器
```powershell
# 生产模式
npm start

# 开发模式（自动重启）
npm run dev
```

服务器运行在 `http://localhost:3001`

---

### 3. 前端React应用设置

#### 安装依赖
```powershell
cd frontend
npm install
```

#### 配置环境变量
编辑 `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:3001
```

#### 启动前端
```powershell
npm start
```

前端应用运行在 `http://localhost:3000`

---

## API端点文档

### 基础URL
```
http://localhost:3001/api
```

### 端点列表

#### 1. 获取所有情绪数据
```http
GET /api/emotions
```

响应示例：
```json
[
  {
    "image": "test_001.jpg",
    "faceId": 1,
    "bbox": [100, 150, 200, 250],
    "emotion_class": 3,
    "emotion_name": "happiness",
    "valence": 0.85,
    "arousal": 0.62
  }
]
```

#### 2. 按图片名称查询
```http
GET /api/emotions/image/:imageName
```

示例：`GET /api/emotions/image/test_001.jpg`

#### 3. 按人脸ID查询
```http
GET /api/emotions/face/:faceId
```

示例：`GET /api/emotions/face/1`

#### 4. 获取统计数据
```http
GET /api/emotions/stats
```

响应示例：
```json
{
  "totalRecords": 258,
  "avgValence": 0.23,
  "avgArousal": 0.45,
  "emotionDistribution": {
    "neutral": 145,
    "happiness": 67,
    "sadness": 23,
    "anger": 12,
    "fear": 6,
    "disgust": 3,
    "surprise": 2,
    "contempt": 0
  }
}
```

#### 5. 健康检查
```http
GET /health
```

---

## 数据格式

### JSON结果文件结构
```json
{
  "image": "test_001.jpg",
  "faces": [
    {
      "id": 1,
      "bbox": [100, 150, 200, 250],
      "emotion_class": 3,
      "emotion_name": "happiness",
      "valence": 0.8542,
      "arousal": 0.6231,
      "expression_probs": {
        "neutral": 0.05,
        "happiness": 0.82,
        "sadness": 0.03,
        "anger": 0.02,
        "fear": 0.01,
        "disgust": 0.01,
        "surprise": 0.05,
        "contempt": 0.01
      }
    }
  ]
}
```

### 情绪类别映射
```python
EMOTION_NAMES = {
    0: 'neutral',     # 中性
    1: 'happiness',   # 快乐
    2: 'sadness',     # 悲伤
    3: 'surprise',    # 惊讶
    4: 'fear',        # 恐惧
    5: 'disgust',     # 厌恶
    6: 'anger',       # 愤怒
    7: 'contempt'     # 轻蔑
}
```

### Valence和Arousal解读

**Valence（情绪效价）**：情绪的正负性
- **+1.0 到 +0.3**：积极情绪（快乐、兴奋、满足）
- **+0.3 到 -0.3**：中性情绪（平静、放松）
- **-0.3 到 -1.0**：消极情绪（悲伤、恐惧、愤怒）

**Arousal（唤醒度）**：情绪的激烈程度
- **+1.0 到 +0.5**：高唤醒（兴奋、愤怒、恐惧）
- **+0.5 到 -0.5**：中等唤醒（满足、平静）
- **-0.5 到 -1.0**：低唤醒（悲伤、疲倦、放松）

**情绪象限**：
- **高Valence + 高Arousal**：兴奋、狂喜
- **高Valence + 低Arousal**：满足、平静
- **低Valence + 高Arousal**：愤怒、恐惧
- **低Valence + 低Arousal**：悲伤、沮丧

---

## 前端功能使用

### 1. 情绪时序图表
- 显示Valence和Arousal的时间趋势
- 双Y轴设计
- 悬停查看详细情绪名称

### 2. 数据表格
- 点击列标题排序
- 每页显示20条记录
- 情绪emoji指示器
- Valence值颜色编码（绿色=正面，红色=负面）

### 3. 统计面板
- 总记录数
- 平均Valence和Arousal
- 情绪分布横向条形图

### 4. 过滤功能
- 按情绪类型过滤
- 实时刷新按钮

---

## 未来扩展

### 数据库集成
当前架构使用服务层模式，可无缝迁移到数据库：

1. **修改 `emotionService.js`**：
   ```javascript
   // 替换文件读取为数据库查询
   async getAllEmotions() {
     return await EmotionModel.findAll();
   }
   ```

2. **routes和前端无需修改**

3. **推荐数据库**：
   - MongoDB（文档型，适合JSON结构）
   - PostgreSQL（关系型，适合复杂查询）
   - MySQL（关系型，通用选择）

### 功能扩展建议
- 实时视频流处理
- 情绪报告PDF导出
- 多用户权限管理
- 情绪热力图可视化
- 历史对比分析
- WebSocket实时推送

---

## 故障排除

### Python部分

**问题：找不到人脸**
```powershell
# 检查face_alignment安装
pip install face-alignment --upgrade
```

**问题：CUDA内存不足**
```python
# 在predict_image.py中修改
device = 'cpu'  # 使用CPU模式
```

### 后端部分

**问题：CORS错误**
```env
# 修改server/.env
CORS_ORIGIN=*  # 允许所有源（仅开发环境）
```

**问题：找不到JSON文件**
```env
# 检查DATA_DIR路径
DATA_DIR=../results  # 使用相对路径
```

### 前端部分

**问题：API连接失败**
```env
# 检查frontend/.env
REACT_APP_API_URL=http://localhost:3001  # 确保端口正确
```

**问题：Chart.js不显示**
```powershell
# 重新安装依赖
npm install chart.js react-chartjs-2 --save
```

---

## 技术栈

### 后端
- **Node.js** v18+
- **Express** v4.21.1
- **cors** v2.8.5

### 前端
- **React** v18.2.0
- **Chart.js** v4.4.0
- **react-chartjs-2** v5.2.0
- **axios** v1.6.0

### Python
- **Python** 3.10+
- **PyTorch** 1.13+
- **OpenCV** 4.8+
- **face-alignment** 1.4+

---

## 许可证

MIT License

---

## 联系方式

如有问题，请提交Issue或联系开发团队。
