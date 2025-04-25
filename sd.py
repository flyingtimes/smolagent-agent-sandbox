from smolagents import CodeAgent, DuckDuckGoSearchTool, VisitWebpageTool, ToolCallingAgent
from smolagents import LiteLLMModel, tool  
import os
# 设置HTTP代理
#os.environ['HTTP_PROXY'] = "http://127.0.0.1:1087"
#os.environ['HTTPS_PROXY'] = "http://127.0.0.1:1087"
amodel = LiteLLMModel(
    model_id="openrouter/google/gemini-2.5-flash-preview",
    api_base="https://openrouter.ai/api/v1",
    api_key="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",
)
search_agent = ToolCallingAgent(
        tools=[DuckDuckGoSearchTool(),VisitWebpageTool()],
        model=amodel,
        name="search_agent",
        description="This is an agent that can do web search.",
    )
agent = CodeAgent(tools=[],managed_agents=[search_agent], model=amodel, executor_type="docker")
output = agent.run("今天2025年4月24日，美国今天各个股票市场的情况如何？请用数据说明涨幅，上涨板块，上涨股票都有哪些，详细说明各个信息来源的观点并注明信息来源，用中文回答")
print("Docker executor result:", output)