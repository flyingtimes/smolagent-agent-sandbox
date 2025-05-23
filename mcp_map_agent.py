from smolagents import ToolCollection, CodeAgent
from mcp import StdioServerParameters
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
server_parameters = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server_fetch"],
    env={
        "HTTP_PROXY": os.environ["PROXY"],
        "HTTPS_PROXY": os.environ["PROXY"]
    },
)

server_parameters1 = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server_baidu_maps"],
    env={
        "BAIDU_MAPS_API_KEY": "ojLxZsudnK4TAT9Rma8u5VGDiQ5sqJ2J",
        "HTTP_PROXY": os.environ["PROXY"],
        "HTTPS_PROXY": os.environ["PROXY"]
    },
)

with ToolCollection.from_mcp(server_parameters1, trust_remote_code=True) as tool_collection:
    agent = CodeAgent(tools=[*tool_collection.tools], model=amodel, add_base_tools=True)
    agent.run("从广州珠江新城到荔湾的游览路线，已经应该怎么乘坐公共交通工具，要给出每个参观景点的路线、耗时、交通方式，最终以markdown格式告诉我结果")