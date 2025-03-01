import io
import logging
from typing import Any
from PIL import Image
import torch
from .model_config import Config, idx2char
from .model_data_loader import test_transform
from .model import CaptchaModel

logger = logging.getLogger(__name__)


class CNNPredictor:
    """CNN验证码识别器"""

    def __init__(self, model_path: str):
        """初始化识别器

        Args:
            model_path: 模型文件路径
        """
        self.device = Config.device
        self.model = self._load_model(model_path)
        self.transform = test_transform
        self.model.eval()
        logger.info(f"CNN验证码处理器已初始化，使用设备: {self.device}")

    def _load_model(self, model_path: str) -> Any:
        """加载训练好的模型"""
        try:
            model = CaptchaModel().to(self.device)
            model.load_state_dict(torch.load(model_path, map_location=self.device))
            return model
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            raise RuntimeError("无法加载CNN模型") from e

    def predict(self, image_data: bytes) -> str:
        """执行验证码预测

        Args:
            image_data: 验证码图片的二进制数据

        Returns:
            识别后的验证码字符串（大写）
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(image_tensor)
                preds = torch.stack([output.argmax(dim=1) for output in outputs], dim=1)
                raw = "".join([idx2char[idx.item()] for idx in preds[0]])
                cleaned = raw.strip().upper()

                if len(cleaned) == 4 and cleaned.isalnum():
                    logger.debug(f"验证码识别结果: {cleaned}")
                    return cleaned
                raise ValueError(f"无效的验证码格式: {cleaned}")
        except Exception as e:
            logger.error(f"验证码识别失败: {str(e)}")
            raise RuntimeError("验证码识别失败") from e
