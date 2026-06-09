# California Tax Policy Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Streamlit RAG assistant that indexes the provided tax PDFs into Pinecone and answers questions with metadata-filtered retrieval, reranking, citations, and OpenAI response generation.

**Architecture:** The app is split into an offline indexing flow and a runtime Streamlit Q&A flow. Focused modules under `src/` handle PDF extraction, metadata, chunking, embeddings, Pinecone access, retrieval, reranking, generation, and UI helpers. Tests validate each module before it is wired into the app.

**Tech Stack:** Python, Streamlit, PyMuPDF, sentence-transformers, Pinecone, OpenAI API, pytest.

---

## File Structure

Create or modify these files:

- `requirements.txt`: Python dependencies.
- `.streamlit/config.toml`: Streamlit theme and basic config.
- `app.py`: Streamlit entry point.
- `src/__init__.py`: package marker.
- `src/config.py`: environment and Streamlit secrets loading.
- `src/models.py`: shared dataclasses for pages, chunks, retrieval results, and filters.
- `src/pdf_loader.py`: page-level PDF extraction.
- `src/metadata.py`: document metadata detection and query filter conversion.
- `src/chunking.py`: structure-aware semantic chunking.
- `src/embeddings.py`: local embedding model wrapper.
- `src/pinecone_store.py`: Pinecone index and vector operations.
- `src/retrieval.py`: metadata-filtered retrieval and fallback widening.
- `src/reranking.py`: local reranker wrapper.
- `src/generation.py`: OpenAI answer generation.
- `src/ui.py`: Streamlit layout and styling helpers.
- `scripts/index_corpus.py`: offline indexing script.
- `tests/`: focused pytest coverage.
- `README.md`: update with concrete setup commands once implementation exists.

## Task 1: Project Skeleton And Shared Models

**Files:**
- Create: `requirements.txt`
- Create: `.streamlit/config.toml`
- Create: `src/__init__.py`
- Create: `src/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write shared model tests**

Create `tests/test_models.py`:

```python
from src.models import DocumentChunk, PageText, RetrievalFilters


def test_document_chunk_metadata_payload_contains_source_fields():
    chunk = DocumentChunk(
        chunk_id="p587-4-0",
        text="A home office must be used exclusively and regularly.",
        source_file="p587.pdf",
        source_title="IRS Publication 587",
        page_number=4,
        tax_year="2024",
        jurisdiction="federal",
        agency="IRS",
        document_type="publication",
        form_or_pub_number="587",
        section_heading="Business Use of Your Home",
        topic_tags=["home_office"],
    )

    payload = chunk.to_pinecone_metadata()

    assert payload["source_file"] == "p587.pdf"
    assert payload["page_number"] == 4
    assert payload["agency"] == "IRS"
    assert payload["text"] == chunk.text


def test_retrieval_filters_convert_to_pinecone_filter():
    filters = RetrievalFilters(
        tax_year="2024",
        jurisdiction="california",
        document_types=["instructions", "booklet"],
        agencies=["FTB"],
    )

    pinecone_filter = filters.to_pinecone_filter()

    assert pinecone_filter == {
        "tax_year": {"$eq": "2024"},
        "jurisdiction": {"$in": ["california", "mixed"]},
        "document_type": {"$in": ["instructions", "booklet"]},
        "agency": {"$in": ["FTB"]},
    }


def test_page_text_normalizes_empty_text():
    page = PageText(source_file="p17.pdf", page_number=1, text="   ")
    assert page.text == ""
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models.py -v`

Expected: FAIL because `src.models` does not exist.

- [ ] **Step 3: Add dependencies and shared models**

Create `requirements.txt`:

```text
streamlit
pymupdf
sentence-transformers
pinecone
openai
pytest
python-dotenv
numpy
```

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#185FA5"
backgroundColor = "#F7F6F2"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1A1915"
font = "serif"
```

Create `src/__init__.py`:

```python
"""California Tax Policy Assistant package."""
```

