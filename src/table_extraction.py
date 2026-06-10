from __future__ import annotations

from collections.abc import Sequence
import re
from typing import Any


Block = tuple[float, float, float, float, str, int, int]
BBox = tuple[float, float, float, float]
TABLE_CUES = ("tax table", "tax rate schedule", "tax rate schedules")


def clean_cell(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def should_detect_tables(text: str) -> bool:
    normalized = clean_cell(text).lower()
    if "if you" in normalized and "then use" in normalized:
        return True
    return any(cue in normalized for cue in TABLE_CUES)


def _non_empty_column_indexes(rows: list[list[str]]) -> list[int]:
    max_columns = max((len(row) for row in rows), default=0)
    indexes = []
    for index in range(max_columns):
        if any(index < len(row) and row[index] for row in rows):
            indexes.append(index)
    return indexes


def _compact_rows(rows: Sequence[Sequence[Any]]) -> list[list[str]]:
    cleaned = [[clean_cell(cell) for cell in row] for row in rows]
    indexes = _non_empty_column_indexes(cleaned)
    return [[row[index] if index < len(row) else "" for index in indexes] for row in cleaned]


def _sentence_case(text: str) -> str:
    if not text:
        return text
    return text[0].lower() + text[1:]


def _join_clauses(clauses: list[str]) -> str:
    if len(clauses) == 1:
        return clauses[0]
    return f"{', '.join(clauses[:-1])}, and {clauses[-1]}"


def table_to_prose(rows: Sequence[Sequence[Any]], page_number: int, max_rows: int = 80) -> str:
    compact_rows = [row for row in _compact_rows(rows) if any(row)]
    if len(compact_rows) < 2:
        return ""

    headers = compact_rows[0]
    body_rows = compact_rows[1 : max_rows + 1]
    sentences = [f"Table on page {page_number}:"]

    then_header_index = next((index for index, header in enumerate(headers) if header.upper().startswith("THEN USE")), -1)
    if len(headers) >= 2 and headers[0].upper().startswith("IF YOU") and then_header_index > 0:
        for row in body_rows:
            if len(row) < 2 or not row[0]:
                continue
            result = ""
            if then_header_index < len(row) and row[then_header_index]:
                result = row[then_header_index]
            else:
                result = next((value for value in row[1:] if value), "")
            if not result:
                continue
            condition = _sentence_case(row[0]).rstrip(".")
            result = result.rstrip(".")
            sentences.append(f"If you {condition}, then use {result}.")
        return "\n".join(sentences)

    for row in body_rows:
        if not row or not row[0]:
            continue
        clauses = []
        for header, value in zip(headers[1:], row[1:]):
            if header and value:
                clauses.append(f"{header} is {value}")
        if clauses:
            sentences.append(f"For {headers[0]} {row[0]}, {_join_clauses(clauses)}.")
    return "\n".join(sentences)


def block_center(block: Block) -> tuple[float, float]:
    x0, y0, x1, y1 = block[:4]
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def point_inside_bbox(point: tuple[float, float], bbox: BBox) -> bool:
    x, y = point
    x0, y0, x1, y1 = bbox
    return x0 <= x <= x1 and y0 <= y <= y1


def blocks_outside_tables(blocks: Sequence[Block], table_bboxes: Sequence[BBox]) -> list[Block]:
    outside = []
    for block in blocks:
        center = block_center(block)
        if any(point_inside_bbox(center, bbox) for bbox in table_bboxes):
            continue
        outside.append(block)
    return outside
