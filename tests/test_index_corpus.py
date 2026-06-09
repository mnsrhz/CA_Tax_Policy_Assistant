from pathlib import Path

from scripts.index_corpus import discover_pdfs


def test_discover_pdfs_returns_sorted_pdf_paths():
    paths = discover_pdfs(Path("Data Corpus"))

    assert paths
    assert paths == sorted(paths)
    assert all(path.suffix == ".pdf" for path in paths)
