from src.config import AppConfig


def test_config_reads_environment_values(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("PINECONE_API_KEY", "pinecone-key")
    monkeypatch.setenv("PINECONE_INDEX_NAME", "tax-index")

    config = AppConfig.from_env()

    assert config.openai_api_key == "openai-key"
    assert config.pinecone_api_key == "pinecone-key"
    assert config.pinecone_index_name == "tax-index"


def test_missing_required_values_are_reported(monkeypatch):
    for key in ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]:
        monkeypatch.delenv(key, raising=False)

    config = AppConfig.from_env()

    assert config.missing_required_values() == [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_INDEX_NAME",
    ]
