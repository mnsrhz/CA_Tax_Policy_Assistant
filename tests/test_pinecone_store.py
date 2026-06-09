from src.models import DocumentChunk
from src.pinecone_store import BGE_SMALL_DIMENSION, ensure_pinecone_index, vectors_for_chunks


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


class FakePineconeClient:
    def __init__(self, has_index: bool):
        self._has_index = has_index
        self.created_indexes = []

    def has_index(self, name: str) -> bool:
        return self._has_index

    def create_index(self, **kwargs):
        self.created_indexes.append(kwargs)


def test_ensure_pinecone_index_creates_missing_serverless_index():
    client = FakePineconeClient(has_index=False)

    ensure_pinecone_index(client, index_name="tax-index", cloud="aws", region="us-east-1")

    assert client.created_indexes == [
        {
            "name": "tax-index",
            "dimension": BGE_SMALL_DIMENSION,
            "metric": "cosine",
            "spec": {"serverless": {"cloud": "aws", "region": "us-east-1"}},
        }
    ]


def test_ensure_pinecone_index_skips_existing_index():
    client = FakePineconeClient(has_index=True)

    ensure_pinecone_index(client, index_name="tax-index", cloud="aws", region="us-east-1")

    assert client.created_indexes == []
