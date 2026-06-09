from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.bm25 import DEFAULT_BM25_INDEX_PATH, build_bm25_index, write_bm25_index
from src.chunking import chunk_pages
from src.metadata import detect_document_metadata
from src.pdf_loader import load_pdf_pages


def discover_pdfs(corpus_dir: Path) -> list[Path]:
    return sorted(corpus_dir.glob("*.pdf"))


def build_local_bm25_index(corpus_dir: Path = Path("Data Corpus"), index_path: Path = DEFAULT_BM25_INDEX_PATH) -> None:
    all_chunks = []
    for pdf_path in discover_pdfs(corpus_dir):
        pages = load_pdf_pages(pdf_path)
        sample_text = pages[0].text if pages else ""
        metadata = detect_document_metadata(pdf_path.name, sample_text)
        all_chunks.extend(chunk_pages(pages, metadata))
    write_bm25_index(build_bm25_index(all_chunks), index_path)
    print(f"Wrote BM25 index with {len(all_chunks)} chunks to {index_path}")


if __name__ == "__main__":
    build_local_bm25_index()
