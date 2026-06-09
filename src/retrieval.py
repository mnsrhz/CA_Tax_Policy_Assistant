from __future__ import annotations

from dataclasses import replace
from typing import Any

from src.bm25 import search_bm25
from src.models import RetrievalFilters


def fallback_filters(filters: RetrievalFilters) -> RetrievalFilters:
    if filters.jurisdiction in {"california", "federal"}:
        return replace(filters, jurisdiction="both", agencies=[])
    if filters.document_types:
        return replace(filters, document_types=[])
    return filters


def response_matches(response) -> list[object]:
    if hasattr(response, "matches"):
        return list(response.matches)
    return list(response.get("matches", []))


def match_metadata(match) -> dict[str, Any]:
    if hasattr(match, "metadata"):
        return dict(match.metadata)
    return dict(match.get("metadata", {}))


def merge_retrieval_candidates(vector_matches: list[object], bm25_matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    order: list[str] = []

    for match in vector_matches:
        metadata = match_metadata(match)
        chunk_id = str(metadata.get("chunk_id", ""))
        if not chunk_id:
            continue
        metadata["retrieval_method"] = "vector"
        if hasattr(match, "score"):
            metadata["vector_score"] = float(match.score)
        merged[chunk_id] = metadata
        order.append(chunk_id)

    for match in bm25_matches:
        metadata = match_metadata(match)
        chunk_id = str(metadata.get("chunk_id", ""))
        if not chunk_id:
            continue
        if chunk_id in merged:
            merged[chunk_id]["retrieval_method"] = "vector+bm25"
            if "bm25_score" in metadata:
                merged[chunk_id]["bm25_score"] = metadata["bm25_score"]
            if metadata.get("display_title") and not merged[chunk_id].get("display_title"):
                merged[chunk_id]["display_title"] = metadata["display_title"]
        else:
            metadata["retrieval_method"] = metadata.get("retrieval_method", "bm25")
            merged[chunk_id] = metadata
            order.append(chunk_id)

    return [merged[chunk_id] for chunk_id in order]


def retrieve_with_fallback(
    store,
    query_vector: list[float],
    filters: RetrievalFilters,
    top_k: int = 25,
    min_results: int = 5,
):
    trace = [{"stage": "strict", "filter": filters.to_pinecone_filter()}]
    response = store.query(query_vector, top_k=top_k, metadata_filter=filters.to_pinecone_filter())
    matches = response_matches(response)
    if len(matches) >= min_results:
        return matches, trace

    widened = fallback_filters(filters)
    trace.append({"stage": "fallback", "filter": widened.to_pinecone_filter()})
    response = store.query(query_vector, top_k=top_k, metadata_filter=widened.to_pinecone_filter())
    return response_matches(response), trace


def retrieve_hybrid_with_fallback(
    store,
    query_vector: list[float],
    query_text: str,
    filters: RetrievalFilters,
    bm25_index: dict[str, Any] | None,
    top_k: int = 25,
    min_results: int = 5,
) -> tuple[list[dict[str, Any]], list[dict[str, object]]]:
    trace = [{"stage": "strict", "filter": filters.to_pinecone_filter()}]
    response = store.query(query_vector, top_k=top_k, metadata_filter=filters.to_pinecone_filter())
    vector_matches = response_matches(response)
    bm25_matches = search_bm25(bm25_index, query_text, filters, top_k=top_k)
    merged = merge_retrieval_candidates(vector_matches, bm25_matches)
    trace[-1].update(
        {
            "vector_hits": len(vector_matches),
            "bm25_hits": len(bm25_matches),
            "merged_candidates": len(merged),
        }
    )
    if len(merged) >= min_results:
        return merged, trace

    widened = fallback_filters(filters)
    trace.append({"stage": "fallback", "filter": widened.to_pinecone_filter()})
    response = store.query(query_vector, top_k=top_k, metadata_filter=widened.to_pinecone_filter())
    vector_matches = response_matches(response)
    bm25_matches = search_bm25(bm25_index, query_text, widened, top_k=top_k)
    merged = merge_retrieval_candidates(vector_matches, bm25_matches)
    trace[-1].update(
        {
            "vector_hits": len(vector_matches),
            "bm25_hits": len(bm25_matches),
            "merged_candidates": len(merged),
        }
    )
    return merged, trace
