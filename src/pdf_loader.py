from __future__ import annotations

from pathlib import Path

import fitz

from src.models import PageText
from src.table_extraction import blocks_outside_tables, should_detect_tables, table_to_prose


def page_text_with_tables_as_prose(page, page_number: int) -> str:
    raw_text = page.get_text("text")
    if not should_detect_tables(raw_text):
        return raw_text

    table_finder = page.find_tables()
    tables = list(table_finder.tables)
    if not tables:
        return raw_text

    blocks = page.get_text("blocks")
    table_bboxes = [table.bbox for table in tables]
    text_parts = [block[4].strip() for block in blocks_outside_tables(blocks, table_bboxes) if block[4].strip()]
    table_parts = [table_to_prose(table.extract(), page_number=page_number) for table in tables]
    return "\n\n".join([*text_parts, *[part for part in table_parts if part]]).strip()


def load_pdf_pages(pdf_path: Path) -> list[PageText]:
    document = fitz.open(pdf_path)
    pages: list[PageText] = []
    try:
        for index, page in enumerate(document, start=1):
            text = page_text_with_tables_as_prose(page, page_number=index)
            pages.append(PageText(source_file=pdf_path.name, page_number=index, text=text))
    finally:
        document.close()
    return pages
