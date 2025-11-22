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
    face_alignment.LandmarksType._2D,
    device=_fa_device,
    face_detector="sfd",
)


def detect_faces(image_path: str) -> List[Tuple[List[int], np.ndarray]]:
    """Detect faces and 68-point landmarks in an image.

    Returns a list of tuples (bbox, landmarks) where bbox is [x, y, w, h].
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    logger.info("Detecting faces in image: %s", image_path)
    image = io.imread(image_path)

    output = fa.get_landmarks_from_image(image, return_bboxes=True)
    if output is None:
        logger.warning("No face found in the image.")
        return []

    landmarks_list, _, bbox_array = output
    faces = []
    for i, (landmarks, bbox) in enumerate(zip(landmarks_list, bbox_array)):
        x1, y1, x2, y2 = bbox.astype(int)
        w, h = x2 - x1, y2 - y1
        bbox_dims = [int(x1), int(y1), int(w), int(h)]
        faces.append((bbox_dims, landmarks))
        logger.debug("Face %d: bbox=%s", i + 1, bbox_dims)

    return faces


def align_face(image: np.ndarray, landmarks: np.ndarray, target_size: int = 256) -> np.ndarray:
    """Rotate the image so that the eyes are horizontally aligned."""
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
    """Crop a bounding box from the image and resize to the target size."""
    x, y, w, h = bbox
    ih, iw = image.shape[:2]

    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(iw, x + w), min(ih, y + h)
    face_roi = image[y0:y1, x0:x1]

    if face_roi.size == 0:
        raise ValueError("Face ROI is empty. Check bounding box coordinates.")

    return cv2.resize(face_roi, (target_size, target_size))


def prepare_face_tensor(face_image: np.ndarray) -> torch.Tensor:
    """Convert a cropped face image into a normalized torch tensor."""
    if face_image.ndim == 2:
        face_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2RGB)
    else:
        face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

    face_image = face_image.astype(np.float32) / 255.0
    tensor = torch.from_numpy(face_image.transpose(2, 0, 1))
    return tensor