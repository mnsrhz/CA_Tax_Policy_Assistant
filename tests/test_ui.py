from src.ui import badge_html, retrieval_trace_summary, source_chip_html, source_label


def test_source_label_formats_document_page():
    label = source_label({"source_title": "IRS Publication 587", "page_number": 4})

    assert label == "IRS Publication 587 · p.4"


def test_badge_html_formats_class_and_text():
    assert badge_html("FTB", "blue") == '<span class="ct-badge ct-badge-blue">FTB</span>'


def test_source_chip_html_formats_source_label():
    chip = source_chip_html({"source_title": "IRS Publication 587", "page_number": 4})

    assert "ct-source-chip" in chip
    assert "IRS Publication 587 · p.4" in chip


def test_retrieval_trace_summary_includes_stage_count():
    summary = retrieval_trace_summary([{"stage": "strict"}, {"stage": "fallback"}], source_count=5)

    assert summary == "2 retrieval stages · 5 source chunks"
