from __future__ import annotations

from dataclasses import replace

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
