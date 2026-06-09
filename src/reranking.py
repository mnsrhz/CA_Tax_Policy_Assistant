from __future__ import annotations

from functools import lru_cache


def select_top_contexts(candidates: list[dict[str, object]], top_n: int) -> list[dict[str, object]]:
    return sorted(candidates, key=lambda item: float(item.get("rerank_score", 0.0)), reverse=True)[:top_n]


@lru_cache(maxsize=1)
def load_reranker(model_name: str):
    from sentence_transformers import CrossEncoder

    return CrossEncoder(model_name)


def rerank(query: str, candidates: list[dict[str, object]], model_name: str, top_n: int = 6) -> list[dict[str, object]]:
    model = load_reranker(model_name)
    pairs = [(query, str(candidate["text"])) for candidate in candidates]
    scores = model.predict(pairs)
    scored = []
    for candidate, score in zip(candidates, scores):
        updated = dict(candidate)
        updated["rerank_score"] = float(score)
        scored.append(updated)
    return select_top_contexts(scored, top_n=top_n)
