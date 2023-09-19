import os

from langchain import FAISS, OpenAI
from langchain.chains import ConversationalRetrievalChain
import chardet
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PDFPlumberLoader
from langchain.embeddings import OpenAIEmbeddings
from typing import List, Tuple, Any

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.util.file_processing_util import process_pdf_file, extract_from_docx, detect_encoding



# def get_answer_from_vector(file_path, question):
#     # Determine file type
#     if file_path.endswith('.pdf'):
#         docs = PDFPlumberLoader(file_path).load()
#     elif file_path.endswith('.docx'):
#         doc = extract_from_docx(file_path)
#         docs = [doc]
#     elif file_path.endswith('.txt'):
#         encoding = detect_encoding(file_path)
#         with open(file_path, 'r', encoding=encoding) as f:
#             content = f.read()
#         docs = [Document(page_content=content, metadata={"source": "txt_file"})]
#     else:
#         raise ValueError("Unsupported file type")
#
#     # Split the document and store text embeddings
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#     split_docs = text_splitter.split_documents(docs)
#     embeddings = OpenAIEmbeddings()
#     vectorstore = FAISS.from_documents(split_docs, embeddings)
#
#     # Create a QA chain using OpenAI
#     llm = OpenAI(temperature=0)
#     chain = load_qa_chain(llm, chain_type="stuff")
#
#     # Perform similarity search based on the question
#     similar_docs = vectorstore.similarity_search(question, 2, include_metadata=True)
#
#     # Get the answer using the QA chain and the relevant documents
#     answer = chain.run(input_documents=similar_docs, question=question)
#
#     return answer
