from src.config import AppConfig


def test_config_reads_environment_values(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("PINECONE_API_KEY", "pinecone-key")
    monkeypatch.setenv("PINECONE_INDEX_NAME", "tax-index")

    config = AppConfig.from_env()

    assert config.openai_api_key == "openai-key"
    assert config.pinecone_api_key == "pinecone-key"
    assert config.pinecone_index_name == "tax-index"
    assert config.pinecone_cloud == "aws"
    assert config.pinecone_region == "us-east-1"


def test_missing_required_values_are_reported(monkeypatch):
    for key in ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]:
        monkeypatch.delenv(key, raising=False)

    config = AppConfig.from_env()

    assert config.missing_required_values() == [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_INDEX_NAME",
    ]


def test_config_reads_mapping_values_for_streamlit_secrets():
    config = AppConfig.from_mapping(
        {
            "OPENAI_API_KEY": "openai-secret",
            "PINECONE_API_KEY": "pinecone-secret",
            "PINECONE_INDEX_NAME": "streamlit-index",
            "PINECONE_CLOUD": "gcp",
            "PINECONE_REGION": "us-central1",
            "EMBEDDING_MODEL_NAME": "custom-embedding",
            "RERANKER_MODEL_NAME": "custom-reranker",
        }
    )

    assert config.openai_api_key == "openai-secret"
    assert config.pinecone_api_key == "pinecone-secret"
    assert config.pinecone_index_name == "streamlit-index"
    assert config.pinecone_cloud == "gcp"
    assert config.pinecone_region == "us-central1"
    assert config.embedding_model_name == "custom-embedding"
    assert config.reranker_model_name == "custom-reranker"


def test_config_falls_back_to_env_when_secrets_raise(monkeypatch):
    class MissingSecrets:
        def __bool__(self):
            raise FileNotFoundError("No secrets found")

    monkeypatch.setenv("OPENAI_API_KEY", "openai-env")
    monkeypatch.setenv("PINECONE_API_KEY", "pinecone-env")
    monkeypatch.setenv("PINECONE_INDEX_NAME", "env-index")

    config = AppConfig.from_streamlit_secrets_or_env(MissingSecrets())

    assert config.openai_api_key == "openai-env"
    assert config.pinecone_api_key == "pinecone-env"
    assert config.pinecone_index_name == "env-index"
