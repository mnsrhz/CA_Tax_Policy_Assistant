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
