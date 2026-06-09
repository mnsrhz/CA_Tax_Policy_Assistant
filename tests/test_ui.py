from src.ui import (
    answer_card_html,
    app_css,
    badge_html,
    format_answer_html,
    retrieval_trace_html,
    retrieval_trace_summary,
    source_chip_html,
    source_label,
)


def test_source_label_formats_document_page():
    label = source_label({"display_title": "IRS Publication 587: Business Use of Your Home", "page_number": 4})

    assert label == "IRS Publication 587: Business Use of Your Home · p.4"


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
        ".ct-answer-card",
        ".ct-answer-header",
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


def test_format_answer_html_renders_basic_markdown_safely():
    html = format_answer_html("**No** — not deductible.\n\n- Federal rule (IRS Pub 529, p.8)\n- California follows it.")

    assert "<strong>No</strong>" in html
    assert "<ul>" in html
    assert "<li>Federal rule (IRS Pub 529, p.8)</li>" in html
    assert "<script>" not in format_answer_html("<script>alert('x')</script>")


def test_answer_card_html_includes_mockup_style_header_and_disclaimer():
    html = answer_card_html(
        answer="**No** — not deductible.",
        source_count=3,
        tax_year="2024",
    )

    assert "ct-answer-card" in html
    assert "ct-answer-header" in html
    assert "Answer based on 3 source documents · Tax year 2024" in html
    assert "<strong>No</strong>" in html
    assert "ct-disclaimer" in html


def test_retrieval_trace_summary_includes_stage_count():
    summary = retrieval_trace_summary([{"stage": "strict"}, {"stage": "fallback"}], source_count=5)

    assert summary == "2 retrieval stages · 5 source chunks"


def test_retrieval_trace_html_formats_pipeline_steps():
    html = retrieval_trace_html(
        trace=[{"stage": "strict"}],
        tax_year="2024",
        jurisdiction="California",
        source_count=5,
    )

    assert "ct-pipeline-trace" in html
    assert "ct-pipeline-title" in html
    assert "Pre-filter 2024" in html
    assert "Filter California" in html
    assert "Vector · 0 hits" in html
    assert "BM25 · 0 hits" in html
    assert "Merged · 0 candidates" in html
    assert "Reranked top 5" in html
    assert "Fallback widened" not in html


def test_retrieval_trace_html_includes_fallback_step_when_present():
    html = retrieval_trace_html(
        trace=[{"stage": "strict"}, {"stage": "fallback"}],
        tax_year="All",
        jurisdiction="Both",
        source_count=3,
    )

    assert "Fallback widened" in html


def test_retrieval_trace_html_includes_retrieval_counts():
    html = retrieval_trace_html(
        trace=[{"stage": "strict", "vector_hits": 12, "bm25_hits": 8, "merged_candidates": 15}],
        tax_year="2024",
        jurisdiction="Both",
        source_count=6,
    )

    assert "Vector · 12 hits" in html
    assert "BM25 · 8 hits" in html
    assert "Merged · 15 candidates" in html
