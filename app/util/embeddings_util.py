import backoff as backoff
import openai
import pandas as pd

from app.config.api_config import get_openai_key
from openai.embeddings_utils import get_embeddings, get_embedding, cosine_similarity


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def get_embeddings_with_backoff(prompts, engine='text-embedding-ada-002', batch_size=10000):
    embeddings = []
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        embeddings += get_embeddings(list_of_text=batch, engine=engine, api_key=get_openai_key())
    return embeddings


def generate_and_save_embeddings(text_constants, file_path):
    situations = {}
    for key, text in text_constants.items():
        situations[key] = [text, get_embedding(text, engine='text-embedding-ada-002', api_key=get_openai_key())]

    df = pd.DataFrame(list(situations.items()), columns=['Situation', 'TextAndEmbedding'])
    df['TextAndEmbedding'] = df['TextAndEmbedding'].astype(str)
    df.to_parquet(file_path, index=False)


def load_situations_embeddings(text_constants, file_path):
    df = pd.read_parquet(file_path)
    df['TextAndEmbedding'] = df['TextAndEmbedding'].apply(eval)
    situations_dict = dict(zip(df['Situation'], df['TextAndEmbedding']))

    for situation, (text, _) in situations_dict.items():
        assert text == text_constants[situation], f"Text does not match the expected text for {situation}"

    return {k: v[1] for k, v in situations_dict.items()}


def judge_message_category(message, text_constants, file_path):
    situations = load_situations_embeddings(text_constants, file_path)
    message_embedding = get_embedding(message, engine='text-embedding-ada-002', api_key=get_openai_key())
    max_similarity = -1
    best_match = None

    for situation, embedding in situations.items():
        similarity = cosine_similarity(message_embedding, embedding)
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = situation

    return best_match
