# SmolagentAI 沙盒环境

这是一个基于Docker的安全沙盒环境，用于安全地运行基于smolagents框架的AI智能体代码。该项目提供了一个隔离的执行环境，确保AI代码在受控条件下运行。

## 项目结构

```
.
├── agent_code.py          # 智能体示例代码
├── docker-sandbox/        # Docker沙盒环境
│   ├── Dockerfile        # Docker镜像构建文件
│   └── sandbox_main.py   # 沙盒运行主程序
└── run_in_sandbox.bat    # Windows下运行沙盒的脚本
```

## 环境要求

- Docker Desktop
- Python 3.x
- smolagents库

## 安装步骤

1. 克隆本项目到本地
2. 确保已安装Docker Desktop并运行
3. 在项目根目录下安装依赖：
   ```bash
   pip install smolagents[openai]
   ```

## 使用说明

### 1. 编写智能体代码

在`agent_code.py`中编写你的智能体代码。示例代码展示了如何使用smolagents创建一个基本的智能体：

```python
from smolagents import CodeAgent, OpenAIServerModel

# 初始化模型和智能体
amodel = OpenAIServerModel(
    model_id="deepseek/deepseek-chat-v3-0324:free",
    api_base="https://openrouter.ai/api/v1",
    api_key="your-api-key"
)
agent = CodeAgent(model=amodel, tools=[])

# 运行智能体
response = agent.run("What's the 20th Fibonacci number?")
print(response)
```

### 2. 在沙盒中运行

在Windows环境下，直接运行`run_in_sandbox.bat`脚本：

```bash
./run_in_sandbox.bat
```

这将在Docker容器中安全地执行你的智能体代码。

## 安全特性

- 基于Docker的隔离环境
- 最小化的基础镜像
- 以非root用户运行
- 受限的系统权限

## 注意事项

1. 确保在运行代码前已正确配置API密钥
2. Docker容器会限制智能体的资源使用和系统访问权限
3. 建议在开发阶段进行充分测试，确保代码在沙盒环境中正常运行