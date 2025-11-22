import argparse
import glob
import json
import logging
import os
from typing import Iterable

from models.emotion_model import EmotionModel
from utils.face_utils import align_face, crop_face, detect_faces, prepare_face_tensor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def iter_image_files(path: str) -> Iterable[str]:
    """从可能是文件或目录的路径中生成图像文件。"""
    if os.path.isdir(path):
        patterns = ["*.jpg", "*.jpeg", "*.png", "*.bmp"]
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

    import cv2

    orig_image = cv2.imread(image_path)
    for idx, (bbox, landmarks) in enumerate(faces, start=1):
        aligned_image = align_face(orig_image, landmarks)
        face_img = crop_face(aligned_image, bbox)
        face_tensor = prepare_face_tensor(face_img)
        valence, arousal = model.predict(face_tensor)

        faces_data.append(
            {
                "id": idx,
                "bbox": bbox,
                "valence": round(valence, 4),
                "arousal": round(arousal, 4),
            }
        )
        logger.info(
            "图像 %s - 面部 %d：valence=%.3f, arousal=%.3f",
            image_name,
            idx,
            valence,
            arousal,
        )

    result = {"image": image_name, "faces": faces_data}

    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, os.path.splitext(image_name)[0] + ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    logger.info("结果保存到 %s", json_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="在图像上运行 EmoNet 情绪预测")
    parser.add_argument("--images", "-i", required=True, help="图像文件或目录的路径")
    parser.add_argument("--model", "-m", required=True, help="EmoNet 模型权重文件的路径")
    parser.add_argument(
        "--output_dir",
        "-o",
        default="results",
        help="保存输出 JSON 文件的目录",
    )
    parser.add_argument(
        "--expressions",
        "-e",
        type=int,
        default=8,
        help="EmoNet 权重期望的离散表情类别数量",
    )

    args = parser.parse_args()

    emo_model = EmotionModel(model_path=args.model, n_expression=args.expressions)

    for image_file in iter_image_files(args.images):
        try:
            process_image(image_file, emo_model, args.output_dir)
        except Exception as exc:  # noqa: BLE001
            logger.error("处理 %s 失败：%s", image_file, exc)


if __name__ == "__main__":
    main()