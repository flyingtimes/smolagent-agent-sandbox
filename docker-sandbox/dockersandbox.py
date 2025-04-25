"""
Docker沙盒实现模块

提供安全的容器环境来执行不受信任的代码，具有以下安全特性：
1. 内存限制(512MB)
2. CPU配额限制
3. 进程数限制(100)
4. 禁止特权提升
5. 移除所有Linux capabilities
6. 以nobody用户身份运行代码
"""
import os
import atexit
import docker
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()  # 加载环境变量


class DockerSandbox:
    """
    Docker沙盒类，用于在隔离的容器环境中安全执行代码
    
    属性:
        client: Docker客户端实例
        container: 当前运行的容器实例
    """
    
    def __init__(self):
        """初始化Docker沙盒"""
        self.client = docker.from_env()  # 创建Docker客户端
        self.container = None  # 当前容器实例
        atexit.register(self.cleanup)  # 注册退出时清理函数
        self.default_volumes = {
            os.path.abspath('./workspace'): {
                'bind': '/app/output',  # 挂载到容器内的/workdir目录
                'mode': 'rw'  # 读写模式
            }
        }
        self.default_code_template = """

        """
    
    def __del__(self):
        """析构函数，确保沙盒被正确清理"""
        print("正在清除沙盒...")
        self.cleanup()
        print("沙盒清理完毕。")
    
    def create_container(self, force = False, volumes: Optional[Dict[str, Any]] = None) -> None:
        """
        创建并启动Docker容器
        
        参数:
            volumes: 可选的自定义卷配置，格式为{"主机路径": {"bind": "容器路径", "mode": "rw/ro"}}
                    
        异常:
            docker.errors.BuildError: 镜像构建失败
            docker.errors.APIError: 容器创建失败
        """
        try:
            # 检查镜像是否存在
            existing_images = self.client.images.list(name="py-sandbox")
            if not existing_images:
                print("开始构建py-sandbox...")
                # 构建新镜像
                dockerfile_path = os.path.join(os.path.dirname(__file__), 'Dockerfile')
                image, _ = self.client.images.build(
                    path=os.path.dirname(__file__),
                    dockerfile=dockerfile_path,
                    tag="py-sandbox",
                    rm=True,
                    forcerm=True,
                    buildargs={}
                )
            else:
                # 使用现有镜像
                image = existing_images[0]
        except docker.errors.BuildError as e:
            print("构建错误日志:")
            for log in e.build_log:
                if 'stream' in log:
                    print(log['stream'].strip())
            raise

        # 设置默认卷配置
        if volumes is None:
            volumes = self.default_volumes
            print("使用默认卷配置。")
        else:
            print("使用自定义卷配置。")
        print(volumes) 
        try:
            if (not self.container) or force:
                if self.container:
                    print("正在销毁沙盒...")
                    self.container.cleanup()
                # 创建并启动容器
                self.container = self.client.containers.run(
                    "py-sandbox",
                    command="tail -f /dev/null",  # 保持容器运行
                    detach=False,
                    tty=True,
                    mem_limit="512m",  # 内存限制
                    cpu_quota=50000,  # CPU配额
                    pids_limit=100,  # 进程数限制
                    security_opt=["no-new-privileges"],  # 禁止特权提升
                    cap_drop=["ALL"],  # 移除所有Linux capabilities
                    environment={
                        "OPENAI_TOKEN": os.getenv("OPENAI_TOKEN"),
                        "MODEL_NAME": os.getenv("MODEL_NAME"),
                        "PROXY": os.getenv("PROXY_IN_DOCKER")
                    },
                    volumes=volumes,
                    auto_remove=True  # 容器退出时自动删除
                )
                print("沙盒创建成功。") 
        except docker.errors.APIError as e:
            print(f"创建沙盒时发生错误: {str(e)}")
            raise
    
    def run_code(self, code: str, template_file: str = "default.tmpl") -> str:
        """
        在容器中执行代码
        
        参数:
            code: 要执行的Python代码字符串
            
        返回:
            代码执行输出，如果无输出则返回None
        """
        if not self.container:
            print("沙盒不存在，尝试创建...")
            self.create_container()

        
        # 从code_template/default.py 中读取代码模板,使用Jinja2渲染模板
        from jinja2 import Template
        with open(os.path.join(os.path.dirname(__file__), 'code_template/default.tmpl'), 'r',encoding='utf-8') as f:
            template = Template(f.read())
            code = template.render(question=code)

        # 在容器中执行代码
        exec_result = self.container.exec_run(
            cmd=["python", "-c", code],
            user="nobody"  # 以非特权用户运行
        )

        # 返回执行结果
        return exec_result.output.decode() if exec_result.output else None
    
    def cleanup(self) -> None:
        """
        清理容器资源
        
        安全地停止并清理当前运行的容器
        """
        if self.container:
            try:
                self.container.stop()
            except docker.errors.NotFound:
                # 容器已被删除是预期行为
                pass
            except Exception as e:
                print(f"沙盒关闭时出错，请检查py-sandbox是否异常退出: {e}")
            finally:
                self.container = None  # 清除容器引用
