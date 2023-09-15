import os
import re

import jupyter_client

from app.util.file_processing_utli import extract_text_from_TXT, extract_text_from_DOCX, extract_text_from_PDF, \
    extract_file_paths_from_code


def delete_color_control_char(string):
    """
        删除字符串中的颜色控制字符。

        参数:
        - string (str): 要处理的字符串。

        返回:
        - str: 删除颜色控制字符后的字符串。
    """
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    return ansi_escape.sub("", string)


class JupyterKernel:
    """
       JupyterKernel 类

       这个类提供与Jupyter核交互的接口，允许执行代码并获取结果。

       属性:
       - kernel_manager: Jupyter核的管理器实例。
       - kernel_client: Jupyter核的客户端实例。
       - work_dir: 工作目录路径。
       - available_functions: 提供的可用函数映射。

       方法:
       - execute_code_(): 执行代码并直接获取输出。
       - execute_code(): 执行代码并返回格式化的输出。
       - _create_work_dir(): 在Jupyter环境中创建和设置工作目录。
       - restart_jupyter_kernel(): 重启Jupyter核。
    """

    def __init__(self, work_dir):
        (
            self.kernel_manager,
            self.kernel_client,
        ) = jupyter_client.manager.start_new_kernel(kernel_name="python3")
        self.work_dir = work_dir
        self._create_work_dir()
        self.available_functions = {
            "execute_code": self.execute_code,
            "python": self.execute_code,
            "process_text_file": self.process_text_file
        }

    def execute_code_(self, code):
        """
            在Jupyter核中执行代码并获取输出。

            参数:
            - code (str): 要执行的代码字符串。

            返回:
            - list: 包含输出标记和对应输出内容的列表。
        """
        # 检查code中是否有指定的文件名扩展
        if 'filename = "' in code or "filename = '" in code:
            if '.txt"' in code:
                files = extract_file_paths_from_code(code)
                text = extract_text_from_TXT(files)
                return [("extracted_text", text)]
            elif '.docx"' in code:
                files = extract_file_paths_from_code(code)
                text = extract_text_from_DOCX(files)
                return [("extracted_text", text)]
            elif '.pdf"' in code:
                files = extract_file_paths_from_code(code)
                text = extract_text_from_PDF(files)
                return [("extracted_text", text)]
        msg_id = self.kernel_client.execute(code)

        # Get the output of the code
        iopub_msg = self.kernel_client.get_iopub_msg()

        all_output = []
        while True:
            if iopub_msg["msg_type"] == "stream":
                if iopub_msg["content"].get("name") == "stdout":
                    output = iopub_msg["content"]["text"]
                    all_output.append(("stdout", output))
                iopub_msg = self.kernel_client.get_iopub_msg()
            elif iopub_msg["msg_type"] == "execute_result":
                if "data" in iopub_msg["content"]:
                    if "text/plain" in iopub_msg["content"]["data"]:
                        output = iopub_msg["content"]["data"]["text/plain"]
                        all_output.append(("execute_result_text", output))
                    if "text/html" in iopub_msg["content"]["data"]:
                        output = iopub_msg["content"]["data"]["text/html"]
                        all_output.append(("execute_result_html", output))
                    if "image/png" in iopub_msg["content"]["data"]:
                        output = iopub_msg["content"]["data"]["image/png"]
                        all_output.append(("execute_result_png", output))
                    if "image/jpeg" in iopub_msg["content"]["data"]:
                        output = iopub_msg["content"]["data"]["image/jpeg"]
                        all_output.append(("execute_result_jpeg", output))
                iopub_msg = self.kernel_client.get_iopub_msg()
            elif iopub_msg["msg_type"] == "display_data":
                if "data" in iopub_msg["content"]:
                    if "text/plain" in iopub_msg["content"]["data"]:
                        output = iopub_msg["content"]["data"]["text/plain"]
                        all_output.append(("display_text", output))
                    if "text/html" in iopub_msg["content"]["data"]:
                        output = iopub_msg["content"]["data"]["text/html"]
                        all_output.append(("display_html", output))
                    if "image/png" in iopub_msg["content"]["data"]:
                        output = iopub_msg["content"]["data"]["image/png"]
                        all_output.append(("display_png", output))
                    if "image/jpeg" in iopub_msg["content"]["data"]:
                        output = iopub_msg["content"]["data"]["image/jpeg"]
                        all_output.append(("display_jpeg", output))
                iopub_msg = self.kernel_client.get_iopub_msg()
            elif iopub_msg["msg_type"] == "error":
                if "traceback" in iopub_msg["content"]:
                    output = "\n".join(iopub_msg["content"]["traceback"])
                    all_output.append(("error", output))
                iopub_msg = self.kernel_client.get_iopub_msg()
            elif (
                iopub_msg["msg_type"] == "status"
                and iopub_msg["content"].get("execution_state") == "idle"
            ):
                break
            else:
                iopub_msg = self.kernel_client.get_iopub_msg()

        return all_output

    def execute_code(self, code):
        """
            在Jupyter核中执行代码并返回格式化的输出。

            参数:
            - code (str): 要执行的代码字符串。

            返回:
            - tuple: 格式化的输出字符串和原始内容。
        """
        text_to_gpt = []
        print(code)
        content_to_display = self.execute_code_(code)
        for mark, out_str in content_to_display:
            if mark in ("stdout", "execute_result_text", "display_text"):
                text_to_gpt.append(out_str)
            elif mark in (
                "execute_result_png",
                "execute_result_jpeg",
                "display_png",
                "display_jpeg",
            ):
                text_to_gpt.append("[image]")
            elif mark == "error":
                text_to_gpt.append(delete_color_control_char(out_str))

        return "\n".join(text_to_gpt), content_to_display

    def _create_work_dir(self):
        """
            在Jupyter环境中创建和设置工作目录。
        """
        # set work dir in jupyter environment
        init_code = (
            f"import os\n"
            f"if not os.path.exists('{self.work_dir}'):\n"
            f"    os.mkdir('{self.work_dir}')\n"
            f"os.chdir('{self.work_dir}')\n"
            f"del os"
        )
        self.execute_code_(init_code)

    def restart_jupyter_kernel(self):
        """
            重启Jupyter核并重新设置工作目录。
        """
        self.kernel_client.shutdown()
        (
            self.kernel_manager,
            self.kernel_client,
        ) = jupyter_client.manager.start_new_kernel(kernel_name="python3")
        self._create_work_dir()

    def process_text_file(self, filename):
        """
        处理并展示文本文件的内容。

        参数:
        - filename (str): 上传的文本文件的名称。

        返回:
        - tuple: 格式化的输出字符串和原始内容。
        """
        filepath = os.path.join(self.work_dir, filename)

        # 检查文件是否存在
        if not os.path.exists(filepath):
            return f"Error: File '{filename}' not found in the working directory.", [
                ("error", f"File '{filename}' not found.")]

        lines = []
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        text_to_gpt = []
        content_to_display = []

        if len(lines) > 500:
            preview_lines = lines[:10]
            formatted_output = f"File '{filename}' contains {len(lines)} lines. Here are the first 10 lines:\n{''.join(preview_lines)}"
            content_to_display.append(("stdout", formatted_output))
        else:
            file_content = ''.join(lines)
            content_to_display.append(("stdout", file_content))

        for mark, out_str in content_to_display:
            if mark in ("stdout", "execute_result_text", "display_text"):
                text_to_gpt.append(out_str)

        return "\n".join(text_to_gpt), content_to_display
