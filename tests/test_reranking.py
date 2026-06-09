from src.reranking import select_top_contexts


def test_select_top_contexts_sorts_by_score():
    candidates = [
        {"text": "less relevant", "rerank_score": 0.1},
        {"text": "more relevant", "rerank_score": 0.9},
    ]

    selected = select_top_contexts(candidates, top_n=1)

    assert selected == [{"text": "more relevant", "rerank_score": 0.9}]
