from pathlib import Path
import subprocess
import sys

from scripts.index_corpus import discover_pdfs, required_indexing_values
from src.config import AppConfig


def test_discover_pdfs_returns_sorted_pdf_paths():
    paths = discover_pdfs(Path("Data Corpus"))

    assert paths
    assert paths == sorted(paths)
    assert all(path.suffix == ".pdf" for path in paths)


def test_required_indexing_values_allows_missing_openai_key():
    config = AppConfig(openai_api_key="", pinecone_api_key="pinecone-key", pinecone_index_name="tax-index")

    assert required_indexing_values(config) == []


def test_index_corpus_script_runs_directly_to_configuration_check():
    result = subprocess.run(
        [sys.executable, "scripts/index_corpus.py"],
        cwd=Path(__file__).resolve().parents[1],
        env={},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Missing required configuration values" in result.stderr
    assert "No module named 'src'" not in result.stderr
