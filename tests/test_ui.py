from src.ui import app_css, badge_html, retrieval_trace_summary, source_chip_html, source_label


def test_source_label_formats_document_page():
    label = source_label({"source_title": "IRS Publication 587", "page_number": 4})

    assert label == "IRS Publication 587 · p.4"


def test_app_css_returns_style_block_with_required_classes():
    css = app_css()

    assert css.startswith("<style>")
    assert css.endswith("</style>")
    for class_name in [
        ".stApp",
        ".ct-header",
        ".ct-title",
        ".ct-subtitle",
        ".ct-badges",
        ".ct-badge",
        ".ct-badge-blue",
        ".ct-badge-gold",
        ".ct-badge-green",
        ".ct-answer",
        ".ct-disclaimer",
        ".ct-source-row",
        ".ct-source-chip",
    ]:
        assert class_name in css


def test_badge_html_formats_class_and_text():
    assert badge_html("FTB", "blue") == '<span class="ct-badge ct-badge-blue">FTB</span>'


def test_badge_html_escapes_html_sensitive_text():
    badge = badge_html("<script>alert('x')</script>", "gold")

    assert "<script>" not in badge
    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in badge


def test_badge_html_defaults_invalid_color_to_blue():
    badge = badge_html("FTB", 'gold" onclick="alert(1)')

    assert badge == '<span class="ct-badge ct-badge-blue">FTB</span>'


def test_source_chip_html_formats_source_label():
    chip = source_chip_html({"source_title": "IRS Publication 587", "page_number": 4})

    assert "ct-source-chip" in chip
    assert "IRS Publication 587 · p.4" in chip


def test_source_chip_html_escapes_html_sensitive_source_label():
    chip = source_chip_html({"source_title": "<b>IRS Publication 587</b>", "page_number": 4})

    assert "<b>" not in chip
    assert "&lt;b&gt;IRS Publication 587&lt;/b&gt; · p.4" in chip


def test_retrieval_trace_summary_includes_stage_count():
    summary = retrieval_trace_summary([{"stage": "strict"}, {"stage": "fallback"}], source_count=5)

    assert summary == "2 retrieval stages · 5 source chunks"
