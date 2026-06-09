from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chunking import chunk_pages
from src.bm25 import DEFAULT_BM25_INDEX_PATH, build_bm25_index, write_bm25_index
from src.config import AppConfig
from src.embeddings import embed_texts
from src.metadata import detect_document_metadata
from src.pdf_loader import load_pdf_pages
from src.pinecone_store import PineconeStore


def discover_pdfs(corpus_dir: Path) -> list[Path]:
    return sorted(corpus_dir.glob("*.pdf"))


def required_indexing_values(config: AppConfig) -> list[str]:
    missing: list[str] = []
    if not config.pinecone_api_key:
        missing.append("PINECONE_API_KEY")
    if not config.pinecone_index_name:
        missing.append("PINECONE_INDEX_NAME")
    return missing


def index_corpus(corpus_dir: Path = Path("Data Corpus")) -> None:
    config = AppConfig.from_local_secrets_or_env()
    missing = required_indexing_values(config)
    if missing:
        raise RuntimeError(f"Missing required configuration values: {', '.join(missing)}")

    store = PineconeStore(api_key=config.pinecone_api_key, index_name=config.pinecone_index_name)
    all_chunks = []
    for pdf_path in discover_pdfs(corpus_dir):
        pages = load_pdf_pages(pdf_path)
        sample_text = pages[0].text if pages else ""
        metadata = detect_document_metadata(pdf_path.name, sample_text)
        chunks = chunk_pages(pages, metadata)
        all_chunks.extend(chunks)
        embeddings = embed_texts([chunk.text for chunk in chunks], model_name=config.embedding_model_name)
        store.upsert_chunks(chunks, embeddings)
        print(f"Indexed {len(chunks)} chunks from {pdf_path.name}")
    write_bm25_index(build_bm25_index(all_chunks), DEFAULT_BM25_INDEX_PATH)
    print(f"Wrote BM25 index with {len(all_chunks)} chunks to {DEFAULT_BM25_INDEX_PATH}")


if __name__ == "__main__":
    index_corpus()
