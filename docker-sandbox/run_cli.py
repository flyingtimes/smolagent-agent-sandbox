from dockersandbox import DockerSandbox
sandbox = DockerSandbox()
# result = sandbox.run_code("""
# 帮我写一个python程序完成这个目标：
# 创建一个excel模板，搜集广东省21个地市的无线网络指标：接通率，掉话率，切换成功率，要求每个地市给出填表人姓名、联系方式。表格的字段使用中文，在表格最后一行添加一个全省汇总行。
# """)
# print(result)
# print("===============================")

result = sandbox.run_code("""
2025年4月22日中国和美国关于关税都有哪些重大新闻？用中文回答，将结果以markdown格式写入工作目录下的output.md
""")

# result = sandbox.run_code("""
# mcp工具都有哪些主流的工具，在哪些地方能找到比较全面的mcp工具列表？深度搜索网络信息，给出最常见的20种以上mcp工具，用中文回答，请注明出处，将结果以markdown格式写入工作目录下的output2.md
# """)
print(result)
