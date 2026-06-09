from src.models import RetrievalFilters
from src.retrieval import fallback_filters, merge_retrieval_candidates


def test_fallback_filters_relax_california_to_both():
    filters = RetrievalFilters(tax_year="2024", jurisdiction="california", agencies=["FTB"])

    widened = fallback_filters(filters)

    assert widened.jurisdiction == "both"
    assert widened.agencies == []


class Match:
    def __init__(self, metadata):
        self.metadata = metadata


def test_merge_retrieval_candidates_deduplicates_by_chunk_id_and_tracks_methods():
    vector_match = Match({"chunk_id": "same", "text": "Vector text", "vector_score": 0.8})
    bm25_match = {
        "metadata": {
            "chunk_id": "same",
            "text": "BM25 text",
            "display_title": "IRS Publication 587: Business Use of Your Home",
            "bm25_score": 3.2,
        }
    }
    bm25_only = {"metadata": {"chunk_id": "keyword", "text": "Keyword text", "bm25_score": 1.7}}

    merged = merge_retrieval_candidates([vector_match], [bm25_match, bm25_only])

    assert [candidate["chunk_id"] for candidate in merged] == ["same", "keyword"]
    assert merged[0]["retrieval_method"] == "vector+bm25"
    assert merged[0]["text"] == "Vector text"
    assert merged[0]["display_title"] == "IRS Publication 587: Business Use of Your Home"
    assert merged[0]["bm25_score"] == 3.2
    assert merged[1]["retrieval_method"] == "bm25"
