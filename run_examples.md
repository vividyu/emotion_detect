# 使用示例

## 图像模式示例

### 1. 处理单个图像
```bash
python predict_image.py --images data\images\KA.AN1.39.tiff --model emonet\pretrained\emonet_8.pth --output_dir results
```

### 2. 批量处理目录中的所有图像
```bash
python predict_image.py --images data\images --model emonet\pretrained\emonet_8.pth --output_dir results
```

### 3. 使用 5 类情感模型
```bash
python predict_image.py --images data\images --model emonet\pretrained\emonet_5.pth --expressions 5 --output_dir results
```

## 视频模式示例

### 处理视频文件
```bash
python predict_image.py --video "data\videos\YTDown.com_Shorts_Media_drX-ABVHT_8_001_480p.mp4" --model emonet\pretrained\emonet_8.pth --output_video output.mp4
```

**重要提示：**
- 视频模式需要指定具体的视频文件路径，不能使用目录
- 视频处理会比较耗时，258 帧的视频大约需要几分钟
- 输出视频会包含原始帧、面部检测框、情感标签和效价-唤醒度可视化

## 输出说明

### 图像模式输出
- 在指定的 `output_dir` 目录下生成 JSON 文件
- 每个图像对应一个 JSON 文件，包含所有检测到的面部及其情感信息

### 视频模式输出
- 生成一个 MP4 视频文件
- 视频包含三部分：
  1. 左侧：原始视频帧 + 面部检测框和情感标签
  2. 右上：裁剪的面部图像
  3. 右下：效价-唤醒度二维情绪空间（红点表示当前情绪位置）

## 常见问题

### 1. 提示"是一个目录"错误
**原因：** 视频模式需要具体的文件路径，不能使用目录

**解决：** 使用完整的文件路径
```bash
# ❌ 错误
python predict_image.py --video data\videos --model ...

# ✅ 正确
python predict_image.py --video "data\videos\your_video.mp4" --model ...
```

### 2. 某些帧未检测到面部
**说明：** 这是正常现象，视频中某些帧可能没有面部或面部不清晰
- 程序会自动跳过这些帧并继续处理
- 输出视频中未检测到面部的帧只显示原始画面

### 3. 处理速度较慢
**原因：** 每帧都需要进行面部检测和情感识别
- 面部检测是最耗时的步骤
- GPU 会显著加速处理过程
- 258 帧的视频大约需要 3-5 分钟（取决于硬件）
