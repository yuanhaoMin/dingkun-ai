import ast
from concurrent.futures import ThreadPoolExecutor
import asyncio

from app.util.time_utll import timeit


def check_syntax_error(code: str) -> bool:
    """
    检查代码中是否有语法错误。
    如果有语法错误，返回True，否则返回False。
    """
    try:
        ast.parse(code)
        return False
    except SyntaxError:
        return True


@timeit
def run_code_to_get_svg(code: str, query_result: list) -> str:
    """
    运行代码并获取SVG数据。
    """
    # 检查代码中的语法错误
    if check_syntax_error(code):
        raise ValueError("Syntax error in the provided code.")

    # 运行代码
    try:
        exec_env = {"query_result": query_result}  # 将query_result添加到执行环境中
        exec(code, exec_env)  # 在隔离的命名空间中执行代码
        svg_data = exec_env.get("svg_data")  # 代码执行后会在svg_data变量中存放SVG数据
        if svg_data is None:
            raise ValueError("The code did not produce the expected SVG data.")

        return svg_data
    except Exception as e:
        raise Exception(f"Execution error: {str(e)}")


async def run_async_tasks(tasks):
    async def run_async(func, *args):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, func, *args)

    return await asyncio.gather(*[run_async(task[0], *task[1]) for task in tasks])

