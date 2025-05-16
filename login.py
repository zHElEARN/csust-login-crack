import json
import logging
import os
import re
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.parse import parse_qs, urlparse

import requests
import urllib3
from dotenv import load_dotenv

script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)

# 加载环境变量
load_dotenv()


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        TimedRotatingFileHandler(
            filename=os.path.join(log_dir, "login.log"),
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
            utc=False,
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


proxies = {"http": None, "https": None}


# 检查是否联网的函数
def is_online() -> bool:
    """检测当前网络状态"""
    try:
        # 使用generate_204页面检测是否联网
        response = requests.get(
            "http://connect.rom.miui.com/generate_204",
            proxies=proxies,
            timeout=5,
        )
        return response.status_code == 204
    except requests.RequestException:
        return False


class LoginSession:
    def __init__(self) -> None:
        self._session = requests.Session()

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
            response = self._session.get(
                "https://login.csust.edu.cn:802/eportal/portal/login",
                params=params,
                proxies=proxies,
                verify=False,
                timeout=9,
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

    @staticmethod
    def get_location_parameters() -> Dict[str, str]:
        """获取重定向地址中的查询参数"""
        try:
            response = requests.get(
                "http://10.10.10.10/", allow_redirects=False, proxies=proxies, timeout=6
            )
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

        if is_online():
            logger.info("当前已检测到网络连接，无需登录")
            exit(0)

        while True:
            session = LoginSession()

            location_params = session.get_location_parameters()
            if not location_params:
                raise RuntimeError("无法获取网络位置参数")

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
