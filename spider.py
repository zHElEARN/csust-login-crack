import os
import uuid
import requests
from typing import List


def download_images(output_dir: str, request_count: int) -> List[str]:
    """
    下载指定数量的验证码图片并保存到指定目录
    """
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    saved_files: List[str] = []
    for _ in range(request_count):
        # 请求图片
        url = "https://login.csust.edu.cn:802/eportal/captcha"
        response: requests.Response = requests.get(url)

        # 生成唯一文件名
        file_name: str = f"{uuid.uuid4()}.png"
        file_path: str = os.path.join(output_dir, file_name)

        # 保存图片
        with open(file_path, "wb") as f:
            f.write(response.content)

        # 记录保存的文件路径
        saved_files.append(file_path)
        print(f"已保存图片: {file_path}")

    return saved_files


def main() -> None:
    # 配置参数
    output_dir: str = "outputs"
    request_count: int = 900

    # 下载图片
    saved_files: List[str] = download_images(output_dir, request_count)

    # 输出结果
    print(f"\n所有图片已保存完毕，共保存了 {len(saved_files)} 张图片。")


if __name__ == "__main__":
    main()
