import backoff as backoff
import pandas as pd
from app.config.environment import get_openai_key
from openai.embeddings_utils import get_embeddings, get_embedding, cosine_similarity


def generate_and_save_embeddings(file_path: str, scenarios: dict):
    embedded_scenarios = {}
    for scenario_name, text in scenarios.items():
        embedded_scenarios[scenario_name] = [
            text,
            get_embedding(
                text, engine="text-embedding-ada-002", api_key=get_openai_key()
            ),
        ]

    df = pd.DataFrame(
        list(embedded_scenarios.items()), columns=["Scenario", "TextAndEmbedding"]
    )
    df["TextAndEmbedding"] = df["TextAndEmbedding"].astype(str)
    df.to_parquet(file_path, index=False)


@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def get_embeddings_with_backoff(text_list, batch_size=100):
    all_embeddings = []
    total_size = len(text_list)
    for i in range(0, total_size, batch_size):
        current_batch = text_list[i : i + batch_size]
        batch_embeddings = get_embeddings(
            api_key=get_openai_key(),
            engine="text-embedding-ada-002",
            list_of_text=current_batch,
            request_timeout=10,
        )
        all_embeddings.extend(batch_embeddings)
    return all_embeddings
