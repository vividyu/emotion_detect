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
    """Yield image files from a path that may be a file or directory."""
    if os.path.isdir(path):
        patterns = ["*.jpg", "*.jpeg", "*.png", "*.bmp"]
        for pattern in patterns:
            yield from glob.glob(os.path.join(path, pattern))
    elif os.path.isfile(path):
        yield path
    else:
        logger.error("Provided image path is invalid: %s", path)


def process_image(image_path: str, model: EmotionModel, output_dir: str) -> None:
    """Detect faces in an image and save EmoNet predictions as JSON."""
    image_name = os.path.basename(image_path)
    faces_data = []

    faces = detect_faces(image_path)
    if len(faces) == 0:
        logger.info("No face detected in %s, skipping.", image_name)
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
            "Image %s - Face %d: valence=%.3f, arousal=%.3f",
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

    logger.info("Results saved to %s", json_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run EmoNet emotion prediction on images")
    parser.add_argument("--images", "-i", required=True, help="Path to an image file or directory")
    parser.add_argument("--model", "-m", required=True, help="Path to the EmoNet model weights file")
    parser.add_argument(
        "--output_dir",
        "-o",
        default="results",
        help="Directory to save output JSON files",
    )
    parser.add_argument(
        "--expressions",
        "-e",
        type=int,
        default=8,
        help="Number of discrete expression classes the EmoNet weights expect",
    )

    args = parser.parse_args()

    emo_model = EmotionModel(model_path=args.model, n_expression=args.expressions)

    for image_file in iter_image_files(args.images):
        try:
            process_image(image_file, emo_model, args.output_dir)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to process %s: %s", image_file, exc)


if __name__ == "__main__":
    main()