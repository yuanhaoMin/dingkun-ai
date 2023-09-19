import os
from langchain import OpenAI
from langchain.agents import create_csv_agent
from langchain.embeddings import OpenAIEmbeddings
from pymilvus import MilvusClient

from app.config.api_config import get_milvus_uri, get_milvus_token
from app.util.openai_util import completion
from app.util.text_util import create_prompt_from_template_file
from app.util.time_utll import get_current_date_and_day

current_date, day_of_week = get_current_date_and_day()
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


# OpenAI()默认使用text-davinci-003 效果似乎好于gpt-3.5-turbo
# 问无关问题会返回none
def query_csv(file_path: str, query: str) -> str:
    data_dir = os.path.join(CURRENT_DIR, '..', '..', 'data')
    data_dir = os.path.abspath(data_dir)

    # 列出'data'目录中的文件
    files = os.listdir(data_dir)

    # 如果'data'目录下没有文件或有多个文件，返回提示信息
    if len(files) != 1:
        return "请先上传文件~"

    # 如果只有一个文件，则传入这个文件的路径
    target_file = os.path.join(data_dir, files[0])

    agent = create_csv_agent(OpenAI(temperature=0, model_name='text-davinci-003'), target_file)
    return agent.run(query)


def navigate_to_page():
    return '正在跳转请稍等'


def answer_documentation(question: str, file_path: str = None) -> str:
    extra_info_list = search_similar_texts(question, 2)

    extra_info = ' '.join([item['text'] for item in extra_info_list])
    replacements = {"current_date:": current_date,
                    "day_of_week:": day_of_week,
                    "extra_info:": extra_info
                    }
    prompt = create_prompt_from_template_file(
        filename="smart_helper_forwarding_prompts", replacements=replacements
    )
    print(prompt)
    messages = []
    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": question})
    res = completion(messages)
    return res


def search_similar_texts(message, k):
    client = MilvusClient(
        uri=get_milvus_uri(),
        token=get_milvus_token()
    )
    embedding_model = OpenAIEmbeddings()
    # 获取message的向量表示
    vector = embedding_model.embed_query(message)

    # 使用MilvusClient的search方法查询相似的文本
    results = client.search(
        collection_name='dingkun',
        data=[vector],
        limit=k,
        output_fields=["text"]
    )

    # 从results中提取相关的信息
    similar_texts = []
    for hit in results[0]:
        similar_texts.append({
            "text": hit['entity']["text"],
        })

    return similar_texts
