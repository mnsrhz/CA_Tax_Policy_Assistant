from __future__ import annotations

from collections.abc import Iterable

from pinecone import Pinecone

from src.models import DocumentChunk


BGE_SMALL_DIMENSION = 384


def ensure_pinecone_index(
    client,
    index_name: str,
    cloud: str = "aws",
    region: str = "us-east-1",
    dimension: int = BGE_SMALL_DIMENSION,
    metric: str = "cosine",
) -> None:
    if client.has_index(index_name):
        return
    client.create_index(
        name=index_name,
        dimension=dimension,
        metric=metric,
        spec={"serverless": {"cloud": cloud, "region": region}},
    )


def vectors_for_chunks(chunks: list[DocumentChunk], embeddings: list[list[float]]) -> list[dict[str, object]]:
    return [
        {
            "id": chunk.chunk_id,
            "values": embedding,
            "metadata": chunk.to_pinecone_metadata(),
        }
        for chunk, embedding in zip(chunks, embeddings)
    ]


def batched(items: list[dict[str, object]], batch_size: int) -> Iterable[list[dict[str, object]]]:
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


class PineconeStore:
    def __init__(self, api_key: str, index_name: str) -> None:
        self.client = Pinecone(api_key=api_key)
        self.index = self.client.Index(index_name)

    def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]], batch_size: int = 100) -> None:
        vectors = vectors_for_chunks(chunks, embeddings)
        for batch in batched(vectors, batch_size):
            self.index.upsert(vectors=batch)

    def query(self, vector: list[float], top_k: int, metadata_filter: dict[str, object] | None = None):
        return self.index.query(vector=vector, top_k=top_k, filter=metadata_filter or {}, include_metadata=True)
