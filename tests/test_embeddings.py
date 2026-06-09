from src.embeddings import normalize_for_bge


def test_normalize_for_bge_adds_query_prefix():
    assert (
        normalize_for_bge("What is Form 540?", is_query=True)
        == "Represent this sentence for searching relevant passages: What is Form 540?"
    )


def test_normalize_for_bge_strips_documents_without_prefix():
    assert normalize_for_bge("  California tax text  ", is_query=False) == "California tax text"