Create `src/models.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PageText:
    source_file: str
    page_number: int
    text: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", self.text.strip())


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    text: str
    source_file: str
    source_title: str
    page_number: int
    tax_year: str
    jurisdiction: str
    agency: str
    document_type: str
    form_or_pub_number: str
    section_heading: str = ""
    topic_tags: list[str] = field(default_factory=list)

    def to_pinecone_metadata(self) -> dict[str, object]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "source_file": self.source_file,
            "source_title": self.source_title,
            "page_number": self.page_number,
            "tax_year": self.tax_year,
            "jurisdiction": self.jurisdiction,
            "agency": self.agency,
            "document_type": self.document_type,
            "form_or_pub_number": self.form_or_pub_number,
            "section_heading": self.section_heading,
            "topic_tags": self.topic_tags,
        }


@dataclass(frozen=True)
class RetrievalFilters:
    tax_year: str | None = None
    jurisdiction: str = "both"
    document_types: list[str] = field(default_factory=list)
    agencies: list[str] = field(default_factory=list)

    def to_pinecone_filter(self) -> dict[str, object]:
        pinecone_filter: dict[str, object] = {}
        if self.tax_year:
            pinecone_filter["tax_year"] = {"$eq": self.tax_year}
        if self.jurisdiction == "california":
            pinecone_filter["jurisdiction"] = {"$in": ["california", "mixed"]}
        elif self.jurisdiction == "federal":
            pinecone_filter["jurisdiction"] = {"$in": ["federal", "mixed"]}
        if self.document_types:
            pinecone_filter["document_type"] = {"$in": self.document_types}
        if self.agencies:
            pinecone_filter["agency"] = {"$in": self.agencies}
        return pinecone_filter
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_models.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .streamlit/config.toml src/__init__.py src/models.py tests/test_models.py
git commit -m "feat: add project skeleton and shared models"
```

## Task 2: Configuration Loading

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write configuration tests**

Create `tests/test_config.py`:

```python
import os

from src.config import AppConfig


def test_config_reads_environment_values(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("PINECONE_API_KEY", "pinecone-key")
    monkeypatch.setenv("PINECONE_INDEX_NAME", "tax-index")

    config = AppConfig.from_env()

    assert config.openai_api_key == "openai-key"
    assert config.pinecone_api_key == "pinecone-key"
    assert config.pinecone_index_name == "tax-index"


def test_missing_required_values_are_reported(monkeypatch):
    for key in ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]:
        monkeypatch.delenv(key, raising=False)

    config = AppConfig.from_env()

    assert config.missing_required_values() == [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_INDEX_NAME",
    ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_config.py -v`

Expected: FAIL because `src.config` does not exist.

- [ ] **Step 3: Implement configuration loading**

Create `src/config.py`:

```python
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_index_name: str = ""
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            pinecone_api_key=os.getenv("PINECONE_API_KEY", ""),
            pinecone_index_name=os.getenv("PINECONE_INDEX_NAME", ""),
            embedding_model_name=os.getenv("EMBEDDING_MODEL_NAME", cls.embedding_model_name),
            reranker_model_name=os.getenv("RERANKER_MODEL_NAME", cls.reranker_model_name),
        )

    def missing_required_values(self) -> list[str]:
        missing: list[str] = []
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.pinecone_api_key:
            missing.append("PINECONE_API_KEY")
        if not self.pinecone_index_name:
            missing.append("PINECONE_INDEX_NAME")
        return missing
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_config.py tests/test_models.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add app configuration loading"
```

## Task 3: PDF Extraction And Metadata

**Files:**
- Create: `src/pdf_loader.py`
- Create: `src/metadata.py`
- Create: `tests/test_pdf_loader.py`
- Create: `tests/test_metadata.py`

- [ ] **Step 1: Write metadata tests**

Create `tests/test_metadata.py`:

```python
from src.metadata import detect_document_metadata


def test_detects_irs_publication_metadata():
    metadata = detect_document_metadata("p587.pdf", "Publication 587 Business Use of Your Home")

    assert metadata["agency"] == "IRS"
    assert metadata["jurisdiction"] == "federal"
    assert metadata["document_type"] == "publication"
    assert metadata["form_or_pub_number"] == "587"


def test_detects_ftb_form_metadata():
    metadata = detect_document_metadata("2025-540-ca-instructions.pdf", "Schedule CA Instructions")

    assert metadata["agency"] == "FTB"
    assert metadata["jurisdiction"] == "california"
    assert metadata["document_type"] == "instructions"
    assert metadata["form_or_pub_number"] == "540"
    assert metadata["tax_year"] == "2025"
```

- [ ] **Step 2: Write PDF loader test**

Create `tests/test_pdf_loader.py`:

