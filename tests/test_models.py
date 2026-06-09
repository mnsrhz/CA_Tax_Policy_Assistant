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
