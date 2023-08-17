from app.util.openai_util import completion
from app.util.text_util import create_prompt_from_template_file
from app.util.time_utll import timeit


@timeit
def ai_analyze_query_result_to_code_chain(
    input_text: str, query_result: dict, current_date: str, day_of_week: str
) -> str:
    """
    根据用户的输入和查询结果，通过AI生成可运行的数据可视化代码。

    参数:
    - input_text: 用户提供的自然语言输入。
    - query_result: SQL查询返回的数据。

    返回:
    - 可运行的数据可视化代码。
    """

    # 使用提示词模板并替换其中的内容
    replacements = {
        "current_date": current_date,  # 使用Python的date.today()获取今天的日期
        "day_of_week": day_of_week,  # 使用strftime获取当前的星期
    }
    prompt = create_prompt_from_template_file(
        filename="data_visualization_code_generator_prompts", replacements=replacements
    )

    # 构造与AI对话的消息列表
    messages = [
        {"role": "system", "content": prompt},
        {
            "role": "user",
            "content": f"Question:\n{input_text}\n\nquery_result_sample:\n{query_result}",
        },
    ]

    # 使用OpenAI API获取可运行的代码
    runnable_code = completion(messages)

    return runnable_code
