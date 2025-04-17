# SmolagentAI 沙盒环境

## 项目简介

这是一个用于运行smolagents智能体的Docker沙箱环境。该项目提供了一个安全的容器化环境，让您可以在隔离的环境中运行和测试智能体代码。

## 项目结构

```
.
├── agent_code.py          # 智能体示例代码
├── docker-sandbox/        # Docker沙盒环境
│   ├── Dockerfile        # Docker镜像构建文件
│   └── sandbox_main.py   # 沙盒运行主程序
├── run_in_sandbox.bat    # Windows下运行沙盒的脚本
├── run_in_sandbox.sh     # Linux/Mac下运行沙盒的脚本
└── .env                  # 环境变量配置文件（需要自行创建）
```

## 环境要求

- Docker Desktop
- Python 3.x
- smolagents库

## 环境配置

1. 首先复制`env.example`文件并重命名为`.env`
2. 在`.env`文件中配置以下环境变量：

```
OPENAI_TOKEN="Your openrouter.ai token"    # 设置您的OpenRouter API token
MODEL_NAME="deepseek/deepseek-chat-v3-0324:free"  # 使用的模型名称
PROXY="http://ip:port"                    # 代理服务器地址（如需要）
PROXY_IN_DOCKER="http://host.docker.internal:port"  # Docker容器内使用的代理地址
```

注意：
- 请确保设置正确的OpenRouter API token
- 如果需要使用代理，请正确配置PROXY和PROXY_IN_DOCKER地址
- Windows环境下Docker容器访问宿主机代理，需要使用`host.docker.internal`作为主机名

## 使用说明

### Windows环境

1. 确保Docker Desktop已启动
2. 双击运行`run_in_sandbox.bat`脚本

### Linux/Mac环境

1. 确保Docker服务已启动
2. 执行以下命令：
```bash
chmod +x run_in_sandbox.sh
./run_in_sandbox.sh
```

## 注意事项

1. 首次运行时会自动构建Docker镜像，可能需要一些时间
2. 确保环境变量配置正确，特别是API token和代理设置
3. 如遇到网络问题，请检查代理配置是否正确
4. 代码修改后需要重新运行脚本以更新容器中的代码