# csust-login-crack

`csust-login-crack` 是一个用于长沙理工大学校园网登录的 Python 项目。本项目适配 2025 年上半年学校的新登录系统。

## 环境要求

- 安装相关依赖：
  ```bash
  pip install -r requirements.txt
  ```

## 使用方法

### 1. 配置环境变量

你需要配置以下环境变量：

- `CSUST_USERNAME`: 你的校园网账号
- `CSUST_PASSWORD`: 你的校园网密码

可以使用`.env`文件来配置环境变量

### 2. 启动脚本

运行主脚本 `login.py` 来开始自动登录过程：

```bash
python login.py
```

## 配置说明

### 定时模式

在启用 CNN 验证码识别的基础上，还需额外配置环境变量：

- `DAEMON_EXEC_INTERVAL`：守护进程定时执行主脚本的间隔（单位为秒，默认为 `20`）。

配置后，运行守护进程 `daemon.py` 并保持后台运行即可定时检查登录状态并自动尝试登录。

```bash
python daemon.py
```

> \[!NOTE]
>
> 学校登录系统的验证码框是个摆设，实际上可以直接跳过

## ~~工作原理~~

~~项目使用基于 CNN 的机器学习模型（训练代码见[csust-captcha-CNN](https://github.com/zHElEARN/csust-captcha-CNN)）来自动识别校园网登录验证码，主要流程包括：~~

~~1. 自动获取网络连接状态~~
~~2. 获取登录页面参数~~
~~3. 验证码识别与校验~~
~~4. 自动提交登录请求~~
