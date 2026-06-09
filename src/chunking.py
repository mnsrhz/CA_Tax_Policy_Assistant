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
