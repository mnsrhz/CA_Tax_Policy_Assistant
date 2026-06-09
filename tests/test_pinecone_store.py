from src.models import DocumentChunk
from src.pinecone_store import vectors_for_chunks


def test_vectors_for_chunks_builds_pinecone_payloads():
    chunk = DocumentChunk(
        chunk_id="one",
        text="California standard deduction information.",
        source_file="2024-540-booklet.pdf",
        source_title="2024 540 Booklet",
        page_number=10,
        tax_year="2024",
        jurisdiction="california",
        agency="FTB",
        document_type="booklet",
        form_or_pub_number="540",
    )

    vectors = vectors_for_chunks([chunk], [[0.1, 0.2, 0.3]])

    assert vectors == [
        {
            "id": "one",
            "values": [0.1, 0.2, 0.3],
            "metadata": chunk.to_pinecone_metadata(),
        }
    ]
