from src.chunking import chunk_pages
from src.models import PageText


def test_chunk_pages_preserves_metadata_and_page_number():
    pages = [
        PageText(
            source_file="p587.pdf",
            page_number=4,
            text="Business Use of Your Home\n\nExclusive use rule applies.\n\nRegular use rule applies.",
        )
    ]
    metadata = {
        "source_title": "IRS Publication 587",
        "tax_year": "2024",
        "agency": "IRS",
        "jurisdiction": "federal",
        "document_type": "publication",
        "form_or_pub_number": "587",
    }

    chunks = chunk_pages(pages, metadata, max_chars=120)

    assert len(chunks) >= 1
    assert chunks[0].source_file == "p587.pdf"
    assert chunks[0].page_number == 4
    assert chunks[0].section_heading == "Business Use of Your Home"
    assert "Exclusive use" in chunks[0].text


def test_chunk_pages_splits_large_text():
    text = "\n\n".join([f"Paragraph {index} discusses estimated tax payments." for index in range(20)])
    pages = [PageText(source_file="p505.pdf", page_number=2, text=text)]
    metadata = {
        "source_title": "IRS Publication 505",
        "tax_year": "2024",
        "agency": "IRS",
        "jurisdiction": "federal",
        "document_type": "publication",
        "form_or_pub_number": "505",
    }

    chunks = chunk_pages(pages, metadata, max_chars=250)

    assert len(chunks) > 1
    assert all(len(chunk.text) <= 320 for chunk in chunks)
