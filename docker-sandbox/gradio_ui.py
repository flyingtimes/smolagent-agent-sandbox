import os
import gradio as gr
import docker
from dotenv import load_dotenv
load_dotenv()

import atexit
from dockersandbox import DockerSandbox



class DockerSandboxUI:
    """Docker沙盒UI的核心类，处理所有业务逻辑"""
    CODE_DIR = os.path.abspath('./code')
    DEFAULT_EXAMPLE_CODE = """
# 示例代码 - 处理输入文件并生成输出文件
import os

# 输入目录和输出目录已挂载到容器中
input_dir = '/workdir/input'
output_dir = '/workdir/output'

# 列出输入目录中的所有文件
print(f"输入目录中的文件:")
for file in os.listdir(input_dir):
    print(f" - {file}")

# 创建一个示例输出文件
with open(os.path.join(output_dir, 'output.txt'), 'w') as f:
    f.write('处理完成!')

print("处理完成，输出已保存到输出目录。")
"""

    def __init__(self):
        self._init_directories()
        self.docker_available = self._check_docker_available()
        self.sandbox = DockerSandbox() if self.docker_available else None
        os.makedirs(self.CODE_DIR, exist_ok=True)
        self.selected_file = None  # 存储当前选中的文件名

    def get_python_files(self):
        """获取code目录下的Python文件列表"""
        python_files = []
        if os.path.exists(self.CODE_DIR):
            for file in os.listdir(self.CODE_DIR):
                if file.endswith('.py'):
                    python_files.append(file)
        return python_files

    def load_file_content(self, filename):
        """加载指定Python文件的内容"""
        if not filename:
            return "No filename provided"
        if isinstance(filename, list):
            filename = filename[0]
        
        # 确保文件名是字符串且去除可能的引号和方括号
        filename = str(filename).strip("'[]")
        file_path = os.path.join(self.CODE_DIR, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"文件不存在: {filename}"
        except Exception as e:
            return f"加载文件时出错: {str(e)}"

    def _init_directories(self):
        """初始化输入输出目录"""
        self.input_dir = os.path.abspath('./docker-sandbox/tmp/input')
        self.output_dir = os.path.abspath('./docker-sandbox/tmp/output')
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def _check_docker_available(self):
        """检查Docker服务是否可用"""
        try:
            docker.from_env().ping()
            return True
        except Exception:
            return False

    def update_directory(self, new_dir, is_input=True):
        """更新目录路径"""
        if not new_dir or not os.path.isdir(new_dir):
            return f"无效的目录: {new_dir}"
        
        if is_input:
            self.input_dir = new_dir
            # 更新Docker卷配置
            if self.sandbox and self.sandbox.container:
                volumes = self._prepare_volumes()
                self.sandbox.cleanup()  # 停止当前容器
                self.sandbox.create_container(volumes=volumes)  # 使用新的卷配置创建容器
            return f"输入目录已更新为: {new_dir}"
        else:
            self.output_dir = new_dir
            # 更新Docker卷配置
            if self.sandbox and self.sandbox.container:
                volumes = self._prepare_volumes()
                self.sandbox.cleanup()  # 停止当前容器
                self.sandbox.create_container(volumes=volumes)  # 使用新的卷配置创建容器
            return f"输出目录已更新为: {new_dir}"

    def execute_code(self, code):
        """执行代码"""
        if not self.docker_available:
            return "错误: Docker服务未运行或无法连接。请确保Docker已安装并启动。"
        if not code.strip():
            return "错误: 代码不能为空"

        try:
            self.run_btn.interactive = False
                
            volumes = self._prepare_volumes()
            self.sandbox.create_container(volumes=volumes)
            result = self.sandbox.run_code(code)
            return result if result else "代码执行完成，无输出"
        except Exception as e:
            return f"执行错误: {str(e)}"
        finally:
            self.run_btn.interactive = True

    def _prepare_volumes(self):
        """准备Docker卷配置"""
        return {
            self.input_dir: {'bind': '/workdir/input', 'mode': 'ro'},
            self.output_dir: {'bind': '/workdir/output', 'mode': 'rw'}
        }

    def stop_execution(self):
        """停止代码执行"""
        if self.sandbox and self.sandbox.container:
            self.sandbox.cleanup()
            return "已停止代码执行"
        return "没有正在运行的代码"

def create_ui_components(ui):
    """创建UI组件"""
    with gr.Blocks(title="Docker沙盒执行器") as demo:
        gr.Markdown("# Docker沙盒代码执行器")
        
        if not ui.docker_available:
            gr.Markdown("⚠️ **警告: Docker服务未运行或无法连接**", elem_classes=["warning"])
            gr.Markdown("请确保Docker已安装并启动，然后刷新页面。")
        
        gr.Markdown("在安全的Docker环境中执行Python代码，处理输入文件并生成输出文件。")
        
        with gr.Row():
            with gr.Column(scale=1):
                input_dir = gr.Textbox(label="输入文件夹路径", value=ui.input_dir)
                input_dir_btn = gr.Button("更新输入目录")
                output_dir = gr.Textbox(label="输出文件夹路径", value=ui.output_dir)
                output_dir_btn = gr.Button("更新输出目录")
                dir_status = gr.Textbox(label="状态信息", interactive=False)
                
                # 添加Python文件列表
                file_list = gr.List(
                    ui.get_python_files(),
                    label="Python文件列表",
                    elem_classes=["file-list"],
                    interactive=False
                )
                load_btn = gr.Button("加载选中文件")
            
            with gr.Column(scale=2):
                code_input = gr.Code(language="python", label="Python代码", value=ui.DEFAULT_EXAMPLE_CODE)
                with gr.Row():
                    run_btn = gr.Button("在Docker中执行代码", variant="primary")
                    stop_btn = gr.Button("停止执行", variant="stop")
                output = gr.Textbox(label="执行结果", interactive=False)
        
        setup_event_handlers(ui, input_dir, input_dir_btn, output_dir, output_dir_btn,
                            dir_status, code_input, run_btn, stop_btn, output, file_list, load_btn)
        add_styles()
    
    return demo

def setup_event_handlers(ui, input_dir, input_dir_btn, output_dir, output_dir_btn,
                        dir_status, code_input, run_btn, stop_btn, output, file_list, load_btn):
    """设置事件处理器"""
    # 保存run_btn引用到UI实例中
    ui.run_btn = run_btn
    
    input_dir_btn.click(lambda x: ui.update_directory(x, True),
                       inputs=input_dir, outputs=dir_status)
    output_dir_btn.click(lambda x: ui.update_directory(x, False),
                        inputs=output_dir, outputs=dir_status)
    run_btn.click(ui.execute_code, inputs=code_input, outputs=output)
    stop_btn.click(ui.stop_execution, outputs=output)
    
    # 添加文件列表选择事件
    def on_file_select(evt: gr.SelectData):
        ui.selected_file = evt.value
        return f"已选择文件: {evt.value}"
    
    file_list.select(on_file_select, outputs=dir_status)
    
    # 修改加载按钮事件，使用选中的文件名
    load_btn.click(
        fn=lambda: ui.load_file_content(ui.selected_file) if ui.selected_file else "请先选择一个文件",
        outputs=[code_input]
    )

def add_styles():
    """添加CSS样式"""
    gr.Markdown("""
    <style>
    .warning {
        color: #721c24;
        background-color: #f8d7da;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    </style>
    """)

def main():
    ui = DockerSandboxUI()
    demo = create_ui_components(ui)
    demo.launch()

if __name__ == "__main__":
    main()