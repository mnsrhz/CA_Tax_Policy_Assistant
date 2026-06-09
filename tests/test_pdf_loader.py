from pathlib import Path

from src.pdf_loader import load_pdf_pages


def test_load_pdf_pages_extracts_pages_from_existing_corpus_pdf():
    pages = load_pdf_pages(Path("Data Corpus/2025-540-ca.pdf"))

    assert len(pages) >= 1
    assert pages[0].source_file == "2025-540-ca.pdf"
    assert pages[0].page_number == 1
    assert isinstance(pages[0].text, str)
