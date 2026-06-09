from src.models import RetrievalFilters
from src.retrieval import fallback_filters


def test_fallback_filters_relax_california_to_both():
    filters = RetrievalFilters(tax_year="2024", jurisdiction="california", agencies=["FTB"])

    widened = fallback_filters(filters)

    assert widened.jurisdiction == "both"
    assert widened.agencies == []
