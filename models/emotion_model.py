import logging
import os
from typing import Optional, Tuple

import torch

logger = logging.getLogger(__name__)


class EmotionModel:
    """Wraps a pretrained EmoNet model for valence/arousal prediction."""

    def __init__(self, model_path: str, device: Optional[torch.device] = None, n_expression: int = 8):
        """
        Args:
            model_path: Path to a EmoNet weights file (.pth/.pt).
            device: Optional torch.device. Defaults to CUDA if available.
            n_expression: Number of discrete expression classes the model was trained on.
        """
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = device
        logger.info("Initializing EmotionModel on device: %s", self.device)

        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        logger.info("Loading EmoNet model weights from %s", model_path)
        checkpoint = torch.load(model_path, map_location=self.device)

        state_dict = checkpoint["state_dict"] if isinstance(checkpoint, dict) and "state_dict" in checkpoint else checkpoint

        # EmoNet definition is expected to be provided by the external emonet package.
        # The class is imported lazily here to make it configurable by the user environment.
        from emonet import EmoNet  # type: ignore

        self.model = EmoNet(n_expression=n_expression).to(self.device)
        self.model.load_state_dict(state_dict, strict=False)
        self.model.eval()
        logger.info("EmoNet model loaded and ready for prediction.")

    def predict(self, face_tensor: torch.Tensor) -> Tuple[float, float]:
        """
        Run inference on a single face tensor.

        Args:
            face_tensor: Preprocessed face image tensor with shape (C, H, W) or (1, C, H, W).

        Returns:
            (valence, arousal) tuple.
        """
        if face_tensor.ndim == 3:
            face_tensor = face_tensor.unsqueeze(0)

        face_tensor = face_tensor.to(self.device)
        with torch.no_grad():
            output = self.model(face_tensor)

        if isinstance(output, dict):
            valence = float(output["valence"].view(-1)[0].item())
            arousal = float(output["arousal"].view(-1)[0].item())
        else:
            valence = float(output[0, 0].item())
            arousal = float(output[0, 1].item())

        logger.debug("Predicted valence=%.3f, arousal=%.3f", valence, arousal)
        return valence, arousal