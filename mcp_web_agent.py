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
fetch_parameters = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server_fetch"],
    env={
        "HTTP_PROXY": os.environ["PROXY"],
        "HTTPS_PROXY": os.environ["PROXY"],
        "USE_PROXY": "true"
    },
)

baidu_parameters = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server_baidu_maps"],
    env={
        "BAIDU_MAPS_API_KEY": "ojLxZsudnK4TAT9Rma8u5VGDiQ5sqJ2J",
        "HTTP_PROXY": os.environ["PROXY"],
        "HTTPS_PROXY": os.environ["PROXY"]
    },
)
currenttime_parameters = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server_time","--local-timezone","Asia/Shanghai"],
    env={
        "HTTP_PROXY": os.environ["PROXY"],
        "HTTPS_PROXY": os.environ["PROXY"]
    },
)

with ToolCollection.from_mcp(fetch_parameters, trust_remote_code=True) as fetch_collection, \
     ToolCollection.from_mcp(currenttime_parameters, trust_remote_code=True) as time_collection, \
     ToolCollection.from_mcp(baidu_parameters, trust_remote_code=True) as baidu_collection:
    agent = CodeAgent(
        tools=[*fetch_collection.tools], 
        model=amodel, 
        add_base_tools=False
    )
    print([*fetch_collection.tools, *time_collection.tools])
    agent.run("先搞清楚今天的日期，然后使用fetch的mcp工具，告诉我bbc今天有什么关于中美贸易战的新闻，用中文markdown格式总结，请注明信息来源")