```python
from pathlib import Path

from src.pdf_loader import load_pdf_pages


def test_load_pdf_pages_extracts_pages_from_existing_corpus_pdf():
    pages = load_pdf_pages(Path("Data Corpus/2025-540-ca.pdf"))

    assert len(pages) >= 1
    assert pages[0].source_file == "2025-540-ca.pdf"
    assert pages[0].page_number == 1
    assert isinstance(pages[0].text, str)
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_metadata.py tests/test_pdf_loader.py -v`

Expected: FAIL because modules do not exist.

- [ ] **Step 4: Implement metadata and PDF loading**

Create `src/metadata.py`:

```python
from __future__ import annotations

import re


def detect_document_metadata(source_file: str, sample_text: str = "") -> dict[str, str]:
    filename = source_file.lower()
    text = sample_text.lower()
    combined = f"{filename} {text}"

    tax_year_match = re.search(r"(20\d{2})", filename)
    tax_year = tax_year_match.group(1) if tax_year_match else "unknown"

    agency = "FTB" if filename.startswith("202") or "california" in combined or "schedule ca" in combined else "IRS"
    jurisdiction = "california" if agency == "FTB" else "federal"

    if "instructions" in combined:
        document_type = "instructions"
    elif "booklet" in combined:
        document_type = "booklet"
    elif "publication" in combined or re.match(r"p\d+\.pdf", filename) or filename.startswith("pub"):
        document_type = "publication"
    elif "form" in combined or re.search(r"540", filename):
        document_type = "form"
    else:
        document_type = "unknown"

    number_match = re.search(r"(?:p|pub)?(\d{2,4})", filename)
    form_or_pub_number = number_match.group(1) if number_match else "unknown"

    return {
        "source_title": source_file.replace(".pdf", "").replace("-", " "),
        "tax_year": tax_year,
        "agency": agency,
        "jurisdiction": jurisdiction,
        "document_type": document_type,
        "form_or_pub_number": form_or_pub_number,
    }
```

Create `src/pdf_loader.py`:

```python
from __future__ import annotations

from pathlib import Path

import fitz

from src.models import PageText


def load_pdf_pages(pdf_path: Path) -> list[PageText]:
    document = fitz.open(pdf_path)
    pages: list[PageText] = []
    try:
        for index, page in enumerate(document, start=1):
            text = page.get_text("text")
            pages.append(PageText(source_file=pdf_path.name, page_number=index, text=text))
    finally:
        document.close()
    return pages
```

- [ ] **Step 5: Run tests**

Run: `pytest tests/test_metadata.py tests/test_pdf_loader.py tests/test_models.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/pdf_loader.py src/metadata.py tests/test_pdf_loader.py tests/test_metadata.py
git commit -m "feat: extract PDF text and document metadata"
```

## Task 4: Semantic Chunking

**Files:**
- Create: `src/chunking.py`
- Create: `tests/test_chunking.py`

- [ ] **Step 1: Write chunking tests**

Create `tests/test_chunking.py`:

```python
from src.chunking import chunk_pages
from src.models import PageText


def test_chunk_pages_preserves_metadata_and_page_number():
    pages = [
        PageText(
            source_file="p587.pdf",
            page_number=4,
            text="Business Use of Your Home\n\nExclusive use rule applies.\n\nRegular use rule applies.",
        )
    ]
    metadata = {
        "source_title": "IRS Publication 587",
        "tax_year": "2024",
        "agency": "IRS",
        "jurisdiction": "federal",
        "document_type": "publication",
        "form_or_pub_number": "587",
    }

    chunks = chunk_pages(pages, metadata, max_chars=120)

    assert len(chunks) >= 1
    assert chunks[0].source_file == "p587.pdf"
    assert chunks[0].page_number == 4
    assert chunks[0].section_heading == "Business Use of Your Home"
    assert "Exclusive use" in chunks[0].text


def test_chunk_pages_splits_large_text():
    text = "\n\n".join([f"Paragraph {index} discusses estimated tax payments." for index in range(20)])
    pages = [PageText(source_file="p505.pdf", page_number=2, text=text)]
    metadata = {
        "source_title": "IRS Publication 505",
        "tax_year": "2024",
        "agency": "IRS",
        "jurisdiction": "federal",
        "document_type": "publication",
        "form_or_pub_number": "505",
    }

    chunks = chunk_pages(pages, metadata, max_chars=250)

    assert len(chunks) > 1
    assert all(len(chunk.text) <= 320 for chunk in chunks)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_chunking.py -v`

