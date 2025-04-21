import os
import docker
import argparse
from docker.transport import NpipeHTTPAdapter
from typing import Optional

class DockerSandbox:
    def __init__(self):
        self.client = docker.from_env()
        self.container = None

    def create_container(self):
        try:
            image, build_logs = self.client.images.build(
                path=".",
                tag="py-sandbox",
                rm=True,
                forcerm=True,
                buildargs={},
                # decode=True
            )
        except docker.errors.BuildError as e:
            print("Build error logs:")
            for log in e.build_log:
                if 'stream' in log:
                    print(log['stream'].strip())
            raise

        # Create container with security constraints and proper logging
        self.container = self.client.containers.run(
            "py-sandbox",
            command="tail -f /dev/null",  # Keep container running
            detach=True,
            tty=True,
            mem_limit="512m",
            cpu_quota=50000,
            pids_limit=100,
            security_opt=["no-new-privileges"],
            cap_drop=["ALL"],
            environment={
                "OPENAI_TOKEN": os.getenv("OPENAI_TOKEN"),
                "MODEL_NAME": os.getenv("MODEL_NAME"),
                "PROXY": os.getenv("PROXY_IN_DOCKER")
            },
            # 将本地./tmp目录挂载到容器的/workdir目录
            volumes={
                os.path.abspath('./tmp'): {
                    'bind': '/workdir',
                    'mode': 'rw'
                }
            }
        )

    def run_code(self, code: str) -> Optional[str]:
        if not self.container:
            self.create_container()

        # Execute code in container
        exec_result = self.container.exec_run(
            cmd=["python", "-c", code],
            user="nobody"
        )

        # Collect all output
        return exec_result.output.decode() if exec_result.output else None

    def cleanup(self):
        if self.container:
            try:
                self.container.stop()
            except docker.errors.NotFound:
                # Container already removed, this is expected
                pass
            except Exception as e:
                print(f"Error during cleanup: {e}")
            finally:
                self.container = None  # Clear the reference

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Run Python code in a Docker sandbox')
    parser.add_argument('--input-file', type=str, default='agent_code.py',
                      help='Python file to execute (default: agent_code.py)')
    return parser.parse_args()

# Example usage:
if __name__ == '__main__':
    args = parse_args()
    sandbox = DockerSandbox()

    try:
        # Get absolute path of the input file relative to the parent directory
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        input_file_path = os.path.join(script_dir, args.input_file)
        
        # Read agent code from specified file
        with open(input_file_path, 'r', encoding='utf-8') as f:
            agent_code = f.read()

        # Run the code in the sandbox
        output = sandbox.run_code(agent_code)
        print(output)

    finally:
        sandbox.cleanup()