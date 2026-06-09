from pathlib import Path
import subprocess
import sys

from scripts.setup_pinecone_index import required_pinecone_values
from src.config import AppConfig


def test_required_pinecone_values_only_requires_pinecone_settings():
    config = AppConfig(openai_api_key="", pinecone_api_key="", pinecone_index_name="")

    assert required_pinecone_values(config) == ["PINECONE_API_KEY", "PINECONE_INDEX_NAME"]


def test_required_pinecone_values_allows_missing_openai_key():
    config = AppConfig(openai_api_key="", pinecone_api_key="pinecone-key", pinecone_index_name="tax-index")

    assert required_pinecone_values(config) == []


def test_setup_pinecone_index_script_runs_directly_to_configuration_check(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(repo_root / "scripts/setup_pinecone_index.py")],
        cwd=tmp_path,
        env={},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Missing required configuration values" in result.stderr
    assert "No module named 'src'" not in result.stderr