Expected: FAIL because `src.chunking` does not exist.

- [ ] **Step 3: Implement chunking**

Create `src/chunking.py`:

```python
from __future__ import annotations

import re

from src.models import DocumentChunk, PageText


def _paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]


def _looks_like_heading(paragraph: str) -> bool:
    words = paragraph.split()
    return 2 <= len(words) <= 12 and len(paragraph) <= 90 and not paragraph.endswith(".")


def chunk_pages(
    pages: list[PageText],
    metadata: dict[str, str],
    max_chars: int = 1400,
) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for page in pages:
        section_heading = ""
        current_parts: list[str] = []

        def flush() -> None:
            if not current_parts:
                return
            chunk_text = "\n\n".join(current_parts).strip()
            chunk_index = len(chunks)
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{page.source_file}:p{page.page_number}:{chunk_index}",
                    text=chunk_text,
                    source_file=page.source_file,
                    source_title=metadata["source_title"],
                    page_number=page.page_number,
                    tax_year=metadata["tax_year"],
                    jurisdiction=metadata["jurisdiction"],
                    agency=metadata["agency"],
                    document_type=metadata["document_type"],
                    form_or_pub_number=metadata["form_or_pub_number"],
                    section_heading=section_heading,
                    topic_tags=[],
                )
            )
            current_parts.clear()

        for paragraph in _paragraphs(page.text):
            if _looks_like_heading(paragraph):
                if current_parts:
                    flush()
                section_heading = paragraph
                continue
            proposed = "\n\n".join([*current_parts, paragraph])
            if current_parts and len(proposed) > max_chars:
                flush()
            current_parts.append(paragraph)
        flush()
    return chunks
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_chunking.py tests/test_models.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/chunking.py tests/test_chunking.py
git commit -m "feat: add structure-aware chunking"
```

## Task 5: Embeddings And Pinecone Store

**Files:**
- Create: `src/embeddings.py`
- Create: `src/pinecone_store.py`
- Create: `tests/test_embeddings.py`
- Create: `tests/test_pinecone_store.py`

- [ ] **Step 1: Write lightweight tests**

Create `tests/test_embeddings.py`:

```python
from src.embeddings import normalize_for_bge


def test_normalize_for_bge_adds_query_prefix():
    assert normalize_for_bge("What is Form 540?", is_query=True) == "Represent this sentence for searching relevant passages: What is Form 540?"


def test_normalize_for_bge_strips_documents_without_prefix():
    assert normalize_for_bge("  California tax text  ", is_query=False) == "California tax text"
```

Create `tests/test_pinecone_store.py`:

```python
from src.models import DocumentChunk
from src.pinecone_store import vectors_for_chunks


def test_vectors_for_chunks_builds_pinecone_payloads():
    chunk = DocumentChunk(
        chunk_id="one",
        text="California standard deduction information.",
        source_file="2024-540-booklet.pdf",
        source_title="2024 540 Booklet",
        page_number=10,
        tax_year="2024",
        jurisdiction="california",
        agency="FTB",
        document_type="booklet",
        form_or_pub_number="540",
    )

    vectors = vectors_for_chunks([chunk], [[0.1, 0.2, 0.3]])

    assert vectors == [
        {
            "id": "one",
            "values": [0.1, 0.2, 0.3],
            "metadata": chunk.to_pinecone_metadata(),
        }
    ]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_embeddings.py tests/test_pinecone_store.py -v`

Expected: FAIL because modules do not exist.

- [ ] **Step 3: Implement embedding helpers and Pinecone payloads**

Create `src/embeddings.py`:

```python
from __future__ import annotations

from functools import lru_cache


QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def normalize_for_bge(text: str, is_query: bool) -> str:
    stripped = text.strip()
    return f"{QUERY_PREFIX}{stripped}" if is_query else stripped


@lru_cache(maxsize=1)
def load_embedding_model(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def embed_texts(texts: list[str], model_name: str, is_query: bool = False) -> list[list[float]]:
    model = load_embedding_model(model_name)
    normalized = [normalize_for_bge(text, is_query=is_query) for text in texts]
    embeddings = model.encode(normalized, normalize_embeddings=True)
    return embeddings.tolist()
```

Create `src/pinecone_store.py`:

