import backoff as backoff
import openai
import pandas as pd

from app.config.environment import get_openai_key
from openai.embeddings_utils import get_embeddings, get_embedding, cosine_similarity


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


def generate_and_save_embeddings(text_constants, file_path):
    situations = {}
    for key, text in text_constants.items():
        situations[key] = [
            text,
            get_embedding(
                text, engine="text-embedding-ada-002", api_key=get_openai_key()
            ),
        ]

    df = pd.DataFrame(
        list(situations.items()), columns=["Situation", "TextAndEmbedding"]
    )
    df["TextAndEmbedding"] = df["TextAndEmbedding"].astype(str)
    df.to_parquet(file_path, index=False)


def load_situations_embeddings(text_constants, file_path):
    df = pd.read_parquet(file_path)
    df["TextAndEmbedding"] = df["TextAndEmbedding"].apply(eval)
    situations_dict = dict(zip(df["Situation"], df["TextAndEmbedding"]))

    for situation, (text, _) in situations_dict.items():
        assert (
            text == text_constants[situation]
        ), f"Text does not match the expected text for {situation}"

    return {k: v[1] for k, v in situations_dict.items()}


def judge_message_category(message, text_constants, file_path):
    situations = load_situations_embeddings(text_constants, file_path)
    message_embedding = get_embedding(
        message, engine="text-embedding-ada-002", api_key=get_openai_key()
    )
    max_similarity = -1
    best_match = None

    for situation, embedding in situations.items():
        similarity = cosine_similarity(message_embedding, embedding)
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = situation

    return best_match
