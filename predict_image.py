import argparse
import glob
import json
import logging
import os
from pathlib import Path
from typing import Iterable, List, Dict

import cv2
import numpy as np

from models.emotion_model import EmotionModel
from utils.face_utils import align_face, crop_face, detect_faces, prepare_face_tensor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def iter_image_files(path: str) -> Iterable[str]:
    """从可能是文件或目录的路径中生成图像文件。"""
    if os.path.isdir(path):
        patterns = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.tif"]
        for pattern in patterns:
            yield from glob.glob(os.path.join(path, pattern))
    elif os.path.isfile(path):
        yield path
    else:
        logger.error("提供的图像路径无效：%s", path)


def process_image(image_path: str, model: EmotionModel, output_dir: str) -> None:
    """检测图像中的面部并将 EmoNet 预测保存为 JSON。"""
    image_name = os.path.basename(image_path)
    faces_data = []

    faces = detect_faces(image_path)
    if len(faces) == 0:
        logger.info("在 %s 中未检测到面部，跳过。", image_name)
        return

    orig_image = cv2.imread(image_path)
    for idx, (bbox, landmarks) in enumerate(faces, start=1):
        aligned_image = align_face(orig_image, landmarks)
        face_img = crop_face(aligned_image, bbox)
        face_tensor = prepare_face_tensor(face_img)
        prediction = model.predict(face_tensor)

        faces_data.append(
            {
                "id": idx,
                "bbox": bbox,
                "emotion_class": prediction["emotion_class"],
                "emotion_name": prediction["emotion_name"],
                "valence": round(prediction["valence"], 4),
                "arousal": round(prediction["arousal"], 4),
            }
        )
        logger.info(
            "图像 %s - 面部 %d：%s (valence=%.3f, arousal=%.3f)",
            image_name,
            idx,
            prediction["emotion_name"],
            prediction["valence"],
            prediction["arousal"],
        )

    result = {"image": image_name, "faces": faces_data}

    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, os.path.splitext(image_name)[0] + ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    logger.info("结果保存到 %s", json_path)


def load_video(video_path: str) -> List[np.ndarray]:
    """使用 OpenCV 加载视频并返回所有帧。"""
    if not os.path.isfile(video_path):
        if os.path.isdir(video_path):
            raise ValueError(
                f"'{video_path}' 是一个目录，请指定具体的视频文件。\n"
                f"目录中的视频文件：\n" +
                "\n".join([f"  - {f}" for f in os.listdir(video_path) 
                          if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))])
            )
        else:
            raise FileNotFoundError(f"视频文件不存在：{video_path}")
    
    video_capture = cv2.VideoCapture(video_path)
    
    if not video_capture.isOpened():
        raise ValueError(f"无法打开视频文件：{video_path}")
    
    frames = []
    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break
        frames.append(frame)
    
    video_capture.release()
    logger.info("从 %s 加载了 %d 帧", video_path, len(frames))
    return frames


