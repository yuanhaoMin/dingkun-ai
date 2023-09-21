import backoff as backoff
import openai
from app.config.api_config import get_openai_key
from openai.embeddings_utils import get_embeddings


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
def get_embeddings_with_backoff(prompts, engine='text-embedding-ada-002', batch_size=10000):
    embeddings = []
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        embeddings += get_embeddings(list_of_text=batch, engine=engine, api_key=get_openai_key())
    return embeddings
