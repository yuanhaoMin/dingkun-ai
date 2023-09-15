from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS, Milvus, Pinecone, Chroma, Zilliz
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from PyPDF2 import PdfReader
import docx2txt
import chardet
from app.config.api_config import get_openai_key


def remove_blank_lines(text: str) -> str:
    """移除文本中的空行"""
    lines = text.splitlines()
    non_blank_lines = [line for line in lines if line.strip()]
    return "\n".join(non_blank_lines)





def detect_encoding(file_path):
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        return chardet.detect(f.read())['encoding']


def extract_text_from_TXT(files):
    """
    加载多个txt文件并返回它们的内容。

    参数:
        files (list): 要加载的txt文件的路径列表。

    返回:
        str: 所有txt文件的联合文本内容。
    """
    text = ""
    for txt_file in files:
        encoding = detect_encoding(txt_file)
        with open(txt_file, 'r', encoding=encoding) as file:
            raw_text = file.read()
            processed_text = remove_blank_lines(raw_text)
            text += processed_text + '\n'  # 添加换行符以区分不同文件的内容
    return text


def extract_text_from_DOCX(files):
    """
    加载多个docx文件并返回它们的内容。

    参数:
        files (list): 要加载的docx文件的路径列表。

    返回:
        str: 所有docx文件的联合文本内容。
    """
    text = ""
    for docx_file in files:
        raw_text = docx2txt.process(docx_file)
        processed_text = remove_blank_lines(raw_text)
        text += processed_text + '\n'  # 添加换行符以区分不同文件的内容
    return text


def extract_text_from_PDF(files):
    # 参考官网链接：https://python.langchain.com/docs/modules/data_connection/document_loaders/pdf
    # 加载多个PDF文件
    text = ""
    for pdf in files:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def extract_file_paths_from_code(code):
    paths = []
    lines = code.split('\n')
    for line in lines:
        if 'filename = "' in line:
            path = line.split('filename = "')[1].split('"')[0]
            paths.append(path)
    return paths

def split_content_into_chunks(text):
    # 参考官网链接：https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/character_text_splitter
    text_spliter = CharacterTextSplitter(separator="\n",
                                         chunk_size=500,
                                         chunk_overlap=80,
                                         length_function=len)
    chunks = text_spliter.split_text(text)
    return chunks


def save_chunks_into_vectorstore(content_chunks, embedding_model):
    # 参考官网链接：https://python.langchain.com/docs/modules/data_connection/vectorstores/
    # ① FAISS
    # pip install faiss-gpu (如果没有GPU，那么 pip install faiss-cpu)
    # vectorstore = FAISS.from_texts(texts=content_chunks,
    #                                embedding=embedding_model)

    # ② Pinecone
    # 官网链接：https://python.langchain.com/docs/integrations/vectorstores/pinecone
    # Pinecone官网链接：https://docs.pinecone.io/docs/quickstart
    # pip install pinecone-client==2.2.2
    # 初始化
    # pinecone.init(api_key=Keys.PINECONE_KEY, environment="asia-southeast1-gcp")
    # # 创建索引
    # index_name = "pinecone-chatbot-demo"
    # # 检查索引是否存在，如果不存在，则创建
    # if index_name not in pinecone.list_indexes():
    #     pinecone.create_index(name=index_name,
    #                           metric="cosine",
    #                           dimension=1536)
    # vectorstore = Pinecone.from_texts(texts=content_chunks,
    #                                       embedding=embedding_model,
    #                                       index_name=index_name)

    vectorstore = Zilliz.from_texts(texts=content_chunks,
                                    embedding=embedding_model,
                                    connection_args={
                                        "uri": "https://in03-5820cbda928cefe.api.gcp-us-west1.zillizcloud.com",
                                        "token": "19c3026bad55e4f75d6b74be453a72d157f0256ddeb96d299ae95c86c7d1b951978f6979f96407596f718d267a46a8a8237b752b",
                                        "secure": True}
                                    )

    return vectorstore


def get_chat_chain(vector_store):
    # ① 获取 LLM model
    llm = ChatOpenAI(get_openai_key)

    # ② 存储历史记录
    # 参考官网链接：https://python.langchain.com/docs/use_cases/question_answering/how_to/chat_vector_db
    # 用于缓存或者保存对话历史记录的对象
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    # ③ 对话链
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory
    )
    return conversation_chain