def plot_valence_arousal(valence: float, arousal: float, size: int = 512) -> np.ndarray:
    """绘制效价-唤醒度的二维情绪空间圆盘图。"""
    circumplex_path = Path(__file__).parent / "emonet/images/circumplex.png"
    
    if circumplex_path.exists():
        circumplex = cv2.imread(str(circumplex_path))
        circumplex = cv2.resize(circumplex, (size, size))
    else:
        # 如果没有circumplex图像，创建一个简单的背景
        circumplex = np.ones((size, size, 3), dtype=np.uint8) * 240
        # 绘制坐标轴
        cv2.line(circumplex, (size//2, 0), (size//2, size), (200, 200, 200), 2)
        cv2.line(circumplex, (0, size//2), (size, size//2), (200, 200, 200), 2)
        cv2.putText(circumplex, "Valence", (size-120, size//2-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        cv2.putText(circumplex, "Arousal", (size//2+10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
    
    # 将 valence 和 arousal 从 [-1, 1] 映射到 [0, size]
    # arousal 轴向上，所以需要反转
    position = (
        int((valence + 1.0) / 2.0 * size),
        int((1.0 - arousal) / 2.0 * size)
    )
    
    cv2.circle(circumplex, position, 16, (0, 0, 255), -1)
    
    return circumplex


def visualize_frame(frame: np.ndarray, bbox: List[int], prediction: Dict[str, any], 
                   face_crop: np.ndarray, font_scale: float = 1.5) -> np.ndarray:
    """为视频帧创建可视化，包括检测框、情感标签和效价-唤醒度图。"""
    frame_vis = frame.copy()
    
    # 绘制边界框
    cv2.rectangle(frame_vis, (bbox[0], bbox[1]), 
                 (bbox[0] + bbox[2], bbox[1] + bbox[3]), (255, 0, 0), 4)
    
    # 添加情感标签
    label = f"{prediction['emotion_name']}"
    label_pos = ((bbox[0] + bbox[2]) // 2 - 50, bbox[1] - 10)
    cv2.putText(frame_vis, label, label_pos, cv2.FONT_HERSHEY_SIMPLEX, 
               font_scale, (255, 0, 0), 2, cv2.LINE_AA)
    
    # 创建组合可视化
    h, w = frame_vis.shape[:2]
    panel_width = h // 2
    
    visualization = np.zeros((h, w + panel_width, 3), dtype=np.uint8)
    visualization[:, :w, :] = frame_vis
    
    # 调整面部裁剪图像大小并放置
    face_crop_resized = cv2.resize(face_crop, (panel_width, panel_width))
    visualization[:panel_width, w:, :] = face_crop_resized
    
    # 绘制效价-唤醒度图
    circumplex = plot_valence_arousal(prediction["valence"], prediction["arousal"], panel_width)
    visualization[panel_width:, w:, :] = circumplex
    
    return visualization


def process_video(video_path: str, model: EmotionModel, output_path: str) -> None:
    """处理视频文件，检测面部情绪并生成可视化视频。"""
    logger.info("开始处理视频：%s", video_path)
    
    frames = load_video(video_path)
    if not frames:
        logger.error("未能从视频中加载任何帧")
        return
    
    visualization_frames = []
    frame_count = len(frames)
    faces_detected = 0
    
    for i, frame in enumerate(frames):
        # 将帧保存为临时图像以便使用 face_alignment 检测
        temp_image_path = "temp_frame.jpg"
        
        try:
            cv2.imwrite(temp_image_path, frame)
            
            faces = detect_faces(temp_image_path)
            
            if faces and len(faces) > 0:
                # 只处理第一个检测到的面部
                bbox, landmarks = faces[0]
                
                aligned_image = align_face(frame, landmarks)
                face_crop = crop_face(aligned_image, bbox)
                face_tensor = prepare_face_tensor(face_crop)
                prediction = model.predict(face_tensor)
                
                # 创建可视化
                vis_frame = visualize_frame(frame, bbox, prediction, face_crop)
                visualization_frames.append(vis_frame)
                faces_detected += 1
            else:
                # 没有检测到面部，创建简单的可视化
                h, w = frame.shape[:2]
                visualization = np.zeros((h, w + h // 2, 3), dtype=np.uint8)
                visualization[:, :w, :] = frame
                visualization_frames.append(visualization)
        
        except Exception as e:
            logger.warning("处理第 %d 帧时出错：%s", i + 1, e)
            # 出错时也创建简单的可视化
            h, w = frame.shape[:2]
            visualization = np.zeros((h, w + h // 2, 3), dtype=np.uint8)
            visualization[:, :w, :] = frame
            visualization_frames.append(visualization)
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
        
        if (i + 1) % 100 == 0 or (i + 1) == frame_count:
            logger.info("已处理 %d/%d 帧 (检测到面部: %d)", i + 1, frame_count, faces_detected)
    
    # 保存输出视频
    if visualization_frames:
        h, w = visualization_frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 24.0, (w, h))
        
        for frame in visualization_frames:
            out.write(frame)
        
        out.release()
        logger.info("视频已保存到：%s", output_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="使用 EmoNet 模型进行情绪预测（图像或视频模式）"
    )
    parser.add_argument(
        "--images", "-i", 
        help="图像文件或目录的路径（图像模式）"
    )
    parser.add_argument(
        "--video", "-v", 
        help="视频文件的路径（视频模式）"
    )
    parser.add_argument(
        "--model", "-m", 
        required=True, 
        help="EmoNet 模型权重文件的路径"
    )
    parser.add_argument(
        "--output_dir",
        "-o",
        default="results",
        help="保存输出文件的目录（图像模式）",
    )
    parser.add_argument(
        "--output_video",
        help="输出视频文件的路径（视频模式，默认：output.mp4）",
    )
    parser.add_argument(
        "--expressions",
        "-e",
        type=int,
        default=8,
        choices=[5, 8],
        help="EmoNet 模型的情感类别数量 (5 或 8)",
    )

    args = parser.parse_args()

    # 验证输入参数
    if not args.images and not args.video:
        parser.error("必须指定 --images 或 --video 参数之一")
    
    if args.images and args.video:
        parser.error("不能同时指定 --images 和 --video 参数")

    # 加载模型
    emo_model = EmotionModel(model_path=args.model, n_expression=args.expressions)

    # 处理图像模式
    if args.images:
        logger.info("运行图像模式")
        for image_file in iter_image_files(args.images):
            try:
                process_image(image_file, emo_model, args.output_dir)
            except Exception as exc:  # noqa: BLE001
                logger.error("处理 %s 失败：%s", image_file, exc)
    
    # 处理视频模式
    elif args.video:
        logger.info("运行视频模式")
        output_video = args.output_video or "output.mp4"
        try:
            process_video(args.video, emo_model, output_video)
        except Exception as exc:  # noqa: BLE001
            logger.error("处理视频失败：%s", exc)


if __name__ == "__main__":
    main()