```python
from __future__ import annotations

from collections.abc import Iterable

from pinecone import Pinecone

from src.models import DocumentChunk


def vectors_for_chunks(chunks: list[DocumentChunk], embeddings: list[list[float]]) -> list[dict[str, object]]:
    return [
        {
            "id": chunk.chunk_id,
            "values": embedding,
            "metadata": chunk.to_pinecone_metadata(),
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]


def batched(items: list[dict[str, object]], batch_size: int) -> Iterable[list[dict[str, object]]]:
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


class PineconeStore:
    def __init__(self, api_key: str, index_name: str) -> None:
        self.client = Pinecone(api_key=api_key)
        self.index = self.client.Index(index_name)

    def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]], batch_size: int = 100) -> None:
        vectors = vectors_for_chunks(chunks, embeddings)
        for batch in batched(vectors, batch_size):
            self.index.upsert(vectors=batch)

    def query(self, vector: list[float], top_k: int, metadata_filter: dict[str, object] | None = None):
        return self.index.query(vector=vector, top_k=top_k, filter=metadata_filter or {}, include_metadata=True)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_embeddings.py tests/test_pinecone_store.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/embeddings.py src/pinecone_store.py tests/test_embeddings.py tests/test_pinecone_store.py
git commit -m "feat: add embeddings and Pinecone payloads"
```

## Task 6: Retrieval Fallback And Reranking

**Files:**
- Create: `src/retrieval.py`
- Create: `src/reranking.py`
- Create: `tests/test_retrieval.py`
- Create: `tests/test_reranking.py`

- [ ] **Step 1: Write retrieval and reranking tests**

Create `tests/test_retrieval.py`:

```python
from src.models import RetrievalFilters
from src.retrieval import fallback_filters


def test_fallback_filters_relax_california_to_both():
    filters = RetrievalFilters(tax_year="2024", jurisdiction="california", agencies=["FTB"])

    widened = fallback_filters(filters)

    assert widened.jurisdiction == "both"
    assert widened.agencies == []
```

Create `tests/test_reranking.py`:

```python
from src.reranking import select_top_contexts


def test_select_top_contexts_sorts_by_score():
    candidates = [
        {"text": "less relevant", "rerank_score": 0.1},
        {"text": "more relevant", "rerank_score": 0.9},
    ]

    selected = select_top_contexts(candidates, top_n=1)

    assert selected == [{"text": "more relevant", "rerank_score": 0.9}]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_retrieval.py tests/test_reranking.py -v`

Expected: FAIL because modules do not exist.

- [ ] **Step 3: Implement retrieval helpers and reranker**

Create `src/retrieval.py`:

```python
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


def retrieve_with_fallback(store, query_vector: list[float], filters: RetrievalFilters, top_k: int = 25, min_results: int = 5):
    trace = [{"stage": "strict", "filter": filters.to_pinecone_filter()}]
    response = store.query(query_vector, top_k=top_k, metadata_filter=filters.to_pinecone_filter())
    matches = response_matches(response)
    if len(matches) >= min_results:
        return matches, trace

    widened = fallback_filters(filters)
    trace.append({"stage": "fallback", "filter": widened.to_pinecone_filter()})
    response = store.query(query_vector, top_k=top_k, metadata_filter=widened.to_pinecone_filter())
    return response_matches(response), trace
```

Create `src/reranking.py`:

```python
from __future__ import annotations

from functools import lru_cache


def select_top_contexts(candidates: list[dict[str, object]], top_n: int) -> list[dict[str, object]]:
    return sorted(candidates, key=lambda item: float(item.get("rerank_score", 0.0)), reverse=True)[:top_n]


@lru_cache(maxsize=1)
def load_reranker(model_name: str):
    from sentence_transformers import CrossEncoder

    return CrossEncoder(model_name)


def rerank(query: str, candidates: list[dict[str, object]], model_name: str, top_n: int = 6) -> list[dict[str, object]]:
    model = load_reranker(model_name)
    pairs = [(query, str(candidate["text"])) for candidate in candidates]
    scores = model.predict(pairs)
    scored = []
    for candidate, score in zip(candidates, scores):
        updated = dict(candidate)
        updated["rerank_score"] = float(score)
        scored.append(updated)
    return select_top_contexts(scored, top_n=top_n)
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_retrieval.py tests/test_reranking.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/retrieval.py src/reranking.py tests/test_retrieval.py tests/test_reranking.py
git commit -m "feat: add retrieval fallback and reranking"
```

