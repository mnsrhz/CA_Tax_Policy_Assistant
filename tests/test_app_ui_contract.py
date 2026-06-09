from pathlib import Path


def test_app_uses_spinner_for_generation_workflow():
    app_source = Path("app.py").read_text(encoding="utf-8")

    assert "st.spinner" in app_source
    assert "Retrieving sources, reranking, and drafting answer" in app_source


def test_app_does_not_render_raw_trace_expander():
    app_source = Path("app.py").read_text(encoding="utf-8")

    assert "Raw trace" not in app_source
    assert "st.json(trace)" not in app_source
