from smolagents import ToolCollection, CodeAgent
from smolagents import OpenAIServerModel
import os

# 设置HTTP代理
os.environ['HTTP_PROXY'] = os.environ["PROXY"]
os.environ['HTTPS_PROXY'] = os.environ["PROXY"]

amodel = OpenAIServerModel(
    model_id=os.environ["MODEL_NAME"],
    api_base="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENAI_TOKEN"],
)


agent = CodeAgent(
    tools=[], 
    model=amodel,
    additional_authorized_imports=["pandas","openpyxl"],
    add_base_tools=False
)

# agent.run("""
# 你的运行环境中有这些包：
# pandas openpyxl
# 请根据需要导入相应的包
# 输入输入文件的交换目录是/workdir，请给程序的输入输出文件名添加这个目录路径
# 帮我写一个python程序完成这个目标：
# 创建一个excel模板，搜集广东省21个地市的无线网络指标：接通率，掉话率，切换成功率，要求每个地市给出填表人姓名、联系方式。表格的字段使用中文，在表格最后一行添加一个全省汇总行。
# """)

agent.run("""
你的运行环境中有这些包：
pandas openpyxl
请根据需要导入相应的包
文件的交换目录是/workdir/output，请给程序的输入输出文件名添加这个目录路径
帮我写一个python程序完成这个目标：
读取工作目录下的'广东省无线网络指标模版.xlsx'文件，将文件拆分成21个文件。每个文件包含输入文件中的1个地市的无线网络指标以及全省汇总行。
""")