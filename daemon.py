import logging
import os
import subprocess
import time
from pathlib import Path

import schedule
from dotenv import load_dotenv

import login

script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)

# 加载 .env 文件
load_dotenv()

# 配置日志
logger = login.logger

# 获取 .env 文件中定义的执行间隔
DAEMON_EXEC_INTERVAL = int(os.getenv("DAEMON_EXEC_INTERVAL", 5))

# 验证码相关环境变量
USE_CNN = os.getenv("USE_CNN", "false").lower() == "true"
CNN_MODEL_PATH = os.getenv("CNN_MODEL_PATH", "")


# 定义定时任务函数，根据 .env 文件中的配置设置执行间隔
@schedule.repeat(schedule.every(DAEMON_EXEC_INTERVAL).minutes)
def run_login_script():
    if login.is_online():
        logger.info("daemon: 网络连接正常，无需进行登录")
    else:
        logger.info(f"daemon: 准备进行登录")
        login.main()


def main():
    if USE_CNN and os.path.exists(CNN_MODEL_PATH):
        schedule.run_all()
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        logger.critical(
            "daemon: 未开启 CNN 识别模式或模型路径设置有误，请检查环境变量配置"
        )
        return 1


if __name__ == "__main__":
    exit(main())
