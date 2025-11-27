import logging
import os
from typing import Dict, Optional, Tuple

import torch
from torch import nn

logger = logging.getLogger(__name__)


class EmotionModel:
    """包装预训练的 EmoNet 模型用于 valence/arousal 预测和离散情感分类。"""

    # 情感类别映射
    EMOTION_CLASSES_8 = {
        0: "Neutral",
        1: "Happy", 
        2: "Sad",
        3: "Surprise",
        4: "Fear",
        5: "Disgust",
        6: "Anger",
        7: "Contempt"
    }
    
    EMOTION_CLASSES_5 = {
        0: "Neutral",
        1: "Happy",
        2: "Sad", 
        3: "Surprise",
        4: "Fear"
    }

    def __init__(self, model_path: str, device: Optional[torch.device] = None, n_expression: int = 8):
        """
        参数：
            model_path: EmoNet 权重文件 (.pth/.pt) 的路径。
            device: 可选的 torch.device。默认为 CUDA（如果可用）。
            n_expression: 模型训练的离散表情类别数量 (5 或 8)。
        """
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device
        self.n_expression = n_expression
        self.emotion_classes = self.EMOTION_CLASSES_8 if n_expression == 8 else self.EMOTION_CLASSES_5
        
        logger.info("在设备上初始化 EmotionModel：%s", self.device)

        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"模型文件未找到：{model_path}")

        logger.info("从 %s 加载 EmoNet 模型权重", model_path)
        checkpoint = torch.load(model_path, map_location=self.device)

        state_dict = checkpoint["state_dict"] if isinstance(checkpoint, dict) and "state_dict" in checkpoint else checkpoint

        # EmoNet definition is expected to be provided by the external emonet package.
        # The class is imported lazily here to make it configurable by the user environment.
        from emonet.emonet.models import EmoNet  # type: ignore

        self.model = EmoNet(n_expression=n_expression).to(self.device)
        self.model.load_state_dict(state_dict, strict=False)
        self.model.eval()
        logger.info("EmoNet 模型已加载并准备好进行预测。")

    def predict(self, face_tensor: torch.Tensor) -> Dict[str, any]:
        """
        对单个面部张量运行推理。

        参数：
            face_tensor: 预处理的面部图像张量，形状为 (C, H, W) 或 (1, C, H, W)。

        返回：
            包含以下键的字典：
            - valence: 效价值 (float)
            - arousal: 唤醒度 (float)
            - emotion_class: 预测的情感类别索引 (int)
            - emotion_name: 预测的情感类别名称 (str)
            - expression_probs: 所有情感类别的概率 (Tensor)
        """
        if face_tensor.ndim == 3:
            face_tensor = face_tensor.unsqueeze(0)

        face_tensor = face_tensor.to(self.device)
        with torch.no_grad():
            output = self.model(face_tensor)

        # 提取 valence 和 arousal
        if isinstance(output, dict):
            valence = float(output["valence"].clamp(-1.0, 1.0).view(-1)[0].item())
            arousal = float(output["arousal"].clamp(-1.0, 1.0).view(-1)[0].item())
            
            # 提取离散情感分类
            expression_logits = output["expression"]
            expression_probs = nn.functional.softmax(expression_logits, dim=1)
            emotion_class = int(torch.argmax(expression_probs, dim=1).cpu().item())
            emotion_name = self.emotion_classes[emotion_class]
        else:
            valence = float(output[0, 0].item())
            arousal = float(output[0, 1].item())
            emotion_class = 0
            emotion_name = "Unknown"
            expression_probs = None

        logger.debug(
            "预测 emotion=%s, valence=%.3f, arousal=%.3f", 
            emotion_name, valence, arousal
        )
        
        return {
            "valence": valence,
            "arousal": arousal,
            "emotion_class": emotion_class,
            "emotion_name": emotion_name,
            "expression_probs": expression_probs
        }