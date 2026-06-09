from pathlib import Path

from src.bm25 import build_bm25_index, load_bm25_index, search_bm25, write_bm25_index
from src.models import DocumentChunk, RetrievalFilters


def _chunk(chunk_id: str, text: str, jurisdiction: str = "federal", agency: str = "IRS") -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        text=text,
        source_file=f"{chunk_id}.pdf",
        source_title=f"Source {chunk_id}",
        page_number=1,
        tax_year="2024",
        jurisdiction=jurisdiction,
        agency=agency,
        document_type="publication",
        form_or_pub_number="587",
    )


def test_search_bm25_prioritizes_exact_lexical_matches():
    index = build_bm25_index(
        [
            _chunk("home-office", "Home office deduction requires exclusive and regular business use."),
            _chunk("rental", "Rental income and depreciation rules for residential real estate."),
        ]
    )

    results = search_bm25(index, "exclusive home office deduction", RetrievalFilters(tax_year="2024"), top_k=2)

    assert results[0]["metadata"]["chunk_id"] == "home-office"
    assert results[0]["metadata"]["retrieval_method"] == "bm25"
    assert results[0]["metadata"]["bm25_score"] > 0


def test_search_bm25_applies_metadata_filters():
    index = build_bm25_index(
        [
            _chunk("irs", "Standard deduction federal rules.", jurisdiction="federal", agency="IRS"),
            _chunk("ftb", "Standard deduction California rules.", jurisdiction="california", agency="FTB"),
        ]
    )

    results = search_bm25(
        index,
        "standard deduction",
        RetrievalFilters(tax_year="2024", jurisdiction="california", agencies=["FTB"]),
        top_k=5,
    )

    assert [result["metadata"]["chunk_id"] for result in results] == ["ftb"]


def test_bm25_index_round_trips_json(tmp_path: Path):
    index_path = tmp_path / "bm25_index.json"
    index = build_bm25_index([_chunk("p587", "Business use of your home.")])

    write_bm25_index(index, index_path)
    loaded = load_bm25_index(index_path)

    assert loaded["documents"][0]["metadata"]["chunk_id"] == "p587"
