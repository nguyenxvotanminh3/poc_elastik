# services/embedder.py
from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_embedding(text: str) -> list[float]:
    resp = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=text
    )
    return resp.data[0].embedding
