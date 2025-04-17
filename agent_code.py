# -*- coding: utf-8 -*-
import os

# 设置HTTP代理
os.environ['HTTP_PROXY'] = os.environ["PROXY"]
os.environ['HTTPS_PROXY'] = os.environ["PROXY"]

from smolagents import CodeAgent, HfApiModel, Tool
from smolagents import OpenAIServerModel
import base64
# 画图工具
image_generation_tool = Tool.from_space(
    "black-forest-labs/FLUX.1-schnell",
    name="image_generator",
    description="Generate an image from a prompt"
)
#image_path = image_generation_tool("一个中国的黑发年轻古典美女")
#print(os.getcwd())
# 将image_path的文件移动到当前目录下
#import shutil
#shutil.move(image_path, os.getcwd())

# Initialize the model
amodel = OpenAIServerModel(
    model_id=os.environ["MODEL_NAME"],
    api_base="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENAI_TOKEN"],
)

# Initialize the agent
agent = CodeAgent(model=amodel,tools=[image_generation_tool])

# Run the agent
response = agent.run("base on the novel provided,Improve the prompt, then generate an scene image according the novel.", additional_args={'user_prompt': '练武厅东边坐着二人。上首是个四十左右的中年道姑，铁青着脸，嘴唇紧闭。下首是个五十余岁的老者，右手撚着长须，神情甚是得意。'})
print(response)