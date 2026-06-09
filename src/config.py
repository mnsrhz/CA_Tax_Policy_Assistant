from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


@dataclass(frozen=True)
class AppConfig:
    openai_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_index_name: str = ""
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    DEFAULT_SECRETS_PATH = Path(".streamlit/secrets.toml")

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

    @classmethod
    def from_streamlit_secrets_or_env(cls, secrets) -> "AppConfig":
        try:
            return cls.from_mapping(secrets) if secrets else cls.from_env()
        except Exception:
            return cls.from_env()

    @classmethod
    def from_secrets_file(cls, path: Path | str) -> "AppConfig":
        secrets_path = Path(path)
        with secrets_path.open("rb") as handle:
            values = tomllib.load(handle)
        return cls.from_mapping(values)

    @classmethod
    def from_local_secrets_or_env(cls, path: Path | str | None = None) -> "AppConfig":
        secrets_path = Path(path) if path is not None else cls.DEFAULT_SECRETS_PATH
        if secrets_path.exists():
            return cls.from_secrets_file(secrets_path)
        return cls.from_env()

    def missing_required_values(self) -> list[str]:
        missing: list[str] = []
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.pinecone_api_key:
            missing.append("PINECONE_API_KEY")
        if not self.pinecone_index_name:
            missing.append("PINECONE_INDEX_NAME")
        return missing
