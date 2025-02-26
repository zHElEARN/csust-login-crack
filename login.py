import os
import re
import json
import requests
import tempfile
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


def get_location_parameters() -> Dict[str, str]:
    """获取重定向地址中的查询参数"""
    try:
        response: requests.Response = requests.get(
            "http://10.10.10.10/", allow_redirects=False
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"请求定位参数失败: {e}")

    location: Optional[str] = response.headers.get("Location", "")
    if not location:
        return {}

    parsed = urlparse(location)
    return {k: v[0] for k, v in parse_qs(parsed.query).items()}


def parse_callback_response(text: str) -> Dict[str, Any]:
    """解析回调函数响应为JSON对象"""
    match: Optional[re.Match] = re.match(r"^\w+\((.*)\);$", text.strip())
    if not match:
        raise ValueError("无效的响应格式")
    return json.loads(match.group(1))


class LoginSession:
    """封装登录流程的会话管理"""

    def __init__(self) -> None:
        self.session: requests.Session = requests.Session()
        self.captcha: str = ""

    def get_captcha(self) -> None:
        """获取并显示验证码"""
        try:
            response: requests.Response = self.session.get(
                "https://login.csust.edu.cn:802/eportal/captcha", stream=True
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"获取验证码失败: {e}")

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
            temp_path: str = f.name

        try:
            os.startfile(temp_path)
            self.captcha = input("请输入验证码: ")
        finally:
            os.unlink(temp_path)

    def verify_captcha(self) -> bool:
        """验证码校验"""
        params: Dict[str, str | int] = {
            "callback": "dr1003",
            "captcha": self.captcha,
            "jsVersion": "4.2.1",
            "v": "5470",
            "lang": "zh",
        }

        try:
            response: requests.Response = self.session.get(
                "https://login.csust.edu.cn:802/eportal/portal/captcha/check",
                params=params,
            )
            response.raise_for_status()
            data: Dict[str, Any] = parse_callback_response(response.text)
        except (requests.RequestException, ValueError) as e:
            raise RuntimeError(f"验证码校验失败: {e}")

        if data.get("result") != 1:
            raise RuntimeError(data.get("msg", "未知验证码错误"))
        return True

    def login(
        self, username: str, password: str, location_params: Dict[str, str]
    ) -> bool:
        """执行登录操作"""
        params: Dict[str, str | int] = {
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
            response: requests.Response = self.session.get(
                "https://login.csust.edu.cn:802/eportal/portal/login", params=params
            )
            response.raise_for_status()
            data: Dict[str, Any] = parse_callback_response(response.text)
        except (requests.RequestException, ValueError) as e:
            raise RuntimeError(f"登录请求失败: {e}")

        if data.get("result") != 1:
            raise RuntimeError(data.get("msg", "未知登录错误"))
        return True


def main() -> int:
    try:
        # 从环境变量中获取用户名和密码
        username: Optional[str] = os.getenv("CSUST_USERNAME")
        password: Optional[str] = os.getenv("CSUST_PASSWORD")

        if not username or not password:
            raise RuntimeError("缺少用户名或密码环境变量")

        # 获取定位参数
        location_params: Dict[str, str] = get_location_parameters()

        # 初始化登录会话
        login_session: LoginSession = LoginSession()

        # 获取并验证验证码
        login_session.get_captcha()
        login_session.verify_captcha()

        # 执行登录
        login_session.login(
            username=username,
            password=password,
            location_params=location_params,
        )

        print("校园网登录成功！")
        return 0

    except Exception as e:
        print(f"程序执行失败: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
