from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from app.config.api_config import get_openai_key


# def get_chat_chain(vector_store):
#     llm = ChatOpenAI(get_openai_key)
#
#     # 存储历史记录
#     # 参考官网链接：https://python.langchain.com/docs/use_cases/question_answering/how_to/chat_vector_db
#     # 用于缓存或者保存对话历史记录的对象
#     memory = ConversationBufferMemory(
#         memory_key='chat_history', return_messages=True)
#     # 对话链
#     conversation_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=vector_store.as_retriever(),
#         memory=memory
#     )
#     return conversation_chain
