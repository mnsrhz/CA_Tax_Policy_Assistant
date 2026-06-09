from __future__ import annotations

from pinecone import Pinecone

from src.config import AppConfig
from src.pinecone_store import BGE_SMALL_DIMENSION, ensure_pinecone_index


def required_pinecone_values(config: AppConfig) -> list[str]:
    missing: list[str] = []
    if not config.pinecone_api_key:
        missing.append("PINECONE_API_KEY")
    if not config.pinecone_index_name:
        missing.append("PINECONE_INDEX_NAME")
    return missing


def setup_pinecone_index() -> None:
    config = AppConfig.from_env()
    missing = required_pinecone_values(config)
    if missing:
        raise RuntimeError(f"Missing required configuration values: {', '.join(missing)}")

    client = Pinecone(api_key=config.pinecone_api_key)
    ensure_pinecone_index(
        client,
        index_name=config.pinecone_index_name,
        cloud=config.pinecone_cloud,
        region=config.pinecone_region,
    )
    print(
        "Pinecone index ready: "
        f"{config.pinecone_index_name} "
        f"({BGE_SMALL_DIMENSION} dimensions, cosine, {config.pinecone_cloud}/{config.pinecone_region})"
    )


if __name__ == "__main__":
    setup_pinecone_index()