## Task 7: OpenAI Generation

**Files:**
- Create: `src/generation.py`
- Create: `tests/test_generation.py`

- [ ] **Step 1: Write prompt tests**

Create `tests/test_generation.py`:

```python
from src.generation import build_answer_prompt


def test_build_answer_prompt_includes_citation_rules_and_context():
    prompt = build_answer_prompt(
        question="Can I deduct home office expenses?",
        contexts=[
            {
                "text": "W-2 employees cannot deduct unreimbursed employee expenses.",
                "source_title": "IRS Publication 529",
                "page_number": 8,
                "agency": "IRS",
            }
        ],
    )

    assert "answer only from the retrieved context" in prompt.lower()
    assert "IRS Publication 529, page 8" in prompt
    assert "Can I deduct home office expenses?" in prompt
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_generation.py -v`

Expected: FAIL because `src.generation` does not exist.

- [ ] **Step 3: Implement prompt and generation wrapper**

Create `src/generation.py`:

```python
from __future__ import annotations

from openai import OpenAI


def build_answer_prompt(question: str, contexts: list[dict[str, object]]) -> str:
    context_blocks = []
    for index, context in enumerate(contexts, start=1):
        source_title = context.get("source_title", context.get("source_file", "Unknown source"))
        page_number = context.get("page_number", "unknown")
        agency = context.get("agency", "unknown")
        text = context.get("text", "")
        context_blocks.append(
            f"[Source {index}: {source_title}, page {page_number}, agency {agency}]\n{text}"
        )

    joined_context = "\n\n".join(context_blocks)
    return f"""You are a California tax policy assistant for educational use.

Answer only from the retrieved context. Cite source document and page for specific claims.
Distinguish federal IRS guidance from California FTB guidance. If the context does not support an answer, say so.
Do not invent thresholds, deadlines, forms, or eligibility rules. Include a brief informational disclaimer.

Question:
{question}

Retrieved context:
{joined_context}
"""


def generate_answer(openai_api_key: str, question: str, contexts: list[dict[str, object]], model: str = "gpt-4.1-mini") -> str:
    client = OpenAI(api_key=openai_api_key)
    response = client.responses.create(
        model=model,
        input=build_answer_prompt(question=question, contexts=contexts),
    )
    return response.output_text
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_generation.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/generation.py tests/test_generation.py
git commit -m "feat: add OpenAI answer generation"
```

## Task 8: Offline Indexing Script

**Files:**
- Create: `scripts/index_corpus.py`
- Create: `tests/test_index_corpus.py`

- [ ] **Step 1: Write indexing discovery test**

Create `tests/test_index_corpus.py`:

```python
from pathlib import Path

from scripts.index_corpus import discover_pdfs


def test_discover_pdfs_returns_sorted_pdf_paths():
    paths = discover_pdfs(Path("Data Corpus"))

    assert paths
    assert paths == sorted(paths)
    assert all(path.suffix == ".pdf" for path in paths)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_index_corpus.py -v`

Expected: FAIL because `scripts.index_corpus` does not exist.

- [ ] **Step 3: Implement indexing script**

Create `scripts/index_corpus.py`:

```python
from __future__ import annotations

from pathlib import Path

from src.chunking import chunk_pages
from src.config import AppConfig
from src.embeddings import embed_texts
from src.metadata import detect_document_metadata
from src.pdf_loader import load_pdf_pages
from src.pinecone_store import PineconeStore


def discover_pdfs(corpus_dir: Path) -> list[Path]:
    return sorted(corpus_dir.glob("*.pdf"))


def index_corpus(corpus_dir: Path = Path("Data Corpus")) -> None:
    config = AppConfig.from_env()
    missing = config.missing_required_values()
    if missing:
        raise RuntimeError(f"Missing required configuration values: {', '.join(missing)}")

    store = PineconeStore(api_key=config.pinecone_api_key, index_name=config.pinecone_index_name)
    for pdf_path in discover_pdfs(corpus_dir):
        pages = load_pdf_pages(pdf_path)
        sample_text = pages[0].text if pages else ""
        metadata = detect_document_metadata(pdf_path.name, sample_text)
        chunks = chunk_pages(pages, metadata)
        embeddings = embed_texts([chunk.text for chunk in chunks], model_name=config.embedding_model_name)
        store.upsert_chunks(chunks, embeddings)
        print(f"Indexed {len(chunks)} chunks from {pdf_path.name}")


if __name__ == "__main__":
    index_corpus()
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_index_corpus.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/index_corpus.py tests/test_index_corpus.py
git commit -m "feat: add corpus indexing script"
```

