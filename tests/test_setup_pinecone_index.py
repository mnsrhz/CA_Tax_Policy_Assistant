from scripts.setup_pinecone_index import required_pinecone_values
from src.config import AppConfig


def test_required_pinecone_values_only_requires_pinecone_settings():
    config = AppConfig(openai_api_key="", pinecone_api_key="", pinecone_index_name="")

    assert required_pinecone_values(config) == ["PINECONE_API_KEY", "PINECONE_INDEX_NAME"]


def test_required_pinecone_values_allows_missing_openai_key():
    config = AppConfig(openai_api_key="", pinecone_api_key="pinecone-key", pinecone_index_name="tax-index")

    assert required_pinecone_values(config) == []
