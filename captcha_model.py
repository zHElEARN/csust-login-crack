# captcha_model.py
import re
import logging
from pathlib import Path
from typing import Optional, Tuple
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

logger = logging.getLogger(__name__)


class CaptchaModel:
    """视觉大模型验证码处理器"""

    def __init__(self, model_path: str):
        self.model: Optional[Qwen2_5_VLForConditionalGeneration] = None
        self.processor: Optional[AutoProcessor] = None
        self._initialize_model(model_path)

    def _initialize_model(self, model_path: str) -> None:
        """初始化大模型"""
        try:
            logger.info(f"Initializing Qwen model from {model_path}...")
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_path, torch_dtype="auto", device_map="auto"
            )
            self.processor = AutoProcessor.from_pretrained(model_path)
            logger.info("Model initialized successfully")
        except Exception as e:
            logger.error(f"模型初始化失败: {str(e)}")
            raise

    def process_image(self, image_path: Path) -> Tuple[str, str]:
        """
        处理验证码图片
        返回: (原始输出, 清洗后的验证码)
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": """你是一个专业的验证码识别系统，请严格遵循以下规则：
1. 专注于分析图像中的4位字母数字组合
2. 字符可能包含字母或数字
3. 优先识别最清晰、最完整的字符组合
4. 特别注意相似字符的区分
5. 必须输出唯一结果，格式为字母和数字组成的4位字符串
6. 禁止添加任何解释、空格或标点""",
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": f"file://{image_path.absolute()}"},
                        {
                            "type": "text",
                            "text": "请直接输出图片中的完整验证码，不要任何额外内容。",
                        },
                    ],
                },
            ]

            # 处理流程
            text = self.processor.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            image_inputs, _ = process_vision_info(messages)
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                padding=True,
                return_tensors="pt",
            ).to("cuda")

            # 生成结果
            generated_ids = self.model.generate(**inputs, max_new_tokens=128)
            generated_ids_trimmed = [
                out_ids[len(in_ids) :]
                for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            raw_output = self.processor.batch_decode(
                generated_ids_trimmed,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            )[0]

            # 清洗结果
            cleaned = self._clean_output(raw_output.strip())
            return raw_output, cleaned

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return ("ERROR", "")

    @staticmethod
    def _clean_output(text: str) -> str:
        """清洗输出结果"""
        cleaned = re.sub(r"[^a-zA-Z0-9]", "", text)
        return cleaned[:4].upper() if len(cleaned) >= 4 else ""
