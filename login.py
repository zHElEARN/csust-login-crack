import os
import re
import json
import requests
import tempfile
import logging
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("login.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# 条件导入大模型相关库
if os.getenv("USE_VLM", "false").lower() == "true":
    try:
        from captcha_model import CaptchaModel
    except ImportError:
        logger.warning("无法导入大模型库，将使用手动模式")
        CaptchaModel = None
else:
    CaptchaModel = None


class LoginSession:
    """封装登录流程的会话管理"""

    VLM_MODEL_PATH = os.getenv("VLM_MODEL_PATH", "")
    VLM_MAX_RETRY = int(os.getenv("VLM_MAX_RETRY", 5))  # 默认重试5次

    def __init__(self) -> None:
        self.session = requests.Session()
        self.captcha_model: Optional[Any] = None
        self.retry_count = 0
        self._initialize_captcha_processor()

    def _initialize_captcha_processor(self) -> None:
        """初始化验证码处理器"""
        if CaptchaModel is not None and self.VLM_MODEL_PATH:
            try:
                self.captcha_model = CaptchaModel(self.VLM_MODEL_PATH)
                logger.info("视觉大模型验证码处理器已启用")
            except Exception as e:
                logger.error(f"大模型初始化失败: {str(e)}")
                raise

    def _get_captcha_image(self) -> bytes:
        """获取验证码图片二进制数据"""
        try:
            response = self.session.get(
                "https://login.csust.edu.cn:802/eportal/captcha",
                stream=True,
                timeout=10,
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"获取验证码失败: {e}")
            raise RuntimeError("无法获取验证码")

    def _handle_vlm_captcha(self, image_data: bytes) -> str:
        """大模型处理验证码"""
        if self.VLM_MAX_RETRY >= 0 and self.retry_count >= self.VLM_MAX_RETRY:
            raise RuntimeError(f"超过最大重试次数 {self.VLM_MAX_RETRY}")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(image_data)
            temp_path = Path(f.name)

        try:
            raw, cleaned = self.captcha_model.process_image(temp_path)  # type: ignore
            logger.debug(f"原始识别结果: {raw} -> 清洗后: {cleaned}")

            if len(cleaned) == 4:
                logger.info(f"验证码识别结果: {cleaned}")
                return cleaned
            raise ValueError("无效的验证码格式")
        finally:
            temp_path.unlink()
            self.retry_count += 1

    def _handle_manual_captcha(self, image_data: bytes) -> str:
        """手动输入处理验证码"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(image_data)
            temp_path = Path(f.name)

        try:
            os.startfile(temp_path)
            while True:
                captcha = input("请输入验证码: ").strip()
                if len(captcha) == 4 and captcha.isalnum():
                    return captcha.upper()
                print("验证码必须为4位字母数字组合，请重新输入")
        finally:
            temp_path.unlink()

    def get_and_process_captcha(self) -> str:
        """获取并处理验证码"""
        image_data = self._get_captcha_image()

        if self.captcha_model:
            return self._handle_vlm_captcha(image_data)
        return self._handle_manual_captcha(image_data)

    def verify_captcha(self, captcha: str) -> bool:
        """验证码校验"""
        params = {
            "callback": "dr1003",
            "captcha": captcha,
            "jsVersion": "4.2.1",
            "v": "5470",
            "lang": "zh",
        }

        try:
            response = self.session.get(
                "https://login.csust.edu.cn:802/eportal/portal/captcha/check",
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            data = self._parse_callback(response.text)
        except (requests.RequestException, ValueError) as e:
            logger.error(f"验证码校验失败: {e}")
            return False

        return data.get("result") == 1

    def login(
        self, username: str, password: str, location_params: Dict[str, str]
    ) -> Tuple[bool, str]:
        """执行登录操作"""
        params = {
            "callback": "dr1004",
            "login_method": 1,
            "user_account": f",0,{username}",
            "user_password": password,
            "wlan_user_ip": location_params.get("wlanuserip", ""),
            "wlan_user_mac": location_params.get("wlanusermac", ""),
            "wlan_ac_ip": location_params.get("wlanacip", ""),
            "wlan_ac_name": location_params.get("wlanacname", ""),
            "jsVersion": "4.2.1",
            "terminal_type": 1,
            "lang": "zh",
            "v": 3333,
        }

        try:
            response = self.session.get(
                "https://login.csust.edu.cn:802/eportal/portal/login",
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            data = self._parse_callback(response.text)
        except (requests.RequestException, ValueError) as e:
            logger.error(f"登录请求失败: {e}")
            return False, "请求失败"

        return (data.get("result") == 1, data.get("msg", "未知错误"))

    @staticmethod
    def _parse_callback(text: str) -> Dict[str, Any]:
        """解析回调函数响应"""
        match = re.match(r"^\w+\((.*)\);$", text.strip())
        if not match:
            raise ValueError("无效的响应格式")
        return json.loads(match.group(1))


def get_location_parameters() -> Dict[str, str]:
    """获取重定向地址中的查询参数"""
    try:
        response = requests.get("http://10.10.10.10/", allow_redirects=False, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"获取定位参数失败: {e}")
        return {}

    location = response.headers.get("Location", "")
    if not location:
        return {}

    parsed = urlparse(location)
    return {k: v[0] for k, v in parse_qs(parsed.query).items()}


def main() -> int:
    try:
        username = os.getenv("CSUST_USERNAME")
        password = os.getenv("CSUST_PASSWORD")

        if not username or not password:
            raise ValueError("请设置CSUST_USERNAME和CSUST_PASSWORD环境变量")

        while True:
            location_params = get_location_parameters()
            if not location_params:
                raise RuntimeError("无法获取网络位置参数")

            session = LoginSession()

            # 验证码处理循环
            while True:
                try:
                    captcha = session.get_and_process_captcha()
                    if session.verify_captcha(captcha):
                        logger.info("验证码校验成功")
                        break
                    logger.warning("验证码校验失败，重新获取...")
                except RuntimeError as e:
                    logger.error(f"严重错误: {str(e)}")
                    return 1

            # 登录流程
            success, msg = session.login(username, password, location_params)
            if success:
                logger.info("校园网登录成功！")
                return 0

            # 处理需要重新登录的情况
            if "login again" in msg.lower():
                logger.warning("检测到需要重新登录，重启登录流程...")
                continue  # 继续外部循环

            logger.error(f"登录失败: {msg}")
            return 1

    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
