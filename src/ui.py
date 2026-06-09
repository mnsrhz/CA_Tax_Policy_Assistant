from __future__ import annotations


def source_label(metadata: dict[str, object]) -> str:
    title = metadata.get("source_title", metadata.get("source_file", "Unknown source"))
    page = metadata.get("page_number", "?")
    return f"{title} · p.{page}"