## Task 9: Streamlit UI And App Wiring

**Files:**
- Create: `src/ui.py`
- Create: `app.py`
- Create: `tests/test_ui.py`

- [ ] **Step 1: Write UI helper test**

Create `tests/test_ui.py`:

```python
from src.ui import source_label


def test_source_label_formats_document_page():
    label = source_label({"source_title": "IRS Publication 587", "page_number": 4})

    assert label == "IRS Publication 587 · p.4"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ui.py -v`

Expected: FAIL because `src.ui` does not exist.

- [ ] **Step 3: Implement UI helper and Streamlit app**

Create `src/ui.py`:

```python
from __future__ import annotations


def source_label(metadata: dict[str, object]) -> str:
    title = metadata.get("source_title", metadata.get("source_file", "Unknown source"))
    page = metadata.get("page_number", "?")
    return f"{title} · p.{page}"
```

Create `app.py`:

```python
from __future__ import annotations

import streamlit as st

from src.config import AppConfig
from src.embeddings import embed_texts
from src.generation import generate_answer
from src.models import RetrievalFilters
from src.pinecone_store import PineconeStore
from src.reranking import rerank
from src.retrieval import retrieve_with_fallback
from src.ui import source_label


st.set_page_config(page_title="CalTax Assistant", page_icon="⚖", layout="wide")


@st.cache_resource
def get_store(api_key: str, index_name: str) -> PineconeStore:
    return PineconeStore(api_key=api_key, index_name=index_name)


def main() -> None:
    config = AppConfig.from_env()
    st.title("CalTax Assistant")
    st.caption("Educational RAG assistant for California and federal tax documents.")

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
        jurisdiction=jurisdiction.lower(),
        document_types=doc_type_map.get(document_type, []),
        agencies=agency_map.get(source_scope, []),
    )

    query_vector = embed_texts([question], model_name=config.embedding_model_name, is_query=True)[0]
    store = get_store(config.pinecone_api_key, config.pinecone_index_name)
    matches, trace = retrieve_with_fallback(store, query_vector, filters)

    candidates = []
    for match in matches:
        if hasattr(match, "metadata"):
            metadata = dict(match.metadata)
        else:
            metadata = dict(match.get("metadata", {}))
        candidates.append(metadata)

    top_contexts = rerank(question, candidates, model_name=config.reranker_model_name)
    answer = generate_answer(config.openai_api_key, question, top_contexts)

    with st.chat_message("assistant"):
        st.write(answer)
        st.caption("For informational purposes only. Not a substitute for advice from a licensed tax professional.")
        st.write("Sources")
        for context in top_contexts:
            st.markdown(f"- {source_label(context)}")
        with st.expander("Retrieval trace"):
            st.json(trace)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_ui.py -v`

Expected: PASS.

- [ ] **Step 5: Run the app smoke check**

Run: `streamlit run app.py`

Expected: App starts and shows missing-secrets warning if secrets are not configured.

- [ ] **Step 6: Commit**

```bash
git add app.py src/ui.py tests/test_ui.py
git commit -m "feat: add Streamlit assistant UI"
```

## Task 10: README Update And Deployment Checklist

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README with concrete commands**

Modify `README.md` to include:

```markdown
## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Local Secrets

Create `.streamlit/secrets.toml` for local Streamlit runs:

```toml
OPENAI_API_KEY = "..."
PINECONE_API_KEY = "..."
PINECONE_INDEX_NAME = "..."
```

## Run Tests

```bash
pytest -v
```

## Index Corpus

```bash
python scripts/index_corpus.py
```

## Run App

```bash
streamlit run app.py
```
```

- [ ] **Step 2: Run the full test suite**

Run: `pytest -v`

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add setup and deployment instructions"
```

## Final Verification

- [ ] Run `pytest -v`; expected PASS.
- [ ] Run `streamlit run app.py`; expected app starts.
- [ ] Run `python scripts/index_corpus.py` after Pinecone secrets are configured; expected PDFs are indexed into Pinecone.
- [ ] Confirm `git status --short` is clean.
