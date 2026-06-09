from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path
import re
from typing import Any

from src.models import DocumentChunk, RetrievalFilters


DEFAULT_BM25_INDEX_PATH = Path("data/bm25_index.json")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def build_bm25_index(chunks: list[DocumentChunk], k1: float = 1.5, b: float = 0.75) -> dict[str, Any]:
    documents = []
    document_frequencies: Counter[str] = Counter()
    total_length = 0

    for chunk in chunks:
        tokens = tokenize(chunk.text)
        token_counts = Counter(tokens)
        document_frequencies.update(token_counts.keys())
        total_length += len(tokens)
        documents.append(
            {
                "metadata": chunk.to_pinecone_metadata(),
                "token_counts": dict(token_counts),
                "length": len(tokens),
            }
        )

    return {
        "version": 1,
        "k1": k1,
        "b": b,
        "document_count": len(documents),
        "average_document_length": total_length / len(documents) if documents else 0.0,
        "document_frequencies": dict(document_frequencies),
        "documents": documents,
    }


def write_bm25_index(index: dict[str, Any], index_path: Path = DEFAULT_BM25_INDEX_PATH) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index), encoding="utf-8")


def load_bm25_index(index_path: Path = DEFAULT_BM25_INDEX_PATH) -> dict[str, Any] | None:
    if not index_path.exists():
        return None
    return json.loads(index_path.read_text(encoding="utf-8"))


def metadata_matches_filters(metadata: dict[str, Any], filters: RetrievalFilters) -> bool:
    return _metadata_matches_pinecone_filter(metadata, filters.to_pinecone_filter())


def _metadata_matches_pinecone_filter(metadata: dict[str, Any], pinecone_filter: dict[str, object]) -> bool:
    for field, condition in pinecone_filter.items():
        value = metadata.get(field)
        if isinstance(condition, dict) and "$eq" in condition and value != condition["$eq"]:
            return False
        if isinstance(condition, dict) and "$in" in condition and value not in condition["$in"]:
            return False
    return True


def _score_document(query_tokens: list[str], document: dict[str, Any], index: dict[str, Any]) -> float:
    document_count = int(index.get("document_count", 0))
    average_length = float(index.get("average_document_length", 0.0))
    if not query_tokens or document_count == 0 or average_length == 0:
        return 0.0

    token_counts = document["token_counts"]
    document_length = int(document["length"])
    document_frequencies = index["document_frequencies"]
    k1 = float(index.get("k1", 1.5))
    b = float(index.get("b", 0.75))
    score = 0.0

    for token in set(query_tokens):
        term_frequency = int(token_counts.get(token, 0))
        if term_frequency == 0:
            continue
        document_frequency = int(document_frequencies.get(token, 0))
        idf = math.log(1 + (document_count - document_frequency + 0.5) / (document_frequency + 0.5))
        denominator = term_frequency + k1 * (1 - b + b * document_length / average_length)
        score += idf * (term_frequency * (k1 + 1)) / denominator
    return score


def search_bm25(
    index: dict[str, Any] | None,
    query: str,
    filters: RetrievalFilters,
    top_k: int = 25,
) -> list[dict[str, Any]]:
    if not index:
        return []

    query_tokens = tokenize(query)
    scored = []
    for document in index.get("documents", []):
        metadata = dict(document["metadata"])
        if not metadata_matches_filters(metadata, filters):
            continue
        score = _score_document(query_tokens, document, index)
        if score <= 0:
            continue
        metadata["bm25_score"] = score
        metadata["retrieval_method"] = "bm25"
        scored.append({"id": metadata.get("chunk_id"), "score": score, "metadata": metadata})

    return sorted(scored, key=lambda item: float(item["score"]), reverse=True)[:top_k]
