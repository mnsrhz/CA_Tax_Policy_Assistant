from __future__ import annotations

import streamlit as st

from src.bm25 import DEFAULT_BM25_INDEX_PATH, load_bm25_index
from src.config import AppConfig
from src.embeddings import embed_texts
from src.generation import generate_answer
from src.models import RetrievalFilters
from src.pinecone_store import PineconeStore
from src.reranking import rerank
from src.retrieval import retrieve_hybrid_with_fallback
from src.ui import answer_card_html, app_css, badge_html, retrieval_trace_html, source_chip_html


st.set_page_config(page_title="CalTax Assistant", page_icon="⚖", layout="wide")


@st.cache_resource
def get_store(api_key: str, index_name: str) -> PineconeStore:
    return PineconeStore(api_key=api_key, index_name=index_name)


@st.cache_resource
def get_bm25_index():
    return load_bm25_index(DEFAULT_BM25_INDEX_PATH)


def main() -> None:
    config = AppConfig.from_streamlit_secrets_or_env(st.secrets)
    st.markdown(app_css(), unsafe_allow_html=True)
    st.markdown(
        """
<header class="ct-header">
  <h1 class="ct-title">CalTax Assistant</h1>
  <p class="ct-subtitle">Educational RAG assistant for California and federal tax documents.</p>
</header>
""".strip(),
        unsafe_allow_html=True,
    )

    missing = config.missing_required_values()
    if missing:
        st.warning(f"Missing required secrets: {', '.join(missing)}")
        return

    with st.sidebar:
        st.subheader("Filters")
        tax_year = st.selectbox("Tax year", ["2024", "2025", "All"], index=0)
        jurisdiction = st.segmented_control("Jurisdiction", ["California", "Federal", "Both"], default="Both")
        document_type = st.selectbox("Document type", ["All", "Forms", "Instructions", "Publications", "Booklets"])
        source_scope = st.selectbox("Source scope", ["All sources", "IRS only", "FTB only"])

    question = st.chat_input("Ask a California tax question...")
    if not question:
        st.info("Ask a question to retrieve sources and generate an answer.")
        return

    st.chat_message("user").write(question)

    doc_type_map = {
        "Forms": ["form"],
        "Instructions": ["instructions"],
        "Publications": ["publication"],
        "Booklets": ["booklet"],
    }
    agency_map = {"IRS only": ["IRS"], "FTB only": ["FTB"]}
    filters = RetrievalFilters(
        tax_year=None if tax_year == "All" else tax_year,
        jurisdiction=str(jurisdiction).lower(),
        document_types=doc_type_map.get(document_type, []),
        agencies=agency_map.get(source_scope, []),
    )

    with st.spinner("Retrieving sources, reranking, and drafting answer..."):
        query_vector = embed_texts([question], model_name=config.embedding_model_name, is_query=True)[0]
        store = get_store(config.pinecone_api_key, config.pinecone_index_name)
        bm25_index = get_bm25_index()
        candidates, trace = retrieve_hybrid_with_fallback(store, query_vector, question, filters, bm25_index)

        top_contexts = rerank(question, candidates, model_name=config.reranker_model_name)
        answer = generate_answer(config.openai_api_key, question, top_contexts)

    badges = [
        badge_html(f"Tax year: {tax_year}", "gold"),
        badge_html(f"Jurisdiction: {jurisdiction}", "blue"),
        badge_html(f"{len(top_contexts)} sources", "green"),
    ]
    st.markdown(f'<div class="ct-badges">{"".join(badges)}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        st.markdown(answer_card_html(answer, len(top_contexts), tax_year), unsafe_allow_html=True)
        source_chips = "".join(source_chip_html(context) for context in top_contexts)
        st.markdown(f'<div class="ct-source-row">{source_chips}</div>', unsafe_allow_html=True)
        st.markdown(
            retrieval_trace_html(
                trace=trace,
                tax_year=tax_year,
                jurisdiction=str(jurisdiction),
                source_count=len(top_contexts),
            ),
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
