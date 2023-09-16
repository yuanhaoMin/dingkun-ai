from langchain import OpenAI
from langchain.agents import create_csv_agent


# OpenAI()默认使用text-davinci-003 效果似乎好于gpt-3.5-turbo
def query_csv(file_path: str, query: str, temperature: int = 0) -> str:
    agent = create_csv_agent(OpenAI(temperature=temperature), file_path)
    return agent.run(query)
