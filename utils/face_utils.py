import logging
import os
from math import atan2, degrees
from typing import List, Tuple

import cv2
import face_alignment
import numpy as np
import torch
from skimage import io

logger = logging.getLogger(__name__)

# Initialize the face alignment detector once so it can be reused.
_fa_device = "cuda" if torch.cuda.is_available() else "cpu"
fa = face_alignment.FaceAlignment(
    face_alignment.LandmarksType.TWO_D,
    device=_fa_device,
    face_detector="sfd",
)


def detect_faces(image_path: str) -> List[Tuple[List[int], np.ndarray]]:
    """检测图像中的面部和 68 点地标。

    返回元组列表 (bbox, landmarks)，其中 bbox 为 [x, y, w, h]。
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"图像文件未找到：{image_path}")

    logger.info("检测图像中的面部：%s", image_path)
    image = io.imread(image_path)
    if image.ndim == 3 and image.shape[2] == 4:
        image = image[:, :, :3]  # 移除 alpha 通道

    output = fa.get_landmarks_from_image(image, return_bboxes=True)
    if output is None:
        logger.warning("图像中未找到面部。")
        return []

    # 处理不同格式的输出
    try:
        if isinstance(output, tuple) and len(output) == 3:
            landmarks_list, scores, bbox_array = output
        else:
            logger.warning("意外的输出格式")
            return []
        
        if landmarks_list is None or bbox_array is None:
            logger.warning("图像中未找到面部。")
            return []
        
        faces = []
        for i, (landmarks, bbox) in enumerate(zip(landmarks_list, bbox_array)):
            x1, y1, x2, y2 = bbox[:4].astype(int)
            w, h = x2 - x1, y2 - y1
            bbox_dims = [int(x1), int(y1), int(w), int(h)]
            faces.append((bbox_dims, landmarks))
            logger.debug("面部 %d：bbox=%s", i + 1, bbox_dims)

        return faces
    except Exception as e:
        logger.warning("处理面部检测结果时出错：%s", e)
        return []


def align_face(image: np.ndarray, landmarks: np.ndarray, target_size: int = 256) -> np.ndarray:
    """旋转图像，使眼睛水平对齐。"""
    left_eye_pts = landmarks[36:42]
    right_eye_pts = landmarks[42:48]

    left_eye_center = left_eye_pts.mean(axis=0)
    right_eye_center = right_eye_pts.mean(axis=0)

    dy = right_eye_center[1] - left_eye_center[1]
    dx = right_eye_center[0] - left_eye_center[0]
    angle = degrees(atan2(dy, dx))

    eyes_center = (
        float((left_eye_center[0] + right_eye_center[0]) / 2.0),
        float((left_eye_center[1] + right_eye_center[1]) / 2.0),
    )

    rot_matrix = cv2.getRotationMatrix2D(eyes_center, angle, scale=1.0)
    height, width = image.shape[:2]
    rotated = cv2.warpAffine(image, rot_matrix, (width, height), flags=cv2.INTER_LINEAR)

    if target_size != min(height, width):
        # Resize while maintaining aspect ratio for predictable downstream cropping.
        rotated = cv2.resize(rotated, (width, height))

    return rotated


def crop_face(image: np.ndarray, bbox: List[int], target_size: int = 256) -> np.ndarray:
    """从图像中裁剪边界框并调整大小到目标尺寸。"""
    x, y, w, h = bbox
    ih, iw = image.shape[:2]

    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(iw, x + w), min(ih, y + h)
    face_roi = image[y0:y1, x0:x1]

    if face_roi.size == 0:
        raise ValueError("面部 ROI 为空。请检查边界框坐标。")

    return cv2.resize(face_roi, (target_size, target_size))


def prepare_face_tensor(face_image: np.ndarray) -> torch.Tensor:
    """将裁剪的面部图像转换为标准化的 torch 张量。"""
    if face_image.ndim == 2:
        face_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
    elif face_image.shape[2] == 4:
        face_image = cv2.cvtColor(face_image, cv2.COLOR_BGRA2RGB)
    else:
        face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

    face_image = face_image.astype(np.float32) / 255.0
    tensor = torch.from_numpy(face_image.transpose(2, 0, 1))
    return tensor