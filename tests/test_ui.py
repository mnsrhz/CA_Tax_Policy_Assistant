from src.ui import source_label


def test_source_label_formats_document_page():
    label = source_label({"source_title": "IRS Publication 587", "page_number": 4})

    assert label == "IRS Publication 587 · p.4"
