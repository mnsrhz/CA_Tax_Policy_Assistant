from __future__ import annotations

from functools import lru_cache


QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def normalize_for_bge(text: str, is_query: bool) -> str:
    stripped = text.strip()
    return f"{QUERY_PREFIX}{stripped}" if is_query else stripped


@lru_cache(maxsize=1)
def load_embedding_model(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def embed_texts(texts: list[str], model_name: str, is_query: bool = False) -> list[list[float]]:
    model = load_embedding_model(model_name)
    normalized = [normalize_for_bge(text, is_query=is_query) for text in texts]
    embeddings = model.encode(normalized, normalize_embeddings=True)
    return embeddings.tolist()
