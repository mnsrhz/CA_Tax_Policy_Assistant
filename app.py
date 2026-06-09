from __future__ import annotations

from html import escape

import streamlit as st

from src.config import AppConfig
from src.embeddings import embed_texts
from src.generation import generate_answer
from src.models import RetrievalFilters
from src.pinecone_store import PineconeStore
from src.reranking import rerank
from src.retrieval import retrieve_with_fallback
from src.ui import app_css, badge_html, retrieval_trace_summary, source_chip_html


st.set_page_config(page_title="CalTax Assistant", page_icon="⚖", layout="wide")


@st.cache_resource
def get_store(api_key: str, index_name: str) -> PineconeStore:
    return PineconeStore(api_key=api_key, index_name=index_name)


def _match_metadata(match) -> dict[str, object]:
    if hasattr(match, "metadata"):
        return dict(match.metadata)
    return dict(match.get("metadata", {}))


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

    query_vector = embed_texts([question], model_name=config.embedding_model_name, is_query=True)[0]
    store = get_store(config.pinecone_api_key, config.pinecone_index_name)
    matches, trace = retrieve_with_fallback(store, query_vector, filters)

    candidates = [_match_metadata(match) for match in matches]
    top_contexts = rerank(question, candidates, model_name=config.reranker_model_name)
    answer = generate_answer(config.openai_api_key, question, top_contexts)

    badges = [
        badge_html(f"Tax year: {tax_year}", "gold"),
        badge_html(f"Jurisdiction: {jurisdiction}", "blue"),
        badge_html(f"{len(top_contexts)} sources", "green"),
    ]
    st.markdown(f'<div class="ct-badges">{"".join(badges)}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        safe_answer = escape(answer, quote=True).replace("\n", "<br>")
        st.markdown(f'<div class="ct-answer">{safe_answer}</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="ct-disclaimer">For informational purposes only. '
            "Not a substitute for advice from a licensed tax professional.</p>",
            unsafe_allow_html=True,
        )
        source_chips = "".join(source_chip_html(context) for context in top_contexts)
        st.markdown(f'<div class="ct-source-row">{source_chips}</div>', unsafe_allow_html=True)
        with st.expander("Retrieval trace"):
            st.caption(retrieval_trace_summary(trace, len(top_contexts)))
            st.json(trace)


if __name__ == "__main__":
    main()
