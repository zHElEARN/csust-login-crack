# csust-login-crack

`csust-login-crack` 是一个用于长沙理工大学校园网登录的 Python 项目。本项目实现了自动化登录和验证码识别功能，支持基于 CNN 的验证码识别模型和手动输入两种验证码处理方式。

## 环境要求

- 安装相关依赖：
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126 # replace with your cuda version
  pip install -r requirements.txt
  ```

## 使用方法

### 1. 配置环境变量

你需要配置以下环境变量：

- `CSUST_USERNAME`: 你的校园网账号
- `CSUST_PASSWORD`: 你的校园网密码
- `USE_CNN`: 是否启用 CNN 模型进行验证码识别（可选，默认为`false`）。如果启用，则需要配置`CNN_MODEL_PATH`
- `CNN_MODEL_PATH`: CNN 模型文件的路径（可选，只有在`USE_CNN=true`时有效）
- `CNN_MAX_RETRY`: 最大重试次数（可选，默认为`5`）

可以使用`.env`文件来配置环境变量

### 2. 启动脚本

运行主脚本 `login.py` 来开始自动登录过程：

```bash
python login.py
```

## 配置说明

### 启用 CNN 验证码识别

如果希望使用基于 CNN 的验证码识别模型：

1. 下载训练好的 CNN 模型文件（项目地址：[csust-captcha-CNN](https://github.com/zHElEARN/csust-captcha-CNN)）
2. 设置 `USE_CNN=true`
3. 设置 `CNN_MODEL_PATH` 环境变量指向模型文件

### 手动输入验证码

如果没有启用 CNN 模型，脚本会自动打开验证码图片，并要求手动输入验证码。验证码应为 4 位字母数字组合，不区分大小写。

###  定时模式

在启用 CNN 验证码识别的基础上，还需额外配置环境变量：

- `DAEMON_EXEC_INTERVAL`：守护进程定时执行主脚本的间隔（单位为分钟，默认为 `5`）。

配置后，运行守护进程 `daemon.py` 并保持后台运行即可定时检查登录状态并自动尝试登录。

```bash
python daemon.py
```

## 工作原理

项目使用基于 CNN 的机器学习模型（训练代码见[csust-captcha-CNN](https://github.com/zHElEARN/csust-captcha-CNN)）来自动识别校园网登录验证码，主要流程包括：

1. 自动获取网络连接状态
2. 获取登录页面参数
3. 验证码识别与校验
4. 自动提交登录请求
