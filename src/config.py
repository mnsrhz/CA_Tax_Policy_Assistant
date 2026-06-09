from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_index_name: str = ""
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls.from_mapping(os.environ)

    @classmethod
    def from_mapping(cls, values: Mapping[str, str]) -> "AppConfig":
        return cls(
            openai_api_key=values.get("OPENAI_API_KEY", ""),
            pinecone_api_key=values.get("PINECONE_API_KEY", ""),
            pinecone_index_name=values.get("PINECONE_INDEX_NAME", ""),
            pinecone_cloud=values.get("PINECONE_CLOUD", cls.pinecone_cloud),
            pinecone_region=values.get("PINECONE_REGION", cls.pinecone_region),
            embedding_model_name=values.get("EMBEDDING_MODEL_NAME", cls.embedding_model_name),
            reranker_model_name=values.get("RERANKER_MODEL_NAME", cls.reranker_model_name),
        )

    def missing_required_values(self) -> list[str]:
        missing: list[str] = []
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.pinecone_api_key:
            missing.append("PINECONE_API_KEY")
        if not self.pinecone_index_name:
            missing.append("PINECONE_INDEX_NAME")
        return missing
