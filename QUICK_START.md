# 快速使用指南

## 第一次使用

### 1. 安装依赖（只需执行一次）

```powershell
# 运行自动安装脚本
.\setup-platform.ps1
```

这将自动安装：
- 后端Node.js依赖（Express, CORS）
- 前端React依赖（React, Chart.js, Axios）

### 2. 启动平台

```powershell
# 运行启动脚本（会自动打开两个终端）
.\start-platform.ps1
```

或者手动启动：

```powershell
# 终端1 - 启动后端
cd server
npm start

# 终端2 - 启动前端
cd frontend
npm start
```

### 3. 访问应用

- 前端界面：`http://localhost:3000`
- 后端API：`http://localhost:3001`

---

## 完整工作流程

### 步骤1：运行情绪检测

```powershell
# 激活Python虚拟环境
.\venv\Scripts\Activate.ps1

# 处理图片
python predict_image.py --image data/images/photo.jpg

# 或处理视频
python predict_image.py --video data/videos/video.mp4
```

结果会保存到 `results/` 目录。

### 步骤2：启动可视化平台

```powershell
# 使用快速启动脚本
.\start-platform.ps1
```

### 步骤3：在浏览器中查看

1. 打开 `http://localhost:3000`
2. 查看情绪统计面板
3. 在图表中分析Valence/Arousal趋势
4. 在表格中浏览详细数据
5. 使用过滤器筛选特定情绪

---

## 界面功能说明

### 📊 统计面板（顶部）
- **总记录数**：检测到的人脸总数
- **平均Valence**：平均情绪效价（-1到+1）
- **平均Arousal**：平均唤醒度（-1到+1）
- **情绪分布**：各情绪类型的横向条形图

### 📈 时序图表
- **蓝线**：Valence（情绪正负性）
- **红线**：Arousal（情绪激烈度）
- **悬停**：查看具体数值和情绪名称
- **缩放**：鼠标滚轮缩放图表

### 📋 数据表格
- **排序**：点击列标题升序/降序排序
- **表情符号**：快速识别情绪类型
- **颜色编码**：Valence值（绿色=正面，红色=负面）
- **分页**：每页20条记录

### 🔍 过滤器
- **情绪下拉框**：选择特定情绪类型
- **刷新按钮**：重新加载数据

---

## 常见问题

### Q1: 前端显示"无数据"？

**原因**：`results/` 目录为空或没有JSON文件

**解决**：
```powershell
# 先运行情绪检测生成数据
python predict_image.py --image data/images/test.jpg
```

### Q2: API连接失败？

**检查**：
- 后端服务器是否在运行（`http://localhost:3001/health`）
- 端口3001是否被占用
- 防火墙是否允许本地连接

**解决**：
```powershell
# 重启后端
cd server
npm start
```

### Q3: Chart.js图表不显示？

**原因**：数据量不足（至少需要2条记录）

**解决**：处理更多图片或视频帧以获得足够数据

### Q4: 如何更改端口？

**后端端口**：
```env
# 编辑 server/.env
API_PORT=3001  # 改为其他端口
```

**前端配置**：
```env
# 编辑 frontend/.env
REACT_APP_API_URL=http://localhost:3001  # 同步修改
```

---

## 数据解读指南

### Valence（情绪效价）
- **+0.5 以上**：积极情绪（开心、兴奋）
- **-0.2 到 +0.2**：中性情绪（平静）
- **-0.5 以下**：消极情绪（悲伤、愤怒）

### Arousal（唤醒度）
- **+0.5 以上**：高能量（兴奋、恐惧）
- **-0.2 到 +0.2**：中等能量（平静）
- **-0.5 以下**：低能量（疲倦、沮丧）

### 情绪组合示例
- **快乐**：Valence=+0.8, Arousal=+0.6（高正面，高能量）
- **平静**：Valence=+0.3, Arousal=-0.2（低正面，低能量）
- **愤怒**：Valence=-0.7, Arousal=+0.8（高负面，高能量）
- **悲伤**：Valence=-0.6, Arousal=-0.4（高负面，低能量）

---

## 下一步

### 扩展功能
1. **添加更多图片**：在 `data/images/` 中添加图片
2. **处理视频**：获得时序情绪数据
3. **导出报告**：使用浏览器打印功能导出PDF

### 自定义配置
1. **修改数据目录**：编辑 `server/.env` 中的 `DATA_DIR`
2. **调整分页**：修改 `EmotionTable.jsx` 中的 `itemsPerPage`
3. **更改主题色**：编辑 `App.css` 中的颜色值

### 学习资源
- **EmoNet论文**：查看 `emonet/README.md`
- **API文档**：查看 `FULL_STACK_README.md`
- **React文档**：https://react.dev/

---

## 关闭平台

在两个终端窗口中按 `Ctrl + C` 停止服务器。

---

## 技术支持

遇到问题？
1. 查看 `FULL_STACK_README.md` 中的故障排除章节
2. 检查终端输出的错误信息
3. 验证所有依赖是否正确安装
