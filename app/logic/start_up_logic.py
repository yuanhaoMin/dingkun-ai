from app.logic import dashboard_logic, helper_chat_logic
from app.util import embeddings_util


def generate_embedding_for_scenarios():
    embeddings_util.generate_and_save_embeddings_locally(
        file_path=dashboard_logic.get_scenario_file_path(),
        scenarios=dashboard_logic.get_scenarios(),
    )
    embeddings_util.generate_and_save_embeddings_locally(
        file_path=helper_chat_logic.get_scenario_file_path(),
        scenarios=helper_chat_logic.get_scenarios(),
    )
