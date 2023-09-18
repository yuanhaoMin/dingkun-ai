from app.agent.csv_agent import query_csv
from app.agent.file_qa_agent import get_answer_from_file


def document_answer_service(file_path: str, question: str) -> str:
    return get_answer_from_file(file_path, question)


def redirect_page_service(operation_text: str) -> str:
    """
    Handle requests related to page redirection, system services, or any user interface interactions.

    Parameters:
    - operation_text (str): Text describing the operation or redirection request.

    Returns:
    - str: Response or result of the operation.
    """
    pass  # TODO: Implement the function


def data_analysis_service(file_path: str, query: str) -> str:
    return query_csv(file_path, query)
