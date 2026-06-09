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
