import os
import threading
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

login_lock = threading.Lock()

# 获取 .env 文件中定义的执行间隔
DAEMON_EXEC_INTERVAL = int(os.getenv("DAEMON_EXEC_INTERVAL", 20))


# 定义定时任务函数，根据 .env 文件中的配置设置执行间隔
@schedule.repeat(schedule.every(DAEMON_EXEC_INTERVAL).seconds)
def run_login_script():
    if not login_lock.acquire(blocking=False):
        logger.warning("daemon: 上一个任务还未完成，跳过本次执行")
        return
    try:
        if login.is_online():
            logger.info("daemon: 网络连接正常，无需进行登录")
        else:
            logger.info(f"daemon: 准备进行登录")
            login.main()
    finally:
        login_lock.release()


def main():
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    exit(main())
