# csust-login-crack

`csust-login-crack` 是一个用户长沙理工大学校园网登录的 Python 项目。本项目实现了自动化登录和验证码识别功能，支持视觉大模型（VLM）和手动输入两种验证码处理方式。

## 环境要求

- 安装相关依赖：
  ```bash
  pip install -r requirements.txt
  ```
- 如果要使用视觉大模型则还需要：
  ```bash
  pip install -r requirements-vlm.txt
  ```

## 使用方法

### 1. 配置环境变量

你需要配置以下环境变量：

- `CSUST_USERNAME`: 你的校园网账号。
- `CSUST_PASSWORD`: 你的校园网密码。
- `USE_VLM`: 是否启用视觉大模型进行验证码识别（可选，默认为`false`）。如果启用，则需要配置`VLM_MODEL_PATH`。
- `VLM_MODEL_PATH`: 视觉大模型的路径（可选，只有在`USE_VLM=true`时有效）。
- `VLM_MAX_RETRY`: 最大重试次数（可选，默认为`5`）。

可以使用`.env`来配置环境变量

### 2. 启动脚本

运行主脚本 `login.py` 来开始自动登录过程：

```bash
python login.py
```

## 配置说明

### 启用视觉大模型（VLM）

如果你希望使用视觉大模型来自动识别验证码，需要满足以下条件：

- 仅支持 Qwen 视觉大模型
- 下载相应的视觉大模型
- 设置 `USE_VLM=true` 和 `VLM_MODEL_PATH` 环境变量指向该模型文件。

如果无法导入大模型，将自动退回到手动输入验证码模式。

### 手动输入验证码

如果没有启用视觉大模型，脚本会自动打开验证码图片，并要求你手动输入验证码。
