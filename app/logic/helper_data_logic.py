import os
from app.constant.path_constants import DATA_DIRECTORY_PATH
from fastapi import HTTPException
from langchain.agents import create_csv_agent
from langchain.agents.agent_types import AgentType
from langchain.llms import OpenAI


def chat_with_data_file(filename: str, user_message: str) -> str:
    file_path = os.path.join(DATA_DIRECTORY_PATH, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=f"File {filename} not found.")
    agent = create_csv_agent(
        OpenAI(temperature=0),
        file_path,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    )
    return agent.run(user_message